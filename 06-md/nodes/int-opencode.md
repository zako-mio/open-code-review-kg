# OpenCode 原生插件 (OpenCode Native Plugin)

- ID: `int-opencode`
- 类型: 工具
- 来源: 集成生态
- 分组: G-E · 集成生态
- 阶段: 高级 advanced

> @opencode-ai/plugin：tool() 注册原生审查工具，spawn 'ocr review --audience agent --format json'，参数互斥校验

## 核心主张 (what)

- Alibaba Open Code Review 为 OpenCode（本工具）提供的原生插件，文件为 plugins/open-code-review/opencode/open-code-review.ts，基于 @opencode-ai/plugin 官方插件 SDK 开发
- 插件通过 tool() 函数注册一个原生工具，将 ocr 审查能力以 OpenCode 工具调用的形态暴露，而非斜杠命令或外部 Skill
- 工具实现内部通过 spawn 执行 'ocr review --audience agent --format json' 子进程，即调用 ocr CLI 并以 JSON 格式输出供程序化消费
- 工具参数经过校验，commit / from / to / resume / preview 等参数之间存在互斥约束，非法组合会被拒绝，避免含糊的审查范围
- 提供「原生工具调用体验」：在 OpenCode 会话中，模型可直接以标准工具调用协议触发审查，结果以结构化 JSON 回流，适合程序化与自动化链路

## 为什么 (why)

- OpenCode 与 OCR 同属 AI 编码生态，原生插件形式（相对斜杠命令/Skill）让审查能力以标准工具调用参与模型决策循环，可被自动编排（如审查后自动接修复）
- --audience agent --format json 的输出设计面向 Agent 消费，保证模型能稳定解析审查结果，这是工具化集成的关键前提
- 参数互斥校验（commit/from/to/resume/preview）在工具层前置拦截非法调用，避免审查范围含糊导致的结果不可信或误报
- 与官方 SDK 对齐的开发方式降低了维护成本，也方便社区复用该插件模式

## 如何实践 (how)

- 前置条件：安装 ocr CLI 并配置 API Key；当前环境为 OpenCode 且已支持 @opencode-ai/plugin 插件体系
- 将 plugins/open-code-review/opencode/ 下的 open-code-review.ts 及其依赖放入 OpenCode 的插件目录（如 ~/.config/opencode/plugin/ 或项目级 .opencode/plugin/），按 OpenCode 插件加载规范注册
- OpenCode 启动时加载插件，tool() 注册的原生工具自动出现在模型可用的工具列表中
- 在会话中向模型发起审查意图（如「审查当前改动」），模型会以工具调用方式触发 ocr review --audience agent --format json
- 通过工具参数指定审查范围：提交范围用 from/to（或 commit），需要续跑时用 resume，仅预览时用 preview；注意这些参数互斥，不能混用
- 工具返回 JSON 审查报告后，模型在会话内呈现结果并可与用户继续讨论、筛选或安排修复
- 可用 preview 参数先行预览审查意图，确认范围正确后再正式执行，避免误审大范围代码
- 验证：在会话中发起一次最小审查（如单文件），确认子进程调用与 JSON 返回正常

## 案例 (cases)

- 在 OpenCode 中完成代码修改后，直接要求模型「审查本次提交之前的改动」，模型自动调用原生工具完成审查并在会话内汇报
- 构建自动审查链路：让模型在完成编码任务后自动触发审查工具，若发现高严重度问题则继续修复并复跑，形成「编码—审查—修复」闭环
- 对历史提交做定向审查：用 from/to 参数限定两个提交之间的范围，工具互斥校验保证不会同时混入 preview 等冲突语义

## 反模式/易错点

- 混用互斥参数：同时传 commit 与 from/to（或 preview 与 resume），工具参数校验会直接拒绝；应先理解互斥关系，一次只指定一种范围语义
- 不装 CLI 直接依赖插件：插件内部 spawn 'ocr review'，本机无 ocr 可执行文件时工具必然失败；任何 OpenCode 集成前先验证 CLI 可用
- 把 --format json 的输出当人类阅读文本：JSON 是给 Agent 消费的结构化数据，直接展示原始 JSON 会破坏可读性，应由模型转述
- 忽略 preview 的价值：在大范围审查前不先用 preview 校验范围，导致误审并消耗大量 token；先预览后执行是成本控制的关键习惯

## 相关关系

| 方向 | 类型 | 关系 |
|---|---|---|
| int-codex → int-opencode | 变体 | 同为插件生态 |
| int-opencode → cli-review | 依赖关联 | OpenCode 插件 spawn CLI |
