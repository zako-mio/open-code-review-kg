# LLM 协议层 (LLM Protocol Layer)

- ID: `cfg-protocol`
- 类型: 方法机制
- 来源: 配置模型
- 分组: G-D · 配置与模型
- 阶段: 进阶 intermediate

> 4 种协议：Anthropic Messages / OpenAI Chat Completions / OpenAI Responses / Bedrock SigV4，统一 CompletionsWithCtx 接口

## 核心主张 (what)

- 抽象统一 LLMClient 接口，核心方法 CompletionsWithCtx，屏蔽不同厂商协议差异
- 4 种内置协议：anthropic（Messages API，基于 anthropic-sdk-go）、openai（Chat Completions，端点 /v1/chat/completions，基于 openai-go/v3）、openai-responses（OpenAI Responses API，端点 /v1/responses，URL 自动补后缀）、anthropic-bedrock（AWS SigV4 签名，模型名进 URL 路径）
- OpenAI 系协议流式响应走 ssestream（SSE 流解析）
- Responses API 为无状态设计：每个请求携带全量对话历史，服务端不维护会话状态
- 协议选择可通过 PROTOCOL 环境变量或 USE_ANTHROPIC 兼容开关控制

## 为什么 (why)

- 不同厂商 API 形态差异大（Messages 与 Chat Completions 的消息结构、工具调用格式不同），统一接口降低接入成本
- 协议可插拔：新增厂商只需实现 LLMClient 接口，扩展点清晰
- Responses API 无状态设计简化服务端实现，代价是客户端需自行携带全量历史

## 如何实践 (how)

- 显式指定：export OCR_LLM_PROTOCOL=openai（或 anthropic/openai-responses/anthropic-bedrock）
- Claude 兼容习惯：USE_ANTHROPIC=true 走 anthropic 协议（Messages API）
- AWS Bedrock：协议选 anthropic-bedrock，配置 AWS 凭证完成 SigV4 签名，模型名放入 URL 路径
- openai-responses：base URL 后自动补 /v1/responses 后缀，无需手动拼路径
- OpenAI 兼容网关（vLLM/OneAPI 等）：选 openai 协议指向 /v1/chat/completions
- 自定义 provider 时按端点能力选协议：OpenAI 兼容端点选 openai，Anthropic 兼容端点选 anthropic

## 案例 (cases)

- OpenAI 兼容网关：openai 协议 + /v1/chat/completions 端点
- Claude 官方或兼容端点：anthropic 协议 Messages API
- AWS Bedrock 上部署的模型：anthropic-bedrock 协议 + SigV4 签名
- 新项目接入 Responses API：openai-responses，享受无状态端点简化

## 反模式/易错点

- 忘记 Responses API 无状态特性：把短历史当会话用，模型丢失前文；每请求必须带全量历史
- Bedrock 选错协议：不用 anthropic-bedrock 就没有 SigV4 签名，请求 403
- openai-responses 手动拼接 URL：协议已自动补 /v1/responses 后缀，再拼会重复路径
- 流式响应当普通 JSON 解析：SSE 流需按 ssestream 处理，直接解析会截断或失败

## 相关关系

| 方向 | 类型 | 关系 |
|---|---|---|
| cfg-providers → cfg-protocol | 前置依赖 | provider 映射到协议 |
| cfg-protocol → cli-config | 前置依赖 | TUI 向导配置协议端点 |
| cfg-providers → cfg-protocol | 变体 | provider 与协议一一映射 |
