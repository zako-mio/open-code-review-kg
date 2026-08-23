# Token 计费与成本控制 (Token Accounting & Cost)

- ID: `q-token`
- 类型: 工程保障
- 来源: 工程保障
- 分组: G-F · 工程保障
- 阶段: 进阶 intermediate

> tiktoken-go 计费（o200k/cl100k_base），预算前瞻截断、80% token 大文件丢弃、prompt-cache 亲和键命中前缀缓存

## 核心主张 (what)

- 基于 tiktoken-go 精确计费：o1/o3/o4 系列用 o200k_base，其余模型用 cl100k_base，分词口径与 OpenAI 一致
- estimate.go 提供 token 预估与预算前瞻：审查前估算输入 token 量，预判是否超出模型上下文与成本预算
- filterLargeDiffs 自动丢弃超过 MaxTokens 80% 的超大文件 diff，防止单文件撑爆上下文
- 三区压缩策略：对超大输入分区压缩，显著降低送入模型的 token 总量
- prompt-cache affinity key 设计：按（会话+任务+文件）组合生成缓存键，命中 provider 前缀缓存后 input 成本节省约 98%
- 端到端对比通用 Agent，同样审查任务 token 消耗节省 5-15 倍

## 为什么 (why)

- token 即成本，审查任务动辄处理整个 diff，无预算控制会产生不可控账单
- 超大 diff 塞入模型不仅贵，还会稀释注意力导致审查质量下降，丢弃 80% 阈值之上的文件是质量与成本的双赢
- 前缀缓存命中与否直接决定 input 成本量级（约 98% 差异），affinity key 让重复/相似任务尽量复用缓存

## 如何实践 (how)

- 默认策略即可享受收益：filterLargeDiffs 与三区压缩自动生效，无需配置
- 关注预算：审查前查看 estimate.go 输出的 token 预估，判断本次任务的成本量级
- 最大化缓存命中：保持会话与任务结构稳定（同一仓库同一文件多次审查），让 prompt-cache affinity key 命中 provider 前缀缓存
- 按模型选口径：使用 o1/o3/o4 时确认计费走 o200k_base，其余模型确认 cl100k_base，避免计费误判
- 结合遥测验证：在 metric 中观察 token 计数与缓存命中率，量化节省效果并发现异常增长

## 案例 (cases)

- 超大 PR 审查：一个 2000 行文件被 filterLargeDiffs 自动跳过，审查继续进行而非整体失败，成本可控
- 重复审查同一分支：第二次运行命中前缀缓存，input token 成本骤降至约 2%
- 多模型对比：用预估工具对比不同模型的 token 消耗，选择性价比最高的审查模型
- 成本审计：月末按 metric 的 token 计数核对账单，确认无异常放大

## 反模式/易错点

- 忽视 80% 阈值丢弃：以为『审查不完整』而调高阈值甚至禁用 filterLargeDiffs，导致成本与质量双双恶化
- 频繁变更 prompt 前缀（改系统提示/顺序），破坏前缀缓存命中，让 98% 的节省归零
- 用 cl100k_base 口径估算 o1 系列任务，token 数量与账单对不上，影响预算决策
- 在长会话中堆积无关上下文，压缩与缓存机制失效，实际 token 远超预估

## 相关关系

| 方向 | 类型 | 关系 |
|---|---|---|
| q-token → eng-compression | 前置依赖 | 计费压力驱动压缩设计 |
| eng-compression → q-token | 共现 | 压缩显著降低 token 消耗 |
