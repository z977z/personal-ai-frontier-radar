from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class SourceItem:
    title: str
    url: str
    source: str
    published_at: str
    retrieved_at: str
    summary: str
    content: str = ""
    source_type: str = "official"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Event:
    id: str
    title: str
    summary: str
    published_at: str
    sources: list[dict[str, str]]
    pre_score: float = 0.0
    ai_score: float = 0.0
    facts: str = ""
    analysis: str = ""
    technical_value: str = ""
    impact: str = ""
    keywords: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()

