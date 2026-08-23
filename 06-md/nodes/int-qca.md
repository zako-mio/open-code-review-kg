# QCA Forward 委托 (QCA Forward)

- ID: `int-qca`
- 类型: 工具
- 来源: 集成生态
- 分组: G-E · 集成生态
- 阶段: 高级 advanced

> QCA 宿主模型运行委托模式：只允许 ocr delegate preview/rule（只读），OCR 侧零 LLM 调用

## 核心主张 (what)

- 「QCA Forward」是一种委托（delegate）模式，配置位于 qca/ 目录，核心文件为 system-prompt.md 与 template.example.json
- 该模式只允许调用 ocr delegate 子命令中的 preview 与 rule 两个只读子能力，明确禁止使用 ocr review，整体为只读行为设计
- 工作机制：由宿主模型（如 Claude、Qwen 等）按 template.example.json 模板组织审查请求，OCR 侧仅在收到委托请求时执行 preview/rule 操作，自身不发起任何 LLM 调用
- template.example.json 提供了委托请求的示例模板，用于规范宿主模型与 OCR 之间的消息契约，保证委托内容结构化可解析
- 典型适用场景：不想为 OCR 单独配置 API Key 的组织——审查推理发生在宿主模型侧，OCR 侧零 LLM 消耗
- 是 Open Code Review 多 Agent 生态中「委托/Forward」模式的代表实现，与 delegate 六步工作流互补

## 为什么 (why)

- 解决 Key 治理痛点：很多组织不希望在 CLI 侧再配一份模型 Key；QCA Forward 把推理放在已有宿主模型上，OCR 只做规则/预览等确定性操作，零 LLM 调用
- 只读安全边界：禁 ocr review、仅开放 preview/rule，保证委托模式下 OCR 不可能主动发起大范围审查，从机制上杜绝越权行为
- 通过 system-prompt.md 约束宿主行为、template.example.json 规范请求格式，让「谁说了算、什么格式」在集成前就确定，降低对接歧义
- 适合网关/中间层场景：组织已有统一模型网关（QCA 式），希望所有 AI 流量都走宿主，Forward 委托让 OCR 能力兼容该架构

## 如何实践 (how)

- 前置条件：确认 ocr CLI 可用，并在组织中确定宿主模型（负责推理的一方）与 OCR（仅执行 preview/rule 的一方）
- 阅读 qca/system-prompt.md，将其注入宿主模型的系统提示，使宿主理解：只能使用 ocr delegate preview / ocr delegate rule，禁止 ocr review，所有操作只读
- 参照 qca/template.example.json 模板结构，在宿主侧构造委托请求体（含目标文件/规则/范围等字段），保证与 OCR 期望的输入契约一致
- 宿主模型发起调用：执行 ocr delegate preview <范围> 先预览委托效果，确认目标与预期相符
- 需要规则检查时执行 ocr delegate rule <范围>，按配置的规则集对目标执行只读分析
- OCR 侧按委托请求执行并返回结果，全程不调用 LLM；审查判断与修复建议由宿主模型结合自身推理完成
- 验证：以模板示例为蓝本跑通一次「宿主发起 preview → OCR 返回结果」的链路，再逐步扩大范围
- 组织落地时把 system-prompt.md 与 template.example.json 固化进团队模板仓库，保证所有宿主按统一口径委托

## 案例 (cases)

- 某企业已有统一大模型网关（QCA）承担所有 AI 成本核算，接入 OCR 审查时采用 QCA Forward：宿主模型做审查判断，OCR 只执行 preview/rule，无需为 OCR 单独配 Key
- 合规敏感环境要求所有代码访问只读：QCA Forward 模式下 OCR 侧被 system-prompt 约束为纯只读操作，天然满足审计要求
- 多宿主混合团队：不同成员用不同宿主模型，统一通过 template.example.json 的契约向同一 OCR 实例委托 preview/rule，审查口径一致

## 反模式/易错点

- 在委托模式下偷偷启用 ocr review：system-prompt 明确禁止，若宿主绕过约束直接调 review，将破坏「零 LLM 调用、纯只读」的架构承诺并产生意外成本
- 把 template.example.json 当固定配置而非示例：不同宿主/场景需要按实际字段调整模板，直接硬套可能导致委托请求解析失败
- 忽略 host 侧 Key 需求：QCA Forward 只免了 OCR 侧的 Key，宿主模型仍需要自己的 Key/网关凭证，部署前应把两侧依赖清单列清楚
- 把 QCA Forward 与常规 delegate 混为一谈：Forward 模式禁用 review 且零 LLM，与 delegate 六步工作流（含逐文件审查、覆盖率报告）的能力边界不同，选型时应按组织的 Key 策略与审查深度需求区分
