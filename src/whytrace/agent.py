"""WhyTrace orchestration: Zetaris queries → Meterless H-MEM → cited answer."""

from __future__ import annotations

from typing import Any

from whytrace.meterless_memory import MeterlessMemory
from whytrace.synthesizer import synthesize
from whytrace.zetaris_client import ZetarisClient, ZetarisError


class WhyTraceAgent:
    def __init__(self) -> None:
        self.zetaris = ZetarisClient()
        self.memory = MeterlessMemory()

    def status(self) -> dict[str, Any]:
        return {
            "project": "WhyTrace",
            "track": "02-the-agent-that-can-explain-why",
            "zetaris": self.zetaris.status(),
            "meterless": self.memory.status(),
        }

    def ping(self) -> dict[str, Any]:
        try:
            z = self.zetaris.ping()
        except ZetarisError as exc:
            z = {"ok": False, "error": str(exc)}
        return {"zetaris": z, "meterless": self.memory.status()}

    def ask(self, question: str) -> dict[str, Any]:
        prior = self.memory.retrieve(question, limit=3)

        try:
            density = self.zetaris.crash_density_by_zone()
        except ZetarisError as exc:
            return self._failed_ask(question, prior, exc)

        top = density.rows[:3]
        if not top:
            return {
                "mode": {
                    "zetaris": density.source,
                    "meterless": self.memory.status()["mode"],
                    "synthesis": "none",
                },
                "question": question,
                "findings": [],
                "prior_memories": [{"id": p.id, "claim": p.claim} for p in prior],
                "answer": (
                    "No crash-density rows returned. "
                    "If live: confirm Lightning tables exist "
                    "(SHOW LIGHTNING DATABASES / cookbook onboard). "
                    "If mock: check data/collisions.json."
                ),
                "citation_ids": [],
                "warning": "empty_density_result",
            }

        zone_ids = [str(r.get("zone_id") or r.get("ZONE_ID") or "") for r in top]
        zone_ids = [z for z in zone_ids if z]

        try:
            zones = self.zetaris.zones_lookup(zone_ids)
            companies = self.zetaris.companies_in_zones(zone_ids)
        except ZetarisError as exc:
            return self._failed_ask(question, prior, exc, partial_density=density)

        zone_name = {
            str(z.get("zone_id") or z.get("ZONE_ID")): z.get("name") or z.get("NAME") or str(z.get("zone_id"))
            for z in zones.rows
        }

        findings = []
        for row in top:
            zid = str(row.get("zone_id") or row.get("ZONE_ID") or "")
            name = zone_name.get(zid, zid)
            crashes = row.get("crashes", row.get("CRASHES", "?"))
            injured = row.get("injured", row.get("INJURED", 0))
            fatal = row.get("fatal", row.get("FATAL", 0))
            claim = (
                f"Zone {zid} ({name}) has {crashes} crashes "
                f"(injured={injured}, fatal={fatal})."
            )
            findings.append(
                self.memory.mine_finding(
                    claim,
                    sql=density.sql,
                    table="collisions/crash_density",
                    rows=[row],
                    confidence=0.9,
                    tags=["crash_density", zid],
                )
            )

        for zid in zone_ids:
            cos = [
                c
                for c in companies.rows
                if str(c.get("zone_id") or c.get("ZONE_ID") or "") == zid
            ]
            if not cos:
                continue
            names = ", ".join(str(c.get("name") or c.get("NAME")) for c in cos)
            claim = f"Companies operating in zone {zid} ({zone_name.get(zid, zid)}): {names}."
            findings.append(
                self.memory.mine_finding(
                    claim,
                    sql=companies.sql,
                    table="companies",
                    rows=cos,
                    confidence=0.85,
                    tags=["company_link", zid],
                )
            )

        synthesis = synthesize(question, findings, prior)
        return {
            "mode": {
                "zetaris": density.source,
                "meterless": self.memory.status()["mode"],
                "synthesis": synthesis.get("provider"),
            },
            "question": question,
            "queries": {
                "density_sql": density.sql,
                "zones_sql": zones.sql,
                "companies_sql": companies.sql,
            },
            "findings": [
                {
                    "id": f.id,
                    "claim": f.claim,
                    "confidence": f.confidence,
                    "provenance": f.provenance,
                }
                for f in findings
            ],
            "prior_memories": [{"id": p.id, "claim": p.claim} for p in prior],
            "answer": synthesis["answer"],
            "citation_ids": synthesis.get("citation_ids", []),
            "warning": synthesis.get("warning"),
        }

    def _failed_ask(
        self,
        question: str,
        prior: list[Any],
        exc: ZetarisError,
        partial_density: Any = None,
    ) -> dict[str, Any]:
        return {
            "mode": {
                "zetaris": "error",
                "meterless": self.memory.status()["mode"],
                "synthesis": "none",
            },
            "question": question,
            "findings": [],
            "prior_memories": [{"id": p.id, "claim": p.claim} for p in prior],
            "answer": (
                "WhyTrace could not finish the investigation because Zetaris failed.\n\n"
                f"{exc}\n\n"
                "Keep USE_MOCK=1 until ping succeeds: python -m whytrace ping"
            ),
            "citation_ids": [],
            "warning": "zetaris_error",
            "error": str(exc),
            "partial": {"density_sql": getattr(partial_density, "sql", None)},
        }

    def remember(self, text: str) -> dict[str, Any]:
        rec = self.memory.remember(
            text, provenance={"source": "user"}, confidence=0.95, tags=["user"]
        )
        return {"id": rec.id, "claim": rec.claim}

    def audit(self, limit: int = 30) -> list[dict[str, Any]]:
        return self.memory.audit(limit=limit)
