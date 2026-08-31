from __future__ import annotations

import argparse
import logging
from datetime import datetime
from pathlib import Path

from src.collectors import collect
from src.config import Settings
from src.llm import DeepSeekProvider, MockProvider
from src.notifications import send_daily_email
from src.processing import deduplicate, pre_score
from src.reporting import render_build, render_daily, safe_slug
from src.storage import append_history, write_json

ROOT = Path(__file__).resolve().parent


def provider_for(settings: Settings):
    if settings.llm_provider == "deepseek" and settings.deepseek_api_key:
        return DeepSeekProvider(settings.deepseek_api_key, settings.deepseek_base_url, settings.fast_model, settings.smart_model, settings.timeout)
    if settings.allow_mock:
        return MockProvider()
    raise RuntimeError("DEEPSEEK_API_KEY is missing and mock fallback is disabled")


def run(settings: Settings) -> tuple[Path, Path]:
    logging.info("Starting AI Frontier pipeline")
    items, failures = collect(settings.timeout)
    write_json(ROOT / "data/raw" / f"{datetime.now():%Y-%m-%d}.json", [item.to_dict() for item in items])
    events = deduplicate(items)
    logging.info("Deduplicating... %s → %s events", len(items), len(events))
    for event in events:
        pre_score(event)
    events.sort(key=lambda event: event.pre_score, reverse=True)
    provider = provider_for(settings)
    logging.info("Structured LLM analysis with %s...", provider.name)
    try:
        result = provider.analyze([event.to_dict() for event in events[:12]])
    except Exception as exc:
        if not settings.allow_mock or provider.name == "mock":
            raise
        logging.warning("LLM unavailable (%s); falling back to mock", type(exc).__name__)
        provider = MockProvider()
        result = provider.analyze([event.to_dict() for event in events[:12]])
    originals = {event.id: event.to_dict() for event in events[:12]}
    analyzed = []
    for assessment in result.data.get("events", []):
        event_id = assessment.get("id")
        if event_id not in originals:
            continue
        merged = {**originals[event_id], **assessment}
        # Ground-truth identity and sources always come from retrieval, never the LLM.
        merged["title"] = originals[event_id]["title"]
        merged["sources"] = originals[event_id]["sources"]
        merged["published_at"] = originals[event_id]["published_at"]
        analyzed.append(merged)
    analyzed = sorted(analyzed, key=lambda event: event.get("ai_score", event.get("pre_score", 0)), reverse=True)[: settings.top_n]
    if not analyzed:
        raise RuntimeError("LLM returned no assessments matching retrieved event IDs")
    date = datetime.now().strftime("%Y-%m-%d")
    concept, build = result.data["concept"], result.data["build"]
    cost = {"date": date, "provider": provider.name, "model": result.model, "task": "daily_analysis", "input_tokens": result.input_tokens, "output_tokens": result.output_tokens, "estimated_cost_rmb": 0.0 if provider.name == "mock" else None, "daily_budget_rmb": settings.daily_budget_rmb}
    write_json(ROOT / "data/events" / f"{date}.json", analyzed)
    write_json(ROOT / "data/cost" / f"{date}.json", [cost])
    append_history(ROOT / "data/concepts.json", {"date": date, **concept})
    append_history(ROOT / "data/projects.json", {"date": date, **build, "status": "idea"})
    daily_path = ROOT / "daily" / f"{date}.md"
    build_path = ROOT / "builds" / f"{date}-{safe_slug(build.get('name_en', 'project'))}.md"
    daily_path.parent.mkdir(parents=True, exist_ok=True)
    build_path.parent.mkdir(parents=True, exist_ok=True)
    daily_path.write_text(render_daily(date, analyzed, concept, build, provider.name, failures), encoding="utf-8")
    build_path.write_text(render_build(date, build), encoding="utf-8")
    logging.info("Generated %s", daily_path)
    logging.info("Generated %s", build_path)
    if settings.enable_email:
        try:
            logging.info("Sending email...")
            send_daily_email(settings, date, analyzed, concept, build)
            logging.info("Email sent to %s", settings.email_to)
        except Exception as exc:
            logging.warning("Email unavailable: %s", type(exc).__name__)
    logging.info("Completed")
    return daily_path, build_path


def smoke_test(settings: Settings) -> int:
    if not settings.deepseek_api_key:
        print("Connection SKIPPED: DEEPSEEK_API_KEY is not configured")
        return 2
    provider = DeepSeekProvider(settings.deepseek_api_key, settings.deepseek_base_url, settings.fast_model, settings.smart_model, settings.timeout)
    result = provider.analyze([{"id": "smoke", "title": "Provider connectivity test", "summary": "Return grounded structured JSON.", "sources": [{"name": "local", "url": "https://example.com", "type": "test"}], "pre_score": 1.0}])
    print("Connection OK")
    print("Model:", result.model)
    print("Token Usage:", result.input_tokens + result.output_tokens)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke-test", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    config = Settings.load(ROOT)
    if args.smoke_test:
        raise SystemExit(smoke_test(config))
    run(config)
