# ocr delegate (ocr delegate)

- ID: `cli-delegate`
- 类型: 工具
- 来源: 命令行
- 分组: G-C · 命令行工具
- 阶段: 进阶 intermediate

> 委托模式：OCR 只做文件选择+规则解析输出 spec JSON，编码 Agent 用自己的 LLM 审查，无需 OCR API Key

## 核心主张 (what)

- ocr delegate 是委托模式：工具自身不调用 LLM，只负责分析准备，把审查工作委托给宿主编码 Agent（如 Cursor/Claude Code 等）用自己的模型完成
- 子命令 preview：输出审查准备的元数据，--format json 时结构化返回 mode（workspace/range/commit 三种范围模式）、merge_base（合并基准）、可审查文件清单、excluded_files（被排除文件）
- 子命令 rule：ocr delegate rule <paths> 按 source\|pattern\|text 三元组对规则进行聚类，输出规则结构，供宿主 Agent 理解将应用的规则体系
- 该模式无需 OCR API Key，也不消耗 OCR 侧模型额度，模型费用由宿主 Agent 自身的 LLM 承担
- 适合将 ocr 的分析管道（git diff 解析、文件筛选、规则匹配）复用为第三方 Agent 的审查前置步骤

## 为什么 (why)

- 许多用户的主要工作流在 AI 编码 Agent 中完成，ocr 直接调 LLM 会与宿主 Agent 的模型形成双重调用与双份成本，delegate 让宿主用自己的模型完成审查
- 避免 API Key 集中管理：无需在 ocr 侧配置任何提供商密钥，降低密钥泄露面
- preview 输出结构化元数据（mode/merge_base/文件清单/排除清单），宿主 Agent 可精确复现 ocr 的审查范围，保证一致性

## 如何实践 (how)

- 获取审查准备元数据：ocr delegate preview --format json，解析其中的 mode、merge_base、可审查文件清单与 excluded_files
- 按输出调整范围：根据 mode（workspace/range/commit）确认审查口径，用 merge_base 确定对比基准
- 获取规则结构：ocr delegate rule <paths>（paths 为目录或文件），查看按 source\|pattern\|text 三元组聚类的规则输出
- 将 preview 的文件清单与 rule 输出一并交给宿主 Agent，由宿主 Agent 用自己的 LLM 逐文件审查并产出结论

## 案例 (cases)

- 在 Claude Code/Cursor 等 Agent 环境中委托审查：宿主 Agent 先运行 ocr delegate preview --format json 拿到变更清单，再自行逐文件审查，全程无 OCR API Key
- 无模型额度场景：本机没有配置任何 LLM Key 或不想在 ocr 侧花钱时，用 delegate 把分析交给已有 Agent 生态
- 审查范围精确控制：在 merge 前只想审 feature 分支引入的变更，通过 preview 的 mode 与 merge_base 字段核对范围是否符合预期

## 反模式/易错点

- 期望 delegate 直接产出审查结论：delegate 只做分析准备（preview/rule），不调 LLM 也不产出审查意见，把产出归零当工具故障是常见误解
- 忽略 preview 的 mode/merge_base 字段直接开审：范围口径错误会导致审查了不该审的文件或漏掉关键变更，务必先核对元数据
- 把 ocr delegate rule 的输出当作最终规则文件直接套用：它只是规则结构的聚类视图，规则生效链路仍要回到 ocr rules check 与四层规则链确认

## 相关关系

| 方向 | 类型 | 关系 |
|---|---|---|
| eng-bundling → cli-delegate | 前置依赖 | 委托模式按规则文本分束 |
| int-claude → cli-delegate | 前置依赖 | Claude 插件可走委托模式 |
| cli-delegate → use-no-key | 前置依赖 | 免 Key 场景指向 delegate |
| cli-delegate → cli-review | 变体 | 委托 vs OCR 驱动 |
| cli-delegate → use-no-key | 共现 | 委托模式即免 Key 场景 |
