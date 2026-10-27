"""Answer synthesis: mock by default; optional Meterless Runtime / OpenAI-compatible."""

from __future__ import annotations

import os
from typing import Any

import httpx

from whytrace.meterless_memory import MemoryRecord


def synthesize(question: str, findings: list[MemoryRecord], prior: list[MemoryRecord]) -> dict[str, Any]:
    provider = os.getenv("SYNTHESIS_PROVIDER", "mock").strip().lower()
    if provider == "mock":
        return _mock_synthesize(question, findings, prior)
    if provider == "meterless":
        return _openai_compat_synthesize(question, findings, prior, runtime=True)
    if provider in {"openai", "nemotron"}:
        return _openai_compat_synthesize(question, findings, prior, runtime=False)
    return _mock_synthesize(question, findings, prior)


def _format_evidence(findings: list[MemoryRecord]) -> str:
    lines = []
    for f in findings:
        lines.append(f"- [{f.id}] (conf={f.confidence:.2f}) {f.claim}")
    return "\n".join(lines) if lines else "- (no findings)"


def _mock_synthesize(
    question: str, findings: list[MemoryRecord], prior: list[MemoryRecord]
) -> dict[str, Any]:
    cites = ", ".join(f.id for f in findings) or "none"
    bullets = "\n".join(f"  • {f.claim} [{f.id}]" for f in findings)
    prior_note = ""
    if prior:
        prior_note = "\nPrior memory considered: " + "; ".join(
            f"{p.id}: {p.claim}" for p in prior[:3]
        )
    answer = (
        f"Question: {question}\n\n"
        f"Evidence-backed summary (mock synthesizer):\n{bullets}\n\n"
        f"Recommendation: Prioritize the top crash-density zones for safety review "
        f"and engage companies operating in those zones for operational context. "
        f"Citations: {cites}.{prior_note}"
    )
    return {"provider": "mock", "answer": answer, "citation_ids": [f.id for f in findings]}


def _openai_compat_synthesize(
    question: str,
    findings: list[MemoryRecord],
    prior: list[MemoryRecord],
    *,
    runtime: bool,
) -> dict[str, Any]:
    if runtime:
        base = os.getenv("METERLESS_RUNTIME_URL", "http://127.0.0.1:8088/v1").rstrip("/")
        token = os.getenv("METERLESS_RUNTIME_TOKEN", "")
        model = "meterless/auto"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "meterless-app": os.getenv("METERLESS_APP_ID", "whytrace"),
            "meterless-scope": "user",
        }
    else:
        base = os.getenv("OPENAI_BASE_URL") or os.getenv("NEMOTRON_BASE_URL") or "https://api.openai.com/v1"
        base = base.rstrip("/")
        token = os.getenv("OPENAI_API_KEY") or os.getenv("NEMOTRON_API_KEY") or ""
        model = os.getenv("SYNTHESIS_MODEL", "gpt-4o-mini")
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    if not token:
        out = _mock_synthesize(question, findings, prior)
        out["provider"] = f"{'meterless' if runtime else 'openai'}-fallback-mock"
        out["warning"] = "No token set; used mock synthesizer."
        return out

    system = (
        "You are WhyTrace. Answer only from the provided evidence. "
        "Cite evidence ids like [ev-xxxxxxxx]. If evidence is weak, say so."
    )
    user = (
        f"Question: {question}\n\nEvidence:\n{_format_evidence(findings)}\n\n"
        f"Prior memories:\n{_format_evidence(prior)}"
    )
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.2,
    }
    with httpx.Client(timeout=180.0) as client:
        resp = client.post(f"{base}/chat/completions", headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
    content = data["choices"][0]["message"]["content"]
    if isinstance(content, list):
        content = "".join(
            part.get("text", "") if isinstance(part, dict) else str(part) for part in content
        )
    return {
        "provider": "meterless-runtime" if runtime else "openai-compat",
        "answer": content,
        "citation_ids": [f.id for f in findings],
    }
