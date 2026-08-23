# 上下文三区压缩 (Context Compression)

- ID: `eng-compression`
- 类型: 方法机制
- 来源: 审查引擎
- 分组: G-B · 审查引擎
- 阶段: 高级 advanced

> frozen（前 2 条）+ compress（LLM 摘要进 previous_review_summary）+ active（最近 K 轮），60%/80% 双阈值触发

## 核心主张 (what)

- 上下文压缩把会话消息划分为三个区：frozen（messages[0:2] 系统/前置固定区）+ compress 区（可压缩区）+ active 区（最近活动区）
- compress 区由 LLM 摘要为 previous_review_summary，追加进 user 消息以保留审查连续性
- active 区按剩余预算保留最近 K 轮对话，保证当前任务的完整上下文
- 60% 软阈值：后台异步触发压缩，不阻塞审查；80% 警告阈值：同步立即压缩，防止溢出
- 压缩失败时保留原消息，不丢内容；每会话独立 compressionState，防止跨文件互踩

## 为什么 (why)

- 长会话中历史轮次占满上下文窗口，导致当前轮次被截断或模型质量下降
- 分区设计让『必须保留的协议头』（frozen）与『可压缩的历史审查』（compress）分离，结构清晰可预测
- 软/硬双阈值平衡成本与质量：60% 后台异步压缩无感，80% 同步兜底防溢出
- 每会话独立状态避免多文件并行会话共享压缩状态，导致 A 会话压缩污染 B 会话

## 如何实践 (how)

- 会话消息按三区划分：frozen=前 2 条（系统提示等），compress=中间历史区，active=最近对话区
- 触发时机由已用上下文占比决定：达到 60% 软阈值时后台异步执行压缩，不阻塞当前审查
- 达到 80% 警告阈值时同步立即压缩，强制腾出空间防止溢出
- 压缩时 LLM 将 compress 区内容摘要成 previous_review_summary，追加进 user 消息
- active 区按剩余预算保留最近 K 轮消息，其余并入 compress 区
- 压缩失败时保留原始消息列表，不执行破坏性替换，保证审查连续性不中断
- 每个文件会话持有独立 compressionState 实例，互不共享

## 案例 (cases)

- 单文件 30 轮审查后上下文达 60%，后台异步触发摘要，用户无感继续审查
- 超大 diff 审查中上下文冲到 80%，同步压缩立即执行，防止当前请求溢出失败
- 摘要后的 previous_review_summary 让后续轮次仍能引用早期审查结论，保持连续性
- 并行审查 5 个文件会话，各会话独立压缩互不干扰

## 反模式/易错点

- 全量压缩包括 frozen 系统消息，破坏协议前缀导致后续工具调用失效
- 压缩失败后仍执行截断丢弃，违反『失败保留原消息』契约
- 全局共享单一压缩状态，多文件会话互相踩踏（A 的压缩清掉 B 的 active 区）
- 只压缩不保留摘要，审查结论断档，后续轮次无法引用早期决策

## 相关关系

| 方向 | 类型 | 关系 |
|---|---|---|
| arch-grounded-tools → eng-compression | 前置依赖 | 工具循环需上下文压缩 |
| q-token → eng-compression | 前置依赖 | 计费压力驱动压缩设计 |
| eng-compression → q-token | 共现 | 压缩显著降低 token 消耗 |
