# 规则引导分派 (Rule-Guided Dispatch)

- ID: `arch-dispatch`
- 类型: 方法机制
- 来源: 核心架构
- 分组: G-A · 核心架构
- 阶段: 进阶 intermediate

> 确定性文件选择/过滤/分束机制：用规则而非语言模型决定审什么、怎么分组

## 核心主张 (what)

- 分派阶段完全由确定性代码驱动：文件选择、过滤、分束均由规则与代码完成，不依赖 LLM 决策
- 文件选择确定要审哪些文件，过滤确定哪些排除并记录原因，分束将文件按规则组织成可并行处理的单元
- 规则采用四层链：custom（用户自定义）> project（项目级）> global（全局）> system（系统内置），上层规则优先级高于下层，形成可覆盖的规则体系
- 规则匹配使用模板引擎实现，比纯语言驱动（让模型读规则文本再判断）更稳定——同一规则在不同输入下结果确定可复现
- injectDiffMap 机制将被过滤文件的 diff 保留注入，供 file_read_diff 工具在需要时读取，实现『过滤但不封死』

## 为什么 (why)

- 文件选择与过滤是强约束环节：哪些文件该审、哪些规则适用属于可枚举逻辑，用确定性代码实现可保证行为一致、可单测，而 LLM 在此类任务上表现不稳定
- 四层规则链让不同范围的规则可叠加覆盖：用户可对单个文件/目录写 custom 规则覆盖全局默认，工程上形成类似 CSS 层叠的规则语义
- 模板引擎匹配规避了语言驱动的两个问题：prompt 长度膨胀（规则文本全塞进上下文）与判断随机性（同一文件两次判断可能不同）
- injectDiffMap 解决『过滤 vs 可读』的矛盾：被过滤文件不进主审查流程，但审查中若确实需要其 diff 上下文，file_read_diff 仍可读取，避免一刀切

## 如何实践 (how)

- 分派顺序：先按确定性逻辑选择 diff 中的文件集合 → 逐文件执行 whyExcluded 过滤链 → 按规则链匹配结果决定归属与排除原因
- 规则链匹配：从 custom 开始逐层查找适用规则，命中即生效，custom 层可显式覆盖 project/global/system 层的默认行为
- 过滤链顺序：binary（二进制）→ 用户 exclude（显式排除）→ 用户 include（显式包含可覆盖 exclude）→ 扩展名白名单（unsupported_ext）→ 默认路径黑名单（default_path）
- 每条被排除文件记录 ExcludeReason（user_exclude/unsupported_ext/default_path/deleted/binary），输出时可供用户审计为何没审某文件
- 注入机制：被过滤文件若被后续规则或工具需要，通过 injectDiffMap 写入其 diff 片段，file_read_diff 按需读取，不占主上下文预算

## 案例 (cases)

- 项目配置了 global 规则『忽略 vendor/ 与生成代码目录』，但某次审查需要核对 vendor 中一个依赖文件的行为差异——custom 规则 include 该文件，过滤链中 include 覆盖 exclude，该文件进入审查且其余 vendor 文件仍被排除
- 多语言仓库（Go+JS+Python）：system 层扩展名白名单只放行支持语言，二进制与 .min.js 等压缩产物在 binary/unsupported_ext 层被排除，用户可在 project 层加白名单覆盖

## 反模式/易错点

- 让 LLM 在 Plan 阶段自行决定『跳过哪些文件』——文件过滤必须发生在分派前的确定性阶段，模型自行跳过会造成审查覆盖不完整且不可审计
- 把所有规则写成 system 层一条大规则——应利用四层链分层，custom 覆盖用户特例，否则项目级定制只能改代码或全局配置
- 过滤后直接丢弃被过滤文件的 diff——正确做法是 injectDiffMap 保留，审查中发现需要上下文时 file_read_diff 还能读到，否则反复重跑 git 命令浪费
- 规则匹配用自然语言 prompt 驱动（把规则文本塞给模型）——模板引擎匹配才稳定，语言驱动在大规则集下判断漂移，且无法单测

## 相关关系

| 方向 | 类型 | 关系 |
|---|---|---|
| arch-hybrid → arch-dispatch | 前置依赖 | 确定性部分由分派承担 |
| arch-dispatch → eng-filter | 前置依赖 | 分派先做文件选择过滤 |
| arch-dispatch → eng-bundling | 前置依赖 | 分派再做文件分束 |
| arch-dispatch → cfg-rules-chain | 前置依赖 | 规则链是分派的数据源 |
| eng-filter → arch-dispatch | 组合 | 选择+分束组合成分派 |
| eng-bundling → arch-dispatch | 组合 | 选择+分束组合成分派 |
| arch-dispatch → arch-pipeline | 组合 | 分派+工具+反思组合成流水线 |
