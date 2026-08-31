from __future__ import annotations

from pathlib import Path
from typing import Any


def render_daily(date: str, events: list[dict[str, Any]], concept: dict[str, Any], build: dict[str, Any], provider: str, failures: list[str]) -> str:
    top = events[:5]
    big = top[0] if top else {"title": "今日无可确认的重要事件", "analysis": "信息不足，系统没有强行生成新闻。"}
    lines = [f"# AI Frontier Daily\n\nDate: {date}\n", "## 今日一句话\n", f"{big.get('title')}。{big.get('analysis', '')}\n", "## 🔥 Today's Big Story\n", f"**{big.get('title')}**\n\n{big.get('facts', '')}\n\n**分析：** {big.get('analysis', '')}\n", "# TOP 5\n"]
    for index, event in enumerate(top, 1):
        lines += [f"## {index}. {event['title']}\n", f"AI Importance Score：{event.get('ai_score', event.get('pre_score', 0))} / 10\n", f"**Facts：** {event.get('facts', '')}\n", f"**Analysis：** {event.get('analysis', '')}\n", f"**技术看点：** {event.get('technical_value', '')}\n", f"**可能影响：** {event.get('impact', '')}\n", "**Sources：**\n"]
        lines += [f"- [{source['name']}]({source['url']})\n" for source in event.get("sources", [])]
    lines += ["## Emerging AI Concept\n", f"中文名称：{concept.get('name_zh', '今日暂无')}  \n英文名称：{concept.get('name_en', '-')}  \nEmerging Score：{concept.get('score', '-')}  \n成熟度：{concept.get('maturity', '-')}\n", f"### 一句话理解\n\n{concept.get('explanation', '')}\n", f"### 为什么现在值得关注？\n\n{concept.get('why_now', '')}\n"]
    evidence = concept.get("evidence_urls", [])
    if evidence:
        lines += ["### Evidence\n"] + [f"- {url}\n" for url in evidence]
    lines += ["## 🛠 AI Build of the Day\n", f"**{build.get('name_zh')} / {build.get('name_en')}**\n\n{build.get('tagline')}\n\n- MVP：{build.get('mvp')}\n- 难度：{build.get('difficulty')}\n- 时间：{build.get('time')}\n", "## Run Metadata\n", f"- LLM provider: `{provider}`\n", f"- Source failures: {', '.join(failures) if failures else 'none'}\n"]
    return "\n".join(lines)


def render_build(date: str, build: dict[str, Any]) -> str:
    scenarios = "\n".join(f"- {item}" for item in build.get("scenarios", []))
    return f"""# AI Build of the Day

Date: {date}

中文名：{build.get('name_zh')}  
英文名：{build.get('name_en')}  
一句话：{build.get('tagline')}

## 为什么今天做？

{build.get('why_today')}

## 实际使用场景

{scenarios}

## Demo

{build.get('flow')}

## AI 在里面真正做什么？

{build.get('ai_role')}

## 技术方案

{build.get('stack')}

## MVP / 今日目标

今天只完成：{build.get('mvp')}

- 难度：{build.get('difficulty')}
- 预计时间：{build.get('time')}
- 预计代码量：{build.get('code_size')}

## V2

{build.get('v2')}
"""


def safe_slug(value: str) -> str:
    slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in value)
    return "-".join(filter(None, slug.split("-")))[:60] or "project"

