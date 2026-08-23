# 受限工具集审查 (Grounded File Review)

- ID: `arch-grounded-tools`
- 类型: 方法机制
- 来源: 核心架构
- 分组: G-A · 核心架构
- 阶段: 进阶 intermediate

> 6 个审查专用工具（file_read/file_find/code_search/file_read_diff/code_comment/task_done）经 ReAct 循环驱动文件级子 Agent

## 核心主张 (what)

- 审查 Agent 只被授予 6 个受限工具：file_read（读文件）、file_find（找文件）、code_search（代码搜索）、file_read_diff（读被过滤文件的 diff）、code_comment（发表评论）、task_done（结束任务）
- 工具集经 ReAct 循环调用：模型在思考（Reason）与行动（Act）间交替，每个行动对应一次工具调用，形成受限但有表达力的审查交互循环
- 工具清单是从线上工具调用轨迹分析中取舍沉淀而来：统计真实审查中哪些工具被高频使用、哪些带来收益、哪些导致失败，据此收敛出最小够用集
- 设计目标之一是防 token 雪球：工具越少、每次调用返回越可控，上下文不会因无界探索而指数膨胀
- code_comment 强制注入 path 参数：模型必须给出评论目标文件的真实路径，防止幻觉路径（模型编造不存在的文件路径）

## 为什么 (why)

- 给 Agent 全量工具（任意 shell、任意文件写、任意网络）在审查场景既危险又浪费：审查只需读代码与发评论，写操作与执行操作完全不需要
- 线上轨迹分析表明大部分无效 token 消耗来自模型在无关工具间来回试探，收敛工具集等于收敛行为空间，直接贡献 token 省 5-15x
- 受限工具集配合场景化注册：不同审查场景（文件审查/全局搜索）可注册不同工具子集，进一步缩小模型决策面
- 防 token 雪球是规模化运行刚需：6 工具 + 预算前瞻（used+estimateDiffFileTokens 超限即停）双保险，避免单个文件耗尽整个会话预算
- code_comment 强制 path 是幻觉防护的关键机制：评论定位由确定性组件异步完成，path 由工具层注入而非模型自由填写

## 如何实践 (how)

- 工具注册：CLI 入口阶段将 6 工具注册进工具表，MainTask 的 ReAct 循环只暴露这 6 个签名，模型无法调用表外能力
- file_read：读取指定文件内容供模型审查；file_find：按名称模式定位文件；code_search：在代码库中搜索符号/模式，三者构成读侧能力
- file_read_diff：读取被过滤文件（injectDiffMap 注入）的 diff，实现『主流程过滤但上下文可按需补齐』
- code_comment：模型产出审查意见的唯一出口，调用时强制注入 path（目标文件）与位置，由异步定位组件计算精确行号
- task_done：模型判定审查完成时调用，终止本文件 ReAct 循环，进入 REVIEW_FILTER 反思阶段
- 循环控制：ReAct 每轮先思考再调工具，配合 ConcurrentTaskTimeout 每文件超时与 budget 前瞻，防止单文件死循环或超预算

## 案例 (cases)

- 线上轨迹分析案例：早期版本暴露了写文件/执行命令类工具，轨迹显示模型频繁误用且产出无效评论，收敛到只读 6 工具后 SEM-F1 提升且 token 显著下降
- 幻觉路径案例：模型曾对不存在的文件路径发表评论，code_comment 强制 path 注入后，定位组件校验路径真实性，该类评论在源头被拦截

## 反模式/易错点

- 给审查 Agent 暴露写/执行类工具（如 bash、write_file）——审查是只读场景，写操作只会引入风险，且被线上轨迹证明是 token 浪费源
- 允许模型自由填写评论文件路径——必须由 code_comment 强制注入 path，否则幻觉路径评论直接流入结果
- 无限制的 code_search 返回全量匹配——搜索应限量返回并控制上下文注入，否则一次搜索即可撑爆预算
- 把工具集做成所有场景共用一个超集——应场景化注册（场景化工具集），不同任务注册不同子集，控制决策面

## 相关关系

| 方向 | 类型 | 关系 |
|---|---|---|
| arch-hybrid → arch-grounded-tools | 前置依赖 | Agent 部分由受限工具承担 |
| arch-grounded-tools → eng-locator | 前置依赖 | 工具评论需行号定位 |
| arch-grounded-tools → eng-compression | 前置依赖 | 工具循环需上下文压缩 |
| arch-grounded-tools → arch-pipeline | 组合 | 分派+工具+反思组合成流水线 |
