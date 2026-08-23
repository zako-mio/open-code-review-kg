# Provider 体系 (Provider Registry)

- ID: `cfg-providers`
- 类型: 方法机制
- 来源: 配置模型
- 分组: G-D · 配置与模型
- 阶段: 基础 basic

> 27 个内置 LLM provider（anthropic/openai/dashscope/deepseek/z-ai/kimi/...）+ 自定义端点，覆盖国内外主流模型

## 核心主张 (what)

- 内置 27 个 LLM provider，覆盖国内外主流大模型服务商：anthropic、bedrock(AWS SigV4)、openai、edenai、gemini、dashscope、dashscope-tokenplan、volcengine、deepseek、tencent-tokenhub、hy-tokenplan、iflytek、kimi、kimi-global、z-ai、z-ai-coding、mimo、minimax、minimax-cn、baidu-qianfan、ollama-cloud、novita、xai、litellm、siliconflow、siliconflow-cn、mistral
- 每个 provider 携带完整的连接元数据：BaseURL（API 端点）、AuthHeader（认证头格式）、EnvVar（对应环境变量名）、Models（可用模型列表），开箱即用
- 支持 custom_providers 自定义 provider，可指向任意端点，包括私有化部署的 LLM（内网/自建网关）
- 国内用户可直接选择 DashScope（阿里通义）或 DeepSeek，无需海外网络即可使用
- provider 体系与协议层解耦：provider 决定连谁，协议（openai/anthropic 等）决定怎么连
- provider 选择可通过 config.json 的 providers/custom_providers 段或命令行 --provider 参数指定

## 为什么 (why)

- 避免厂商锁定：一套 CLI 即可在 OpenAI/Anthropic/国内各家模型间切换，评估与迁移成本低
- 适配国内网络与合规环境：内置 DashScope、DeepSeek、Volcengine、百度千帆等国内端点，直连无需代理
- 满足私有化需求：企业可通过 custom_providers 接入内网模型网关，代码审查数据不出内网

## 如何实践 (how)

- 持久配置：在 config.json 的 providers 段配置官方 provider（models 列表、max_tokens 等参数）
- 私有化接入：在 custom_providers 段定义自定义端点，配置 base_url、auth_header、env_var、models 等字段
- 命令行指定：ocr review --provider deepseek --model deepseek-chat
- 环境变量覆盖：OCR_LLM_URL/OCR_LLM_TOKEN/OCR_LLM_MODEL 可覆盖 provider 的连接信息
- AWS 场景：选 bedrock provider，配合 anthropic-bedrock 协议（SigV4 签名）走通鉴权
- 查看当前生效的 provider 与模型配置，确认 BaseURL/AuthHeader 与密钥是否就绪

## 案例 (cases)

- 国内用户：--provider deepseek --model deepseek-chat 直连使用，无需代理
- 阿里云用户：选 dashscope（通义千问系列），与云上环境天然匹配
- 企业私有化：custom_providers 指向内网 vLLM/统一网关端点，审查数据不出内网
- AWS 环境：bedrock provider + anthropic-bedrock 协议，模型名进 URL 路径完成 SigV4 请求

## 反模式/易错点

- 误以为 27 个 provider 全部开箱即用：未设置 provider 对应 EnvVar 的密钥时鉴权必然失败
- 选海外 provider（openai/gemini 等）而不考虑网络：国内直连可能超时，应改用国内 provider 或代理
- 混淆 provider 与协议：bedrock 必须配 anthropic-bedrock 协议做 SigV4 签名，配成 openai/anthropic 会 403
- custom_providers 只配 base_url 不配 AuthHeader/协议，导致 401 或协议不匹配报错

## 相关关系

| 方向 | 类型 | 关系 |
|---|---|---|
| cfg-providers → cfg-protocol | 前置依赖 | provider 映射到协议 |
| cfg-providers → cfg-priority | 前置依赖 | provider 按优先级解析 |
| cfg-providers → cli-llm | 前置依赖 | llm providers 列出内置注册表 |
| cfg-providers → cfg-protocol | 变体 | provider 与协议一一映射 |
| cfg-providers → use-configure | 组合 | provider+config 命令组合成配置场景 |
