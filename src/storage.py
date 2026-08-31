from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_history(path: Path, entry: dict[str, Any], unique_key: str = "date") -> None:
    history = []
    if path.exists():
        history = json.loads(path.read_text(encoding="utf-8"))
    history = [item for item in history if item.get(unique_key) != entry.get(unique_key)]
    history.append(entry)
    write_json(path, history)

