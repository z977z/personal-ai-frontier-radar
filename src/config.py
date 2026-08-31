from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def as_bool(value: str) -> bool:
    return value.lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    root: Path
    llm_provider: str
    deepseek_api_key: str
    deepseek_base_url: str
    fast_model: str
    smart_model: str
    daily_budget_rmb: float
    top_n: int
    timeout: int
    allow_mock: bool
    enable_email: bool
    email_from: str
    email_to: str
    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    site_url: str

    @classmethod
    def load(cls, root: Path) -> "Settings":
        load_dotenv(root / ".env")
        return cls(
            root=root,
            llm_provider=os.getenv("LLM_PROVIDER", "deepseek"),
            deepseek_api_key=os.getenv("DEEPSEEK_API_KEY", ""),
            deepseek_base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com").rstrip("/"),
            fast_model=os.getenv("DEEPSEEK_MODEL_FAST", "deepseek-chat"),
            smart_model=os.getenv("DEEPSEEK_MODEL_SMART", "deepseek-reasoner"),
            daily_budget_rmb=float(os.getenv("DAILY_LLM_BUDGET_RMB", "0.5")),
            top_n=int(os.getenv("DAILY_TOP_N", "5")),
            timeout=int(os.getenv("HTTP_TIMEOUT_SECONDS", "12")),
            allow_mock=as_bool(os.getenv("ALLOW_MOCK_LLM", "true")),
            enable_email=as_bool(os.getenv("ENABLE_EMAIL", "false")),
            email_from=os.getenv("EMAIL_FROM", os.getenv("SMTP_USERNAME", "")),
            email_to=os.getenv("EMAIL_TO", ""),
            smtp_host=os.getenv("SMTP_HOST", "smtp.qq.com"),
            smtp_port=int(os.getenv("SMTP_PORT", "465")),
            smtp_username=os.getenv("SMTP_USERNAME", ""),
            smtp_password=os.getenv("SMTP_PASSWORD", ""),
            site_url=os.getenv("SITE_URL", ""),
        )
