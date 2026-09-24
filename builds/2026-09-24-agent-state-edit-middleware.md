# AI Build of the Day

Date: 2026-09-24

中文名：智能体状态编辑中间件  
英文名：Agent State-Edit Middleware  
一句话：在真实执行循环中实时识别并修正智能体的噪声推理-动作状态

## 为什么今天做？

LLM 智能体在长程任务中因历史污染而失败率高，而现有世界模型模拟工具响应成本高、收益低；AEWM 证明直接编辑任务状态可在多环境提升 3.2–6.7 分，具备工程落地条件。

## 实际使用场景

- 长程搜索智能体
- 终端运维智能体
- 软件工程智能体
- 多步工具调用工作流

## Demo

观测历史输入 -> Action Judge 分类决策为 Critical/Exploratory/Noisy -> State Revision 对 Noisy 延续生成编辑 -> EditAct 将编辑结果与真实执行结合 -> 更新任务状态 -> 进入下一轮决策

## AI 在里面真正做什么？

Action Judge 使用微调 LLM 对决策分类；State Revision 使用 LLM 生成状态编辑；EditAct 在真实执行前应用编辑并记录轨迹用于后续 RFT。

## 技术方案

基础 LLM（如 Qwen 系列）+ mid-training/SFT 微调 + 真实工具执行环境（Search/Terminal/SWE）+ 轨迹记录与拒绝采样微调流水线

## MVP / 今日目标

今天只完成：在单一环境（如 Terminal）实现 Action Judge 分类器与 State Revision 编辑器，接入现有 agent 循环，用少量标注轨迹做 SFT，验证任务成功率提升。

- 难度：中高
- 预计时间：4–8 周
- 预计代码量：约 3000–6000 行（含训练与集成）

## V2

扩展至多环境统一 Action Judge，加入在线 AEWM 引导与 AEWM-RFT 离线微调，支持多模态观测与跨智能体迁移。
