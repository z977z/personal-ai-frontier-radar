from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


@dataclass
class LLMResult:
    data: dict[str, Any]
    model: str
    input_tokens: int = 0
    output_tokens: int = 0


class BaseLLMProvider:
    name = "base"
    def analyze(self, events: list[dict[str, Any]], model_role: str = "smart") -> LLMResult:
        raise NotImplementedError


class MockProvider(BaseLLMProvider):
    name = "mock"
    def analyze(self, events: list[dict[str, Any]], model_role: str = "smart") -> LLMResult:
        ranked = sorted(events, key=lambda x: x["pre_score"], reverse=True)
        enriched = []
        for event in ranked:
            enriched.append({**event, "ai_score": event["pre_score"], "facts": event["summary"] or event["title"], "analysis": "该事件值得继续跟踪；当前为 Mock 分析，判断仅用于验证系统流程。", "technical_value": "观察其工具、模型或开发者生态影响。", "impact": "需要后续官方资料和历史数据确认。", "keywords": extract_keywords(event["title"] + " " + event["summary"])})
        concept = {"name_zh": "模型上下文协议", "name_en": "Model Context Protocol", "score": 7.2, "maturity": "Growing", "explanation": "让 AI 应用以统一方式连接外部工具和数据。", "why_now": "工具调用和 Agent 应用增长，使标准化连接层更重要。", "evidence_urls": [s["url"] for e in ranked for s in e["sources"] if "modelcontextprotocol" in s["url"]][:2]}
        build = {"name_zh": "来源核验助手", "name_en": "Source Grounding Checker", "tagline": "检查 AI 摘要里的事实是否有来源支撑。", "why_today": "与今日情报系统的来源验证需求直接相关。", "scenarios": ["日报事实核查", "研究笔记审阅", "产品发布摘要检查"], "flow": "User → 粘贴摘要与来源 → AI 提取主张 → 程序匹配证据 → 核验结果", "ai_role": "AI 提取可核验主张并解释证据缺口；URL 与匹配结果由程序保存。", "stack": "Python CLI + JSON + 当前 LLM Provider", "mvp": "输入一段摘要和来源列表，输出 supported/unconfirmed 主张。", "difficulty": "★★☆☆☆", "time": "2h", "code_size": "150–250 行", "v2": "加入网页正文抓取和引用定位。"}
        return LLMResult({"events": enriched, "concept": concept, "build": build}, "mock-deterministic")


def extract_keywords(text: str) -> list[str]:
    known = ["MCP", "Agent", "Reasoning", "Multimodal", "Open Source", "Model", "Research"]
    low = text.lower()
    return [word for word in known if word.lower() in low][:5] or ["AI"]


class DeepSeekProvider(BaseLLMProvider):
    name = "deepseek"
    def __init__(self, api_key: str, base_url: str, fast_model: str, smart_model: str, timeout: int):
        self.api_key, self.base_url = api_key, base_url
        self.fast_model, self.smart_model, self.timeout = fast_model, smart_model, timeout

    def analyze(self, events: list[dict[str, Any]], model_role: str = "smart") -> LLMResult:
        model = self.smart_model if model_role == "smart" else self.fast_model
        schema = '{"events":[{"id":"...","ai_score":0,"facts":"...","analysis":"...","technical_value":"...","impact":"...","keywords":[]}],"concept":{"name_zh":"","name_en":"","score":0,"maturity":"Emerging","explanation":"","why_now":"","evidence_urls":[]},"build":{"name_zh":"","name_en":"","tagline":"","why_today":"","scenarios":[],"flow":"","ai_role":"","stack":"","mvp":"","difficulty":"","time":"","code_size":"","v2":""}}'
        prompt = "你是严谨的AI技术情报分析师。只依据输入事件及其URL，事实和分析分开，不虚构动态数据。返回且仅返回合法JSON，结构为：" + schema + "\n事件：" + json.dumps(events, ensure_ascii=False)
        payload = {"model": model, "messages": [{"role": "system", "content": "输出严格JSON。"}, {"role": "user", "content": prompt}], "response_format": {"type": "json_object"}, "temperature": 0.2}
        body = self._post(payload)
        content = body["choices"][0]["message"]["content"]
        content = re.sub(r"^```(?:json)?|```$", "", content.strip(), flags=re.MULTILINE).strip()
        usage = body.get("usage", {})
        return LLMResult(json.loads(content), model, usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0))

    def _post(self, payload: dict[str, Any]) -> dict[str, Any]:
        req = urllib.request.Request(self.base_url + "/chat/completions", data=json.dumps(payload).encode(), headers={"Authorization": "Bearer " + self.api_key, "Content-Type": "application/json"}, method="POST")
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as response:
                    return json.loads(response.read())
            except (urllib.error.URLError, TimeoutError) as exc:
                last_error = exc
                if attempt < 2:
                    time.sleep(1.5 * (attempt + 1))
        raise RuntimeError(f"DeepSeek request failed: {type(last_error).__name__}") from last_error

