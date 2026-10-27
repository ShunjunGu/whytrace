"""Curated demo questions for recording and local rehearsal."""

from __future__ import annotations

DEMO_QUESTIONS: list[dict[str, str]] = [
    {
        "id": "1",
        "title": "Primary demo (use this in the video)",
        "question": (
            "Which zones have the highest crash density and which companies operate there?"
        ),
        "why": "Forces multi-source join (collisions → zones → companies) and citation ledger.",
    },
    {
        "id": "2",
        "title": "Safety follow-up",
        "question": "Which borough shows the most injured people in the top crash zones?",
        "why": "Shows follow-up ask reusing H-MEM prior findings.",
    },
    {
        "id": "3",
        "title": "Operator outreach",
        "question": "Which taxi fleets should we contact first about Midtown Center crash risk?",
        "why": "Recommendation framing with evidence ids for Track 02 narrative.",
    },
    {
        "id": "4",
        "title": "Sparse-data honesty",
        "question": "Is Astoria a priority for safety review based on current crash counts?",
        "why": "Low-count zone — answer should stay calibrated, not overclaim.",
    },
]


def get_demo(demo_id: str) -> dict[str, str]:
    for item in DEMO_QUESTIONS:
        if item["id"] == str(demo_id):
            return item
    known = ", ".join(d["id"] for d in DEMO_QUESTIONS)
    raise KeyError(f"Unknown demo id {demo_id!r}. Known: {known}")


def format_catalog() -> str:
    lines = ["WhyTrace demo questions (mock-safe):", ""]
    for d in DEMO_QUESTIONS:
        lines.append(f"[{d['id']}] {d['title']}")
        lines.append(f"    Q: {d['question']}")
        lines.append(f"    Why: {d['why']}")
        lines.append("")
    lines.append("Run: python -m whytrace ask --demo 1")
    return "\n".join(lines)
