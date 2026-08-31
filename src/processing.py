from __future__ import annotations

import hashlib
import re
from difflib import SequenceMatcher

from .models import Event, SourceItem


def normalized_title(title: str) -> str:
    return " ".join(re.findall(r"[a-z0-9\u4e00-\u9fff]+", title.lower()))


def deduplicate(items: list[SourceItem], threshold: float = 0.82) -> list[Event]:
    events: list[Event] = []
    seen_urls: set[str] = set()
    for item in items:
        canonical_url = item.url.split("#", 1)[0].rstrip("/")
        if canonical_url in seen_urls:
            continue
        seen_urls.add(canonical_url)
        normalized = normalized_title(item.title)
        match = next((event for event in events if SequenceMatcher(None, normalized, normalized_title(event.title)).ratio() >= threshold), None)
        source = {"name": item.source, "url": item.url, "type": item.source_type}
        if match:
            match.sources.append(source)
            if len(item.summary) > len(match.summary):
                match.summary = item.summary
            continue
        event_id = hashlib.sha256((normalized + canonical_url).encode()).hexdigest()[:16]
        events.append(Event(event_id, item.title.strip(), item.summary.strip(), item.published_at, [source]))
    return events


def pre_score(event: Event) -> float:
    text = f"{event.title} {event.summary}".lower()
    signals = {"release": 0.7, "model": 0.5, "agent": 0.6, "reasoning": 0.6, "open source": 0.5, "benchmark": 0.4, "mcp": 0.7, "research": 0.3}
    score = 4.2 + min(len(event.sources) - 1, 2) * 0.4
    score += sum(weight for word, weight in signals.items() if word in text)
    if any(source["type"] == "official" for source in event.sources):
        score += 0.7
    event.pre_score = round(min(score, 9.5), 1)
    return event.pre_score

