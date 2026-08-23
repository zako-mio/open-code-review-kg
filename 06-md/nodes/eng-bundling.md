# 文件分束 (File Bundling)

- ID: `eng-bundling`
- 类型: 方法机制
- 来源: 审查引擎
- 分组: G-B · 审查引擎
- 阶段: 进阶 intermediate

> 将关联文件归并为审查单元（en/zh properties 捆审）；scan 按 by-language/by-directory 分桶，delegate 按规则文本聚簇

## 核心主张 (what)

- 文件分束是 open-code-review 将一次评审拆解为多个可并行子任务的核心调度机制，决定 diff/文件集合如何被组织成独立任务单元
- review 模式（基于 diff 审查）默认采用『每文件一个子任务』策略，即每个改动文件独立成为一个审查任务单元
- 分束决策发生在 scan 阶段：通过 BatchStrategy 策略枚举，将文件按规则分桶（bucket），再切块生成子任务
- 支持三种分桶策略：none（不分桶，整体作为单一任务）、by-language（按小写扩展名分桶，如 .go/.py/.ts）、by-directory（按首层目录分桶）
- 分桶后按 key 排序保证确定性输出，同一输入集合任何时候产生相同任务序列，为指纹复用与断点续审奠定基础
- 按 BatchSize 对桶内文件切块形成最终批次；delegate 模式则改用 (source\|pattern\|text) 三元组聚簇规则组织任务

## 为什么 (why)

- 单文件一任务保证每个子任务的上下文最小且聚焦，避免超大 diff 超出模型上下文窗口
- 分桶+排序提供确定性：任务划分可复现，是 reviewItemFingerprint 指纹复用、断点续审、审计回放的前提
- 按语言/目录分桶让同类型代码集中审查，便于共享审查规则与领域提示词，提高审查质量与并行度
- delegate 模式按三元组聚簇，是因为该模式面向『指定源码/模式/文本』的定向审查，任务粒度由调用方语义决定而非文件边界

## 如何实践 (how)

- 在 scan 流程中通过 BatchStrategy 决定分桶方式，例如 by-language 策略读取文件扩展名并转小写作为桶 key（.GO 与 .go 归入同一桶）
- by-directory 策略取文件路径的首层目录作为桶 key，跨目录文件分别成桶
- 桶内按 key 字典序排序，保证任务序列确定性，不依赖文件系统遍历顺序
- 排序后的桶内文件按 BatchSize 切块，生成 dispatchSubtasks 可消费的批次列表
- review 模式默认每文件一个子任务，配合并行 worker 分发执行
- delegate 模式不走文件分桶，按 (source\|pattern\|text) 三元组聚簇同类委托请求合并成批次
- 分束结果直接喂给后续的 dispatchSubtasks 与 WaitBackground 时序，构成完整执行链

## 案例 (cases)

- 一次 PR 改动 30 个 Go 文件，by-language 策略下全部归入 .go 桶，按 BatchSize=10 切成 3 个批次子任务并行审查
- 前后端同仓改动，by-directory 策略将 frontend/ 与 backend/ 下文件分别成桶，各自独立审查避免上下文混杂
- delegate 模式下对同一源码文件的不同 pattern 请求聚簇为同一任务组，减少重复读取与审查开销
- 扩展名大小写混用（.GO/.go）时，小写归一化保证同语言文件不分家

## 反模式/易错点

- 选择 none 策略直接审查超大仓库，导致单任务上下文溢出或审查质量急剧下降
- 依赖 map 迭代等非确定顺序生成任务而非显式 key 排序，破坏确定性，使指纹复用与断点续审失效
- 把 delegate 的三元组聚簇与 review 的文件分桶混为一谈，错误设计任务组织逻辑
- 忽略 BatchSize 上限，单批次塞入过多文件，导致单任务超时或超出上下文窗口

## 相关关系

| 方向 | 类型 | 关系 |
|---|---|---|
| arch-dispatch → eng-bundling | 前置依赖 | 分派再做文件分束 |
| eng-bundling → cli-delegate | 前置依赖 | 委托模式按规则文本分束 |
| eng-bundling → arch-dispatch | 组合 | 选择+分束组合成分派 |
