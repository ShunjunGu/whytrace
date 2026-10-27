from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def load_table(name: str) -> list[dict[str, Any]]:
    path = DATA_DIR / f"{name}.json"
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def all_tables() -> dict[str, list[dict[str, Any]]]:
    return {
        "collisions": load_table("collisions"),
        "zones": load_table("zones"),
        "companies": load_table("companies"),
    }
