# Personal AI Frontier Radar

一个小型、可靠、低成本的个人 AI 情报系统。MVP 会采集可靠 RSS/Atom 来源，清洗并合并重复事件，以结构化 LLM 输出完成评分、新概念发现和每日动手项目，最后生成可追踪的 Markdown 与 JSON 数据。

## 架构

`collectors → normalize/deduplicate → deterministic pre-score → LLM structured analysis → validation → Markdown/JSON → cost ledger`

事实与分析分开保存；动态事实必须附来源。单个来源失败只记录日志，不阻断日报。未配置 API Key 时使用 Mock Provider，便于开发和 CI；这会在报告中明确标注，不冒充真实 AI 分析。

## 本地运行

需要 Python 3.11+：

```powershell
cd C:\VScode\personal-ai-frontier
Copy-Item .env.example .env
python main.py
python -m unittest discover -s tests -v
```

首次运行可直接不创建 `.env`。输出位于 `daily/`、`builds/` 和 `data/`。

## DeepSeek 配置

在不会提交的 `.env` 中设置：

```env
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=your_key_here
DEEPSEEK_MODEL_FAST=deepseek-chat
DEEPSEEK_MODEL_SMART=deepseek-chat
```

真实连通性测试：

```powershell
python main.py --smoke-test
```

程序只显示连接状态、模型和 token 用量，不显示密钥。`LLM_PROVIDER` 与业务逻辑解耦，未来可增加 Qwen/Kimi Provider。

## 当前范围

本阶段已覆盖采集、清洗、去重、预评分、DeepSeek/Mock Provider、结构化分析、TOP 5、Emerging Concept、Build of the Day、Markdown、历史与成本记录。GitHub Actions、Pages 和邮件属于第二阶段。

## 常见问题

- 所有来源均失败：仍会用内置带来源的演示样本生成降级报告，并标注运行模式。
- DeepSeek 失败：开启 `ALLOW_MOCK_LLM=true` 时自动降级；错误不会包含密钥。
- 预算：`DAILY_LLM_BUDGET_RMB` 是软上限；达到上限后优先停止额外智能模型调用。
