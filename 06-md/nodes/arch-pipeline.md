# 审查流水线 (Review Pipeline)

- ID: `arch-pipeline`
- 类型: 方法机制
- 来源: 核心架构
- 分组: G-A · 核心架构
- 阶段: 基础 basic

> 从 CLI 入口到评论输出的 8 步确定性+Agent 混合时序：diff→过滤→分派→并行子 Agent→反思→输出

## 核心主张 (what)

- 整个审查过程被组织为 8 步时序流水线，从 CLI 入口到结果输出一气呵成，每步职责单一、可独立测试
- 第 1 步 CLI 入口：初始化 rules resolver（规则解析器）、LLM client 与工具注册表，搭建执行环境
- 第 2 步 diff 获取：按 workspace/range/commit 三种模式从 git 获取 diff，为后续过滤与审查提供原材料
- 第 3 步文件过滤：对 diff 中的文件执行 whyExcluded 过滤链，标记排除原因，确定真正进入审查的文件集合
- 第 4 步分派：以信号量（semaphore）限流，默认最多 8 个并发 goroutine 并行分派文件子任务
- 第 5 步每文件子任务：Plan（单轮 LLM 生成计划）→ MainTask（ReAct 循环执行工具调用）→ code_comment 异步定位评论 → REVIEW_FILTER 反思过滤，构成文件级审查主循环
- 第 6 步 WaitBackground：等待所有异步后台任务（如 code_comment 定位）完成
- 第 7 步 finalizeManifest：收尾汇总 manifest，合并各文件结果与元数据
- 第 8 步 emitRunResult：按 text/json/sarif 三种格式输出最终审查结果

## 为什么 (why)

- 8 步串行流水线把『获取 diff→筛选→审查→反思→输出』的职责彻底分离，任何一步可单独替换或升级，例如更换 diff Provider 不影响过滤与审查逻辑
- 文件级子任务（Plan→MainTask→反思）使每个文件的审查拥有独立生命周期，超时、失败、panic 可被隔离处理，不影响其他文件
- 信号量限流 + 每文件超时使并发度可控，避免大规模 diff 下资源雪崩，是阿里内部规模化运行的前提
- WaitBackground 与 finalizeManifest 分离保证了异步定位（code_comment）与结果收尾的顺序正确性，杜绝结果未齐就输出
- text/json/sarif 三种输出格式统一由 emitRunResult 承担，下游工具链（CI、IDE、SARIF 平台）只需对接稳定出口

## 如何实践 (how)

- CLI 入口阶段：创建 rules resolver（四层规则链加载）、LLM client（模型会话）与工具注册表（6 工具注册），三者作为后续步骤的共享依赖
- diff 获取阶段：按用户指定模式选择 Provider——range 用 git diff -U3 --find-renames merge-base..to、commit 用 git show --diff-merges=first-parent、workspace 用 tracked+untracked 组合，再经 ParseDiffText/ParseHunks 解析
- 文件过滤阶段：对每个 diff 条目执行 binary→exclude→include→扩展名白名单→默认路径黑名单的 whyExcluded 链，附 ExcludeReason
- 分派阶段：semaphore 初始化并发上限（默认 8），每个文件启动独立 goroutine，超过上限的等待
- 子任务阶段：先 Plan 单轮 LLM 产出审查计划 → 进入 MainTask ReAct 循环（模型调用受限 6 工具）→ 产出 code_comment 后异步定位（强制注入 path）→ 触发 REVIEW_FILTER_TASK 反思
- 并发控制：ConcurrentTaskTimeout 为每个文件设置独立超时；budget 前瞻 used+estimateDiffFileTokens>MaxTokensBudget 即提前停止；panic recover 隔离崩溃 goroutine；filterLargeDiffs 丢弃超过 80% MaxTokens 的大文件
- 收尾阶段：WaitBackground 等待异步任务 → finalizeManifest 汇总 → emitRunResult 按 text/json/sarif 输出

## 案例 (cases)

- CI 中通过 commit 模式审查一次 PR（多文件改动）：8 步流水线中过滤掉二进制/生成文件，8 并发分派，每文件独立 Plan+ReAct，最后输出 SARIF 供平台展示，全程无单文件故障拖累整体
- 对超大仓库全量 workspace 审查：filterLargeDiffs 丢弃超大文件 + budget 前瞻提前停止，使流水线在受限上下文预算内完成而非 OOM 崩溃

## 反模式/易错点

- 跳过 Plan 直接进入 MainTask——单轮 Plan 为 ReAct 循环提供方向锚点，缺失会导致工具调用路径发散、token 浪费
- 异步定位未等待（跳过 WaitBackground）就 finalizeManifest——code_comment 定位结果未落盘，输出评论缺 path 或位置
- 无限提高并发（信号量调大）换取速度——并发超过 8 时 token 预算与超时管理失配，出现资源雪崩，应先调 filterLargeDiffs 而非并发
- 在子任务阶段做全局过滤或全局反思——每文件上下文是隔离的，全局判断必须在分派前（过滤）或 finalizeManifest 阶段完成

## 相关关系

| 方向 | 类型 | 关系 |
|---|---|---|
| arch-hybrid → arch-pipeline | 前置依赖 | 混合理念决定流水线形态 |
| arch-pipeline → eng-diff | 前置依赖 | 流水线第一环是 diff 获取 |
| arch-dispatch → arch-pipeline | 组合 | 分派+工具+反思组合成流水线 |
| arch-grounded-tools → arch-pipeline | 组合 | 分派+工具+反思组合成流水线 |
| arch-reflection → arch-pipeline | 组合 | 分派+工具+反思组合成流水线 |
