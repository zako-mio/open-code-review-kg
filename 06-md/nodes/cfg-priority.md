# 配置优先级 (Config Priority)

- ID: `cfg-priority`
- 类型: 方法机制
- 来源: 配置模型
- 分组: G-D · 配置与模型
- 阶段: 进阶 intermediate

> 5 级解析：显式 --provider/--model > config.json > OCR_LLM_* 环境变量 > ANTHROPIC_* 环境变量 > shell RC

## 核心主张 (what)

- 5 级优先级链，实现于 internal/llm/resolver.go 的 ResolveEndpointWithOptions
- ① 最高：命令行显式 --provider/--model 参数
- ② OCR 配置文件：config.json 的 providers/custom_providers 段
- ③ OCR 环境变量：OCR_LLM_URL/OCR_LLM_TOKEN/OCR_LLM_MODEL/OCR_LLM_AUTH_HEADER/OCR_LLM_EXTRA_HEADERS/OCR_LLM_PROTOCOL/OCR_LLM_USE_ANTHROPIC/OCR_LLM_TIMEOUT
- ④ Claude Code 环境：ANTHROPIC_BASE_URL/ANTHROPIC_AUTH_TOKEN/ANTHROPIC_MODEL
- ⑤ 最低：shell RC（.zshrc/.bashrc 中 export 的 ANTHROPIC_* 系列）
- 高优先级覆盖低优先级：命令行 > config.json > OCR_* env > ANTHROPIC_* env > shell RC

## 为什么 (why)

- 配置来源多层并存（项目配置/CI 环境/用户 shell），确定性覆盖规则避免“改了不生效”的困惑
- 与 Claude Code 生态兼容：用户已有 ANTHROPIC_* 环境变量时可零配置复用
- CI 场景用环境变量注入比改配置文件更灵活，且不污染仓库

## 如何实践 (how)

- 临时指定（一级）：ocr review --provider openai --model gpt-4o
- 持久配置（二级）：写 config.json 的 providers 段
- CI/脚本（三级）：export OCR_LLM_URL=... OCR_LLM_MODEL=... OCR_LLM_TOKEN=...
- 复用 Claude Code（四级）：export ANTHROPIC_BASE_URL=... ANTHROPIC_AUTH_TOKEN=... ANTHROPIC_MODEL=...
- shell 常驻（五级）：在 .zshrc/.bashrc 中 export ANTHROPIC_* 系列
- 调超时：export OCR_LLM_TIMEOUT 覆盖默认超时
- 排查生效来源：对照 resolver.go 的 ResolveEndpointWithOptions 逐级确认当前取值
- 验证：查看实际请求的 base URL/模型名，确认被哪一级覆盖

## 案例 (cases)

- CI 中覆盖用户 shell 默认模型：CI 步骤 export OCR_LLM_MODEL（三级）压过用户 shell RC（五级）
- 团队统一端点：config.json 固定 provider，个人临时用命令行参数覆盖
- Claude Code 用户零配置迁移：已有 ANTHROPIC_* 环境变量直接生效
- 生产排障：请求超时/连错端点时按五级逐层排查取值来源

## 反模式/易错点

- 误以为环境变量优先于配置文件：实际 config.json（二级）优先于 OCR_* 环境变量（三级），改 env 不生效先查 config.json
- shell RC 改动后忘记新开终端/重启 shell，误判“配置不生效”
- 混用 ANTHROPIC_* 与 OCR_* 两组变量导致来源不明，排查前先确认当前生效级别
- 同时改 --provider 与 config.json provider 段但不一致：命令行参数生效，看起来“配置没改”
- 依赖 shell RC 的 ANTHROPIC_* 而未意识到它优先级最低，任何上层配置都能覆盖它

## 相关关系

| 方向 | 类型 | 关系 |
|---|---|---|
| cfg-providers → cfg-priority | 前置依赖 | provider 按优先级解析 |
| cfg-priority → cli-config | 前置依赖 | 配置命令写入优先级链 |
