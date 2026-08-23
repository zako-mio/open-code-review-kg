# 会话 JSONL 持久化 (Session Persistence)

- ID: `eng-session`
- 类型: 方法机制
- 来源: 审查引擎
- 分组: G-B · 审查引擎
- 阶段: 高级 advanced

> ~/.opencodereview/sessions/ 下 JSONL 记录全部任务记录（Plan/Main/压缩/重定位/反思），可回放可审计

## 核心主张 (what)

- 会话持久化把每次代码审查的完整执行轨迹以 JSONL 落盘，默认目录 ~/.opencodereview/sessions/
- GetOrCreateFileSession(newPath) 按文件路径建立独立会话文件，一文件一会话
- AppendTaskRecord 记录 Plan/Main/MemoryCompression/ReLocation/ReviewFilter 等任务类型的事件
- session_end 事件落盘标记会话正常结束
- 会话可回放、可审计：任何一次审查都能重建执行过程

## 为什么 (why)

- 审查过程可审计：企业级代码审查需要知道每条评论怎么来的、走了哪条定位链、用了多少轮
- 支持断点续审：JSONL 会话记录是 --resume 恢复执行的基础数据源
- 故障排查：LLM 超时、定位失败、压缩事故都能从会话记录还原现场
- 一文件一会话保证并行审查互不串扰，且单文件会话文件增长可控

## 如何实践 (how)

- 会话文件位于 ~/.opencodereview/sessions/，按文件路径派生（GetOrCreateFileSession(newPath)）
- 会话生命周期内所有关键任务通过 AppendTaskRecord 追加 JSONL 行，任务类型包括 Plan（规划）、Main（主审查）、MemoryCompression（记忆压缩）、ReLocation（重定位）、ReviewFilter（评论过滤）
- 会话结束时写入 session_end 记录并落盘，标识完整生命周期
- 回放时逐行读取 JSONL 重建任务时序与决策过程
- 审计时可按任务类型过滤查询，如只查所有 ReLocation 事件

## 案例 (cases)

- 审查结束后 3 天复盘，回放 JSONL 确认某条评论经历了三级定位回退才落位
- 线上会话崩溃后读取 JSONL 恢复现场，通过 session_end 缺失定位崩溃点
- 用 --resume 读取旧会话，跳过已完成指纹任务直接续审未决项
- 审计团队过滤 ReviewFilter 事件统计被过滤掉的低质量评论数量

## 反模式/易错点

- 多文件共用单一会话文件，并行审查事件交错，无法还原单文件时序
- 会话结束不写 session_end，回放时无法区分『正常结束』与『中断』
- 只记结果不记过程（跳过 Plan/ReLocation 等中间任务），审计失去意义
- 内存缓冲未落盘即结束，崩溃后会话数据全丢

## 相关关系

| 方向 | 类型 | 关系 |
|---|---|---|
| eng-session → eng-resume | 前置依赖 | 续审依赖会话持久化 |
| eng-session → eng-manifest | 前置依赖 | manifest 随会话落盘 |
| eng-session → cli-session | 前置依赖 | CLI 管理 JSONL 会话 |
| eng-session → cli-viewer | 前置依赖 | 查看器回放 JSONL |
| q-telemetry → eng-session | 共现 | 会话 JSONL 是遥测素材 |
| cli-review → eng-session | 依赖关联 | review 产生会话记录 |
| cli-scan → eng-session | 依赖关联 | scan 也写会话（无 manifest） |
