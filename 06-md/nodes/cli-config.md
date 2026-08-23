# ocr config (ocr config)

- ID: `cli-config`
- 类型: 工具
- 来源: 命令行
- 分组: G-C · 命令行工具
- 阶段: 基础 basic

> 配置管理：set/unset 键值 + provider/model 交互式 TUI 向导（Bubble Tea），自动测试连通性

## 核心主张 (what)

- ocr config 是配置管理命令，统一管理模型提供商、模型名、token 上限、自定义提供商、MCP 服务器、LLM 行为、语言与遥测等配置项
- config set <key> <value> 写入配置，支持的键域包括：provider、model、max_tokens、providers.<name>.<field>（官方提供商字段）、custom_providers、mcp_servers、llm.*、language、telemetry.*
- config unset <key> 删除指定配置项，恢复默认或清除错误写入
- config provider 与 config model 为 Bubble Tea 构建的 TUI 交互向导：引导选择官方 provider、输入 API key、测试连接，面向新手友好
- 配置文件默认位于 ~/.opencodereview/config.json；环境变量 OCR_CONFIG_PATH 可覆盖配置的读路径，但写路径强制使用默认位置，防止配置写入被重定向造成泄漏

## 为什么 (why)

- 模型/提供商/LLM/遥测等配置项繁多且相互关联，集中式 key-value 管理与 TUI 向导比手改 JSON 更不易出错
- providers.<name>.<field> 的点分键域设计让 27 个内置 provider 与自定义 provider 的字段都能通过同一机制配置，无需特殊命令
- OCR_CONFIG_PATH 只覆盖读路径的强制设计，避免共享环境/CI 中配置被写入意外位置导致 API Key 等敏感信息泄漏到非预期文件

## 如何实践 (how)

- 设置提供商：ocr config set provider <name>（如 openai、deepseek）
- 设置模型：ocr config set model <model-id>
- 设置官方提供商字段：ocr config set providers.openai.apiKey sk-xxx 或 ocr config set providers.openai.baseUrl <url>
- 设置自定义提供商：ocr config set custom_providers.<name>.<field> <value>
- 设置 LLM 与遥测：ocr config set llm.temperature 0.2、ocr config set telemetry.enabled false
- 删除配置项：ocr config unset provider
- 交互式向导：ocr config provider（选择 provider 并输入 API key、测试连接）、ocr config model（选择模型）
- 指定配置读取：OCR_CONFIG_PATH=/path/to/config.json ocr config set provider openai，注意写路径仍为默认位置

## 案例 (cases)

- 首次安装配置：ocr config provider 进入 TUI 向导，选择官方 provider、粘贴 API key、测试连接成功后即可开始 review
- 切换模型供应商：ocr config set provider deepseek && ocr config set model deepseek-chat，一次切换全部生效
- 多环境隔离：CI 中设置 OCR_CONFIG_PATH 指向项目私有配置读取，同时保证写操作不会污染共享配置文件
- 排查字段名：不确定某 provider 支持哪些字段时，用 ocr config set providers.<name>.<field> 结合 ocr llm providers/test 验证

## 反模式/易错点

- 手改 ~/.opencodereview/config.json 导致 JSON 语法错误或字段拼写错误，工具静默回退默认配置，行为与预期不符，应优先用 config set/unset 与 TUI 向导
- 误以为 OCR_CONFIG_PATH 也覆盖写路径：用它指定配置后执行 set，配置被写入默认位置而非预期路径，误以为未生效或造成敏感信息落到错误文件
- 混淆 providers.<name>.<field>（内置提供商字段）与 custom_providers（自定义提供商）两个键域，把自定义字段写进 providers 导致不生效，接入非官方模型时应明确使用 custom_providers

## 相关关系

| 方向 | 类型 | 关系 |
|---|---|---|
| cfg-priority → cli-config | 前置依赖 | 配置命令写入优先级链 |
| cfg-protocol → cli-config | 前置依赖 | TUI 向导配置协议端点 |
| cli-overview → cli-config | 前置依赖 | 用前必须配置模型 |
| cli-config → use-configure | 组合 | provider+config 命令组合成配置场景 |
