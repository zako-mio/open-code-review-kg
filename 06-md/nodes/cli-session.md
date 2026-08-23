# ocr session (ocr session)

- ID: `cli-session`
- 类型: 工具
- 来源: 命令行
- 分组: G-C · 命令行工具
- 阶段: 进阶 intermediate

> 会话管理：list/show/comments 子命令，--json 输出，按 severity/category 过滤评论

## 核心主张 (what)

- ocr session 是会话管理命令，管理审查任务的持久化会话，会话数据定位在 ~/.opencodereview/sessions/ 目录
- 子命令 list：列出历史会话，支持 --json 结构化输出、--limit 控制条数（默认 20）、--repo 按仓库过滤
- 子命令 show：查看单个会话的详情
- 子命令 comments：查看会话的审查评论，支持 --json 输出及 --severity（严重级别）、--category（类别）过滤
- 会话机制与 ocr review --resume 联动，实现断点续审：长审查中断后可恢复，无需从头开始

## 为什么 (why)

- AI 审查是长耗时、高成本任务（大仓库可达数十分钟与大量 token），会话持久化使中断可恢复，避免重复消耗
- 历史会话是审查过程与结果的审计记录，list/show/comments 支持回看、统计与按仓库筛选，便于团队复盘
- review 后台模式（--background）产出的进度与结果都落在会话中，session 是查看后台任务状态的统一入口

## 如何实践 (how)

- 列出会话：ocr session list
- JSON 输出：ocr session list --json
- 控制条数与过滤：ocr session list --limit 50、ocr session list --repo <repo-name>
- 查看会话详情：ocr session show <session-id>
- 查看评论：ocr session comments <session-id>
- 过滤评论：ocr session comments <session-id> --severity high 或 ocr session comments <session-id> --category <category>
- 断点续审：ocr review --resume <session-id>，从上次中断处继续
- 配合后台审查：ocr review --background 启动后，用 ocr session list 观察会话状态与完成度

## 案例 (cases)

- 长审查中断恢复：大仓库 review 中途断网，ocr session list 找到会话后用 ocr review --resume <session-id> 续审，已消耗的 token 不浪费
- 按仓库回溯：一周内审了多个仓库，ocr session list --repo <repo> 只看目标仓库的审查记录
- 高严重度问题收敛：ocr session comments <session-id> --severity high --json 导出高危评论集中修复与上报
- 后台任务跟踪：--background 启动后定期 ocr session list 查看进度，完成后 show/comments 取结果

## 反模式/易错点

- 依赖默认 limit 20 以为会话丢失：会话多于 20 条时 list 默认只显示前 20，找不到旧会话应先 --limit 放大或 --repo 过滤，而不是以为被清理
- 随手清理 ~/.opencodereview/sessions/ 目录：误删会话文件后 --resume 失效、历史评论不可查，删除前应确认无续审与审计需求
- 混淆 show 与 comments 的用途：show 看会话整体详情，comments 看具体评论，二者输出不同，用错命令会漏掉评论或拿不到过程信息

## 相关关系

| 方向 | 类型 | 关系 |
|---|---|---|
| eng-session → cli-session | 前置依赖 | CLI 管理 JSONL 会话 |
| cli-session → cli-viewer | 变体 | 会话管理 CLI 与 Web 查看器 |
