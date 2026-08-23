# Run Manifest 覆盖度契约 (Run Manifest)

- ID: `eng-manifest`
- 类型: 方法机制
- 来源: 审查引擎
- 分组: G-B · 审查引擎
- 阶段: 高级 advanced

> ocr.run-manifest/v1：注册/封印/完成/失败四态跟踪每文件审查状态，8 类失败分类，预算截断≠运行失败

## 核心主张 (what)

- Run Manifest 是审查运行的覆盖度契约，声明本次审查覆盖了哪些项、每项什么状态、哪些失败，schema 标识为 'ocr.run-manifest/v1'
- 提供 RegisterSelected/SealSelected/MarkCompleted/Reused/Failed 等操作登记任务生命周期
- FailureClass 分 8 类，实现精细化失败归因
- SetRunFailure 与 SetPendingFailureCause 语义分离：预算截断（pending）≠ 运行失败（failure）
- Finalize 冻结 input/repository/coverage，形成不可变快照
- scan 模式无 manifest 属设计行为，非缺陷

## 为什么 (why)

- 审查工具必须能回答『这次审查到底完整吗』，manifest 是覆盖度的单一事实源
- 8 类 FailureClass 让失败可机器归因（超时/上下文溢出/LLM 错误等），支撑自动重试与审计
- pending（预算截断）与 failure 分离，避免把『没审完』误判为『审坏了』
- Finalize 冻结快照保证审计时引用的输入与产出严格一致

## 如何实践 (how)

- 运行开始时通过 RegisterSelected 登记被选中的评审项，SealSelected 封存选定集合
- 每项完成后调用 MarkCompleted/Reused/Failed 更新状态，形成逐项覆盖度台账
- 失败按 FailureClass 8 类归因，如 LLM 调用失败、上下文截断、定位失败、超时等
- 预算截断类情况用 SetPendingFailureCause 记录未决原因，区别于 SetRunFailure 的整体运行失败
- 全部任务结束后 Finalize 冻结 input/repository/coverage 三元快照，落盘为不可变记录
- scan 模式因无逐项评审任务，按设计不产出 manifest

## 案例 (cases)

- 运行中 3 项因上下文溢出失败，manifest 记为 failed（类：上下文溢出），重试时精确重跑这 3 项
- 预算只够审 80 项中的 60 项，剩余 20 项记为 pending（SetPendingFailureCause），不污染失败统计
- 审计时读取 Finalize 快照，确认 coverage 与 input 严格对应
- 复用评论的条目 MarkReused，覆盖度统计中明确区分『新审』与『复用』

## 反模式/易错点

- 把预算截断的 pending 项标记为 failed，覆盖度报告失真，误导重试与统计
- 跳过 Finalize 不冻结快照，后续审计无法确认输入与产出的对应关系
- 失败不按 FailureClass 归因而只记布尔值，机器无法自动分类重试
- 在 scan 模式强造 manifest，破坏『scan 无 manifest』的设计契约

## 相关关系

| 方向 | 类型 | 关系 |
|---|---|---|
| eng-session → eng-manifest | 前置依赖 | manifest 随会话落盘 |
| eng-manifest → eng-resume | 前置依赖 | 复用必须过父 manifest |
