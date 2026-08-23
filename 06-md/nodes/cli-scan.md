# ocr scan (ocr scan)

- ID: `cli-scan`
- 类型: 工具
- 来源: 命令行
- 分组: G-C · 命令行工具
- 阶段: 基础 basic

> 全文件扫描：无需 git 历史，--path 指定目录，--batch by-language/by-directory，PLAN/DEDUP/SUMMARY 三阶段

## 核心主张 (what)

- ocr scan 是全文件扫描模式，不依赖 git 历史与 diff，直接对磁盘上的源码文件逐个审查，覆盖 review 模式无法触及的历史遗留问题
- 裸运行 ocr scan 扫描整个仓库；--path <path> 可指定目录或文件缩小范围（如 ocr scan --path internal/agent）
- 分批策略由 --batch 控制：none（不分批）、by-language（按语言分批）、by-directory（按目录分批），默认按语言/目录自动分批以控制单轮上下文与成本
- 执行分三阶段：PLAN（制定扫描计划）、DEDUP（跨文件去重，避免重复问题重复报告）、PROJECT_SUMMARY（项目级汇总）
- 支持 --no-plan / --no-dedup / --no-summary 分别跳过对应阶段，便于针对性调试或控制耗时
- 支持 --resume 断点续审，配合 session 机制在中断后恢复

## 为什么 (why)

- 陌生代码库往往没有可用的 git 历史或当前无变更，review 的 diff 驱动模型无从下手，scan 的全文件模式是审计陌生代码库的入口
- 按语言/目录分批（--batch）可以控制每次扫描的上下文规模与 token 成本，大仓库不至于单次调用爆掉
- 三阶段流水线（计划/去重/汇总）保证扫描有序、结果无重复、结论有全局视角，而非零散问题列表

## 如何实践 (how)

- 扫描整个仓库：ocr scan
- 扫描指定目录或文件：ocr scan --path internal/agent 或 ocr scan --path internal/agent/main.go
- 按语言分批：ocr scan --batch by-language
- 按目录分批：ocr scan --batch by-directory
- 不分批全量扫描：ocr scan --batch none
- 跳过计划阶段直接扫描：ocr scan --no-plan
- 关闭去重看原始命中：ocr scan --no-dedup
- 跳过项目汇总只出单文件问题：ocr scan --no-summary
- 中断后续扫：ocr scan --resume <session-id>

## 案例 (cases)

- 接手遗留系统摸底：新团队拿到无历史记录或 git 历史被裁剪的代码库，直接 ocr scan 全量扫描，快速得到问题全貌与项目级汇总
- 指定模块深度审查：只关心某个模块时 ocr scan --path internal/agent --batch none，避免全仓噪音
- 大仓库预算控制：先 ocr scan --path 逐目录分批扫，或 --batch by-directory 由工具自动分批，每批结束后评估问题再决定是否扩范围
- 中断恢复：长扫描被网络/断电打断后，ocr scan --resume 从断点继续，不重复消耗已完成的批次

## 反模式/易错点

- 大仓库直接默认全量扫描：上下文与 token 预算被撑爆、耗时超长，应先 --path 收窄范围或显式 --batch 分批，再逐步扩大
- 关闭去重（--no-dedup）后把重复问题当新问题处理：跨文件相似代码会被重复报告，处理问题时须结合 DEDUP 阶段的去重信息合并同类项
- 中断后弃用 --resume 重跑全量：已完成的批次全部重扫，token 与时间双倍浪费，应始终用 --resume 续扫
- 把 scan 当增量审查日常使用：scan 是全文件模式，每次都是全量成本，日常增量审查应使用 ocr review（diff 驱动）

## 相关关系

| 方向 | 类型 | 关系 |
|---|---|---|
| eng-scan → cli-scan | 前置依赖 | scan 命令由扫描引擎驱动 |
| cli-overview → cli-scan | 前置依赖 | 安装后学 scan |
| cli-scan → use-scan-codebase | 前置依赖 | 代码库审计指向 scan 命令 |
| cli-review → cli-scan | 变体 | 两种审查模式互为变体 |
| cli-scan → eng-session | 依赖关联 | scan 也写会话（无 manifest） |
