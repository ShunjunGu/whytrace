"""Meterless H-MEM-shaped memory + append-only trust ledger.

Default: Python mock compatible with WhyTrace demo (no Node required).

Real engine (do this before final submit if judges require live Meterless):

  npx degit meterless/meterless/templates/agentathon-starter ../meterless-hmem
  cd ../meterless-hmem && npm install && npm run setup
  # setup vendors engines/hmem/reference → vendor/hmem

  Real API surface (from notebook.ts):
    hmem.mine("chat_message", text)
    hmem.add({ content, type, source })
    hmem.query(text, { threshold: 0.1 })  # → memories + context + trace
    hmem.ledger.history(memoryId)
    hmem.sleep.preview() / execute()

  Or engine-only:
    npx degit meterless/meterless/engines/hmem ../my-hmem
    cd ../my-hmem/reference && npm install && npm test

Optional Runtime LLM (synthesis only):
  POST {METERLESS_RUNTIME_URL}/chat/completions
  Authorization: Bearer <token from runtime stateDir/proxy-token>
  meterless-app: whytrace
  Docs: https://meterless.ai/engines.html
"""

from __future__ import annotations

import json
import os
import re
import time
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class MemoryRecord:
    id: str
    claim: str
    provenance: dict[str, Any]
    confidence: float
    created_at: float
    tags: list[str] = field(default_factory=list)


@dataclass
class LedgerEvent:
    ts: float
    action: str  # write | read | feedback
    memory_id: str
    detail: dict[str, Any]


class MeterlessMemory:
    """H-MEM-shaped store. Swap for real reference via METERLESS_BRIDGE=node later."""

    def __init__(self, store_dir: str | None = None) -> None:
        root = store_dir or os.getenv("METERLESS_STORE_DIR", ".whytrace/memory")
        self.dir = Path(root)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.mem_path = self.dir / "memories.json"
        self.ledger_path = self.dir / "ledger.jsonl"
        self.bridge = (os.getenv("METERLESS_BRIDGE") or "mock").strip().lower()
        self._memories: dict[str, MemoryRecord] = {}
        self._load()

    def status(self) -> dict[str, Any]:
        return {
            "mode": "python-hmem-mock" if self.bridge == "mock" else f"bridge:{self.bridge}",
            "store": str(self.dir.resolve()),
            "memory_count": len(self._memories),
            "live_starter": (
                "npx degit meterless/meterless/templates/agentathon-starter meterless-hmem "
                "&& cd meterless-hmem && npm install && npm run setup"
            ),
            "engine_only": "npx degit meterless/meterless/engines/hmem my-hmem",
            "note": (
                "Mock is OK for rehearsal. For submit, vendor real H-MEM and show "
                "mine/query/ledger in the demo (see INTEGRATION_NOTES.md)."
            ),
        }

    def remember(
        self,
        claim: str,
        provenance: dict[str, Any] | None = None,
        confidence: float = 0.7,
        tags: list[str] | None = None,
    ) -> MemoryRecord:
        # Maps to hmem.add / mine fallback in the real starter.
        mid = f"ev-{uuid.uuid4().hex[:8]}"
        rec = MemoryRecord(
            id=mid,
            claim=claim.strip(),
            provenance=provenance or {},
            confidence=float(confidence),
            created_at=time.time(),
            tags=tags or [],
        )
        if "source" not in rec.provenance:
            rec.provenance["source"] = "whytrace"
        self._memories[mid] = rec
        self._persist()
        self._ledger("write", mid, {"claim": rec.claim, "provenance": rec.provenance})
        return rec

    def mine_finding(
        self,
        claim: str,
        *,
        sql: str,
        table: str,
        rows: list[dict[str, Any]],
        confidence: float = 0.8,
        tags: list[str] | None = None,
    ) -> MemoryRecord:
        sample = rows[:3]
        return self.remember(
            claim,
            provenance={
                "sql": sql,
                "table": table,
                "row_count": len(rows),
                "sample_rows": sample,
                "sponsor": "zetaris→meterless",
                "origin": "zetaris_query",
            },
            confidence=confidence,
            tags=tags or ["finding"],
        )

    def retrieve(self, query: str, limit: int = 5) -> list[MemoryRecord]:
        # Maps to hmem.query(query, { threshold }) in the real starter.
        tokens = set(re.findall(r"[a-z0-9]+", query.lower()))
        scored: list[tuple[float, MemoryRecord]] = []
        for rec in self._memories.values():
            hay = set(
                re.findall(r"[a-z0-9]+", (rec.claim + " " + " ".join(rec.tags)).lower())
            )
            overlap = len(tokens & hay)
            score = overlap + rec.confidence
            scored.append((score, rec))
        scored.sort(key=lambda x: x[0], reverse=True)
        out = [r for s, r in scored[:limit] if s > 0] or [r for _, r in scored[:limit]]
        for rec in out:
            self._ledger("read", rec.id, {"query": query})
        return out

    def audit(self, limit: int = 50) -> list[dict[str, Any]]:
        # Maps to hmem.ledger.history(id) / full ledger export.
        if not self.ledger_path.exists():
            return []
        lines = self.ledger_path.read_text(encoding="utf-8").strip().splitlines()
        events = [json.loads(line) for line in lines[-limit:]]
        return list(reversed(events))

    def feedback(self, memory_id: str, label: str) -> None:
        if memory_id not in self._memories:
            raise KeyError(
                f"Unknown memory {memory_id}. "
                "List ids via ask findings or audit events."
            )
        rec = self._memories[memory_id]
        if label == "helpful":
            rec.confidence = min(1.0, rec.confidence + 0.05)
        elif label == "not_helpful":
            rec.confidence = max(0.0, rec.confidence - 0.03)
        elif label == "wrong":
            rec.confidence = max(0.0, rec.confidence - 0.20)
            if "review" not in rec.tags:
                rec.tags.append("review")
        self._persist()
        self._ledger("feedback", memory_id, {"label": label, "confidence": rec.confidence})

    def _load(self) -> None:
        if not self.mem_path.exists():
            return
        raw = json.loads(self.mem_path.read_text(encoding="utf-8"))
        for item in raw:
            rec = MemoryRecord(**item)
            self._memories[rec.id] = rec

    def _persist(self) -> None:
        payload = [asdict(m) for m in self._memories.values()]
        self.mem_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _ledger(self, action: str, memory_id: str, detail: dict[str, Any]) -> None:
        event = LedgerEvent(ts=time.time(), action=action, memory_id=memory_id, detail=detail)
        with self.ledger_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(event)) + "\n")
