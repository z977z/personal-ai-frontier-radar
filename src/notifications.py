from __future__ import annotations

import html
import smtplib
from email.message import EmailMessage
from typing import Any

from .config import Settings


def render_email_html(date: str, events: list[dict[str, Any]], concept: dict[str, Any], build: dict[str, Any], site_url: str) -> str:
    top = events[:3]
    rows = "".join(
        f"<li><strong>{html.escape(event.get('title', ''))}</strong> — "
        f"{html.escape(event.get('analysis', ''))}</li>"
        for event in top
    )
    link = f'<p><a href="{html.escape(site_url)}">Read Full Report</a></p>' if site_url else ""
    big_story = top[0] if top else {}
    return f"""<!doctype html><html><body style="font-family:Arial,sans-serif;line-height:1.6;max-width:680px;margin:auto">
<h1>AI FRONTIER DAILY</h1><p>{html.escape(date)}</p>
<h2>🔥 TODAY'S BIG STORY</h2><h3>{html.escape(big_story.get('title', '今日暂无'))}</h3>
<p>{html.escape(big_story.get('analysis', ''))}</p>
<h2>TOP 3</h2><ol>{rows}</ol>
<h2>🚨 EMERGING CONCEPT</h2><p><strong>{html.escape(concept.get('name_zh', '今日暂无'))}</strong> / {html.escape(concept.get('name_en', ''))}</p>
<p>{html.escape(concept.get('explanation', ''))}</p>
<h2>🛠 BUILD OF THE DAY</h2><p><strong>{html.escape(build.get('name_zh', ''))}</strong> / {html.escape(build.get('name_en', ''))}</p>
<p>{html.escape(build.get('tagline', ''))}</p>{link}
</body></html>"""


def send_daily_email(settings: Settings, date: str, events: list[dict[str, Any]], concept: dict[str, Any], build: dict[str, Any]) -> None:
    missing = [name for name, value in {
        "EMAIL_FROM": settings.email_from,
        "EMAIL_TO": settings.email_to,
        "SMTP_USERNAME": settings.smtp_username,
        "SMTP_PASSWORD": settings.smtp_password,
    }.items() if not value]
    if missing:
        raise ValueError("Email enabled but missing: " + ", ".join(missing))
    message = EmailMessage()
    message["Subject"] = f"AI Frontier Daily | {date}"
    message["From"] = settings.email_from
    message["To"] = settings.email_to
    message.set_content(f"AI Frontier Daily {date}. Please view the HTML version of this email.")
    message.add_alternative(render_email_html(date, events, concept, build, settings.site_url), subtype="html")
    with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, timeout=settings.timeout) as smtp:
        smtp.login(settings.smtp_username, settings.smtp_password)
        smtp.send_message(message)
