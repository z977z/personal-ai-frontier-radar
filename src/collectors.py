from __future__ import annotations

import html
import logging
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

from .models import SourceItem, utc_now

LOGGER = logging.getLogger(__name__)

FEEDS = [
    ("Google DeepMind", "https://deepmind.google/blog/rss.xml", "official"),
    ("Hugging Face", "https://huggingface.co/blog/feed.xml", "official"),
    ("arXiv AI", "https://export.arxiv.org/api/query?search_query=cat:cs.AI&start=0&max_results=8&sortBy=submittedDate&sortOrder=descending", "research"),
]


def clean_html(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", value or ""))).strip()


def _text(node: ET.Element, names: list[str]) -> str:
    for name in names:
        child = node.find(name)
        if child is not None and child.text:
            return child.text.strip()
    return ""


def parse_feed(payload: bytes, source: str, source_type: str) -> list[SourceItem]:
    root = ET.fromstring(payload)
    entries = root.findall(".//item") or root.findall("{http://www.w3.org/2005/Atom}entry")
    result: list[SourceItem] = []
    for entry in entries[:12]:
        title = _text(entry, ["title", "{http://www.w3.org/2005/Atom}title"])
        url = _text(entry, ["link"])
        if not url:
            link = entry.find("{http://www.w3.org/2005/Atom}link")
            url = link.attrib.get("href", "") if link is not None else ""
        published = _text(entry, ["pubDate", "published", "updated", "{http://www.w3.org/2005/Atom}published", "{http://www.w3.org/2005/Atom}updated"])
        summary = clean_html(_text(entry, ["description", "summary", "{http://www.w3.org/2005/Atom}summary"]))
        if title and url:
            result.append(SourceItem(title, url, source, published, utc_now(), summary[:1800], summary[:1800], source_type))
    return result


def fallback_items() -> list[SourceItem]:
    now = datetime.now(timezone.utc).isoformat()
    return [
        SourceItem("MCP specification and ecosystem documentation", "https://modelcontextprotocol.io/", "Model Context Protocol", now, now, "Official documentation for an open protocol that connects AI applications to tools and data.", source_type="official"),
        SourceItem("Hugging Face open-source AI platform", "https://huggingface.co/", "Hugging Face", now, now, "Official platform entry used as a degraded-mode sample for open-source AI discovery.", source_type="official"),
        SourceItem("Recent artificial intelligence research", "https://arxiv.org/list/cs.AI/recent", "arXiv", now, now, "Official recent-submissions index used when live feeds are unavailable.", source_type="research"),
    ]


def collect(timeout: int) -> tuple[list[SourceItem], list[str]]:
    items: list[SourceItem] = []
    failures: list[str] = []
    headers = {"User-Agent": "PersonalAIFrontierRadar/0.1 (+https://github.com/)"}
    for source, url, source_type in FEEDS:
        try:
            LOGGER.info("Collecting %s...", source)
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                found = parse_feed(response.read(), source, source_type)
            LOGGER.info("Collected %s items from %s", len(found), source)
            items.extend(found)
        except Exception as exc:  # source isolation is intentional
            failures.append(f"{source}: {type(exc).__name__}")
            LOGGER.warning("Source unavailable: %s (%s)", source, type(exc).__name__)
    if not items:
        LOGGER.warning("All live sources unavailable; using grounded fallback samples")
        items = fallback_items()
    return items, failures

