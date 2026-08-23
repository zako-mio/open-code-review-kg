# AACR-Bench 基准 (AACR-Bench)

- ID: `q-bench`
- 类型: 工程保障
- 来源: 工程保障
- 分组: G-F · 工程保障
- 阶段: 进阶 intermediate

> 50 仓库/200 真实 PR/10 语言/1505 人工标注问题的审查基准（HuggingFace 开源），驱动 Precision/F1/token 量化优化

## 核心主张 (what)

- AACR-Bench 是 Open Code Review 项目构建的自动化 AI 代码审查基准（Automated AI Code Review benchmark），用于评测与对比 AI 审查能力
- 数据规模：覆盖 50 个流行仓库、200 个真实 PR、10 种编程语言，保证语料多样性与真实性（全部来自真实代码实践而非合成样例）
- 标注质量：由 80+ 名资深工程师交叉标注出 1505 个真实问题，多人在标保证问题标签的准确性与一致性
- 数据开源：数据集托管于 HuggingFace，仓库名为 Alibaba-Aone/aacr-bench，可公开获取用于复现与对比实验
- 评测口径：同模型、同 backend 下对比，控制变量以保证对比公平性
- 论文发表于 arXiv，编号 2608.09290，标题《OpenCodeReview: Determinism over Non-Determinism》（确定性优于非确定性）

## 为什么 (why)

- AI 代码审查缺乏统一可信的评测标准，AACR-Bench 用真实 PR + 专家交叉标注构建 ground truth，让「审查质量」可量化、可对比
- 同模型同 backend 的控制变量设计，隔离模型能力与基础设施差异，保证 SEM-F1 等指标的对比结论归因于审查方法本身
- 开源数据集（HuggingFace）与论文并行的形式支持学术界/工业界复现验证，增强基准公信力
- 「Determinism over Non-Determinism」的定位说明项目追求确定性可复现的审查行为，基准是这一理念的量化支撑

## 如何实践 (how)

- 数据获取：从 HuggingFace 拉取数据集 Alibaba-Aone/aacr-bench（含 50 仓库、200 PR、1505 条专家标注问题的数据文件）
- 复现对比：使用相同模型（如同一 LLM）与相同 backend，分别运行待测审查方法与基线，保证变量受控
- 计算指标：以 SEM-F1（语义匹配 F1）为核心指标衡量审查问题与专家标注的匹配度，同时统计 token 消耗与耗时
- 运行项目自身评测脚本/按论文方法执行，获取各项数值：SEM-F1、token 消耗、耗时、Recall 等
- 解读结果：对照「SEM-F1 最高 2.17x（25.10% vs 11.57%）、token 约 1/9、耗时更快」等已发布数据评估自身配置的相对水平
- 如需与 Codex 对比，参照其 2.5x SEM-F1 同成本的表现数据作为参照系
- 发布或审计时，可引用论文 arXiv 2608.09290 作为方法学依据
- 对 Recall 的解读：项目为精度优先、降误报而主动取舍 Recall 略低，对比时应同时看精度与误报率而非单看 Recall

## 案例 (cases)

- 项目团队在发布新版本前跑 AACR-Bench 对比：同模型同 backend 下 SEM-F1 达到 25.10%，相对基线 11.57% 提升 2.17x，token 消耗降至约 1/9，作为版本宣传数据
- 潜在用户评估是否采用 OCR：在 AACR-Bench 上对比 Codex，得到 2.5x SEM-F1、同成本的结果，辅助选型决策
- 研究者基于 HuggingFace 开源数据（Alibaba-Aone/aacr-bench）复现论文 arXiv 2608.09290 的实验，验证方法结论并做延伸实验
- 评测强调确定性：在相同输入下多次运行应得到稳定一致的审查结果，呼应「Determinism over Non-Determinism」的论文主题

## 反模式/易错点

- 跨 backend 直接对比：基准明确要求同模型同 backend 才可比，用不同后端（不同推理服务/参数）跑出的 SEM-F1 对比会得到误导性结论
- 只报 SEM-F1 不看 token/耗时/Recall：2.17x 是精度收益，但 token 约 1/9、耗时更快的成本优势与 Recall 略低的取舍同样重要，单指标宣传以偏概全
- 把 Recall 略低解读为缺陷：这是「精度优先、降误报」的设计取舍，审查场景下低误报往往比高召回更有工程价值，应结合误报率一起评估
- 忽略数据集版本与标注口径：1505 条问题来自 80+ 专家交叉标注，复现时若使用不同清洗/匹配规则，数字可能对不上；应严格按论文与数据集说明的评测流程执行

## 相关关系

| 方向 | 类型 | 关系 |
|---|---|---|
| q-bench → arch-hybrid | 前置依赖 | 基准验证混合架构有效性 |
