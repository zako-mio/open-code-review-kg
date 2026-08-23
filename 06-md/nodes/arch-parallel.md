# 文件级并行与上下文隔离 (Parallel & Isolation)

- ID: `arch-parallel`
- 类型: 方法机制
- 来源: 核心架构
- 分组: G-A · 核心架构
- 阶段: 高级 advanced

> 每文件一个子 Agent 任务、独立上下文，信号量限流（默认 8 并发），防 token 雪球

## 核心主张 (what)

- 每个文件拥有独立的子任务上下文：各自独立的 Plan、ReAct 循环、评论集合与 token 预算，互不共享也互不污染
- 并行度由信号量（semaphore）控制，默认 8 个并发 goroutine：超过上限的文件子任务排队等待
- ConcurrentTaskTimeout 为每个文件子任务设置独立超时：单文件卡死不会拖垮整批审查
- token 预算前瞻：每轮前检查 used+estimateDiffFileTokens 是否超过 MaxTokensBudget，超限即停止该文件，防止单文件耗尽总预算
- panic recover 隔离：单文件子任务的运行时崩溃被 recover 捕获，不影响其他并发子任务
- filterLargeDiffs 预过滤：超过 80% MaxTokens 的大文件在分派前即被丢弃，从源头规避超大上下文

## 为什么 (why)

- 文件级隔离使并行成为可能：每个文件独立上下文意味着无共享可变状态，goroutine 之间零锁竞争，天然可并行
- 默认 8 并发是在吞吐与 token 预算之间的平衡：并行过多会同时挤压多个文件的上下文预算，导致整体质量下降
- 超时与预算前瞻是规模化运行的刚性约束：真实仓库常有异常文件（超大、复杂、工具死循环），无约束会拖垮整批审查
- panic recover 把『偶发崩溃』从全局事故降级为单文件失败：单个文件的 bug 不应中断整个审查流水线
- 上下文隔离同时是质量保证：文件间不串上下文，评论不会把 A 文件的代码误引到 B 文件

## 如何实践 (how)

- 分派：过滤后的文件列表逐个申请 semaphore 许可（默认容量 8），获得许可后启动独立 goroutine 执行子任务
- 每文件子任务内部：Plan（单轮 LLM）→ MainTask（ReAct 循环，受限 6 工具）→ code_comment 异步定位 → REVIEW_FILTER 反思，全部在该文件私有上下文中进行
- 超时控制：ConcurrentTaskTimeout 从子任务启动开始计时，超时则该文件结果标记为超时失败，其余文件继续
- 预算前瞻：每轮 ReAct 迭代前计算 used（已用 token）+ estimateDiffFileTokens（预估 diff token）与 MaxTokensBudget 比较，超限立即终止该文件而非等待触发
- 崩溃隔离：goroutine 内 defer recover 捕获 panic，将错误记录到该文件结果而非向上抛
- 大文件预过滤：filterLargeDiffs 在分派前检测文件 diff 大小，超过 MaxTokens 的 80% 直接丢弃并记录原因，不进入并发队列

## 案例 (cases)

- 一次审查含 50 个文件：8 并发分批执行，其中一个文件 ReAct 循环异常膨胀被预算前瞻终止，一个文件发生 panic 被 recover 隔离，其余 48 个文件正常产出评论并汇总
- 超大单体文件（数万行 diff）在 filterLargeDiffs 阶段被丢弃，审查耗时与 token 消耗因此保持稳定，避免了单文件把整批预算吃光

## 反模式/易错点

- 为提速把 semaphore 调到几十——并行度与预算耦合，文件多了总 token 并发放大，整体质量下降，应先靠 filterLargeDiffs 控制体量
- 让所有文件共享一个全局上下文（先审完所有文件再总结）——文件间串上下文造成评论张冠李戴，且预算失控
- 无超时跑子任务——异常文件（工具死循环、diff 超大）会无限占用预算，ConcurrentTaskTimeout 是必须而非可选
- panic 不 recover 直接向上抛——单文件崩溃会终止整批审查，必须 goroutine 内 recover 并记录到该文件结果
