# 全文件扫描引擎 (Scan Engine)

- ID: `eng-scan`
- 类型: 方法机制
- 来源: 审查引擎
- 分组: G-B · 审查引擎
- 阶段: 高级 advanced

> 无 diff 审查：枚举→过滤→分束→批处理→DEDUP 去重→项目总结，ScanItem 携带全文件内容

## 核心主张 (what)

- 全文件扫描引擎实现无 diff 审查：不依赖 git diff，对仓库全量文件内容做审查
- Run 时序：Enumerate→filterScanItems→filterLargeScans→dispatchSubtasks（按 batch）→maybeRunProjectSummary→WaitBackground→Finalize
- ScanItem 携带全文件 Content，供模型基于全文审查
- DiffLookup 返回合成 Diff：NewFileContent=全文、Diff 为空，使 resolveFromFileContent 路径生效
- 额外存在 DEDUP_TASK（CommentCollector.Snapshot/Since/ReplaceSince 批次级去重）与 PROJECT_SUMMARY_TASK
- Provider.Enumerate 用 git ls-files + 未跟踪文件列举，2MiB 大小上限，8000 字节内容嗅探

## 为什么 (why)

- 新仓库/未提交场景没有 diff 可审，全文件扫描是唯一可行的审查入口
- 全文件内容让模型看到完整上下文，能发现跨函数/跨文件的逻辑问题（diff 模式看不到未改动区域）
- 合成 Diff 复用同一套解析管线，无需为 scan 单独实现定位逻辑
- DEDUP_TASK 解决批次重复生成相同评论的问题；PROJECT_SUMMARY_TASK 提供项目级整体结论

## 如何实践 (how)

- Enumerate 枚举仓库文件：git ls-files 列出跟踪文件 + 未跟踪文件，共同构成扫描候选集
- filterScanItems 过滤无需扫描的项，filterLargeScans 剔除超大文件（2MiB 上限）
- 内容嗅探：8000 字节取样判断文件类型/可审性，跳过二进制等不可审内容
- 每个 ScanItem 携带全文件 Content 进入子任务，按 batch 经 dispatchSubtasks 分发
- DiffLookup 为扫描项返回合成 Diff（NewFileContent=全文、Diff 为空），使 resolveFromFileContent 生效，行号定位直接基于全文
- 批次级 DEDUP_TASK 通过 CommentCollector.Snapshot/Since/ReplaceSince 对重复评论去重
- maybeRunProjectSummary 视条件触发 PROJECT_SUMMARY_TASK 生成项目级总结，最后 WaitBackground 等待后台任务后 Finalize

## 案例 (cases)

- 全新仓库首次审查无 git 历史，scan 模式全量枚举并逐文件审查
- 仓库含 3 个 5MB 大文件被 filterLargeScans 剔除，其余文件正常扫描
- 多个子任务对同一代码模式给出重复评论，DEDUP_TASK 批次级去重只保留一条
- 未跟踪的新文件被 Enumerate 纳入扫描范围，提交前就能被审查

## 反模式/易错点

- 把 scan 模式当 diff 模式用，期待行号定位基于 diff 行号而非全文（合成 Diff 语义不同）
- 忘记 2MiB 上限，超大文件直接进子任务拖垮上下文
- 忽略 8000 字节嗅探，二进制文件被当文本扫描产出垃圾评论
- 不做 DEDUP_TASK 去重，批次重复评论成倍污染最终结果

## 相关关系

| 方向 | 类型 | 关系 |
|---|---|---|
| eng-scan → cli-scan | 前置依赖 | scan 命令由扫描引擎驱动 |
