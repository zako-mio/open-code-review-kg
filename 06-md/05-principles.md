# 12 Factor 原则 × Open Code Review 对照审查

> 审查标尺：12 Factor App + 12 Factor Agent 合并图谱的 24 条原则（来源：0823-12factor-methodology）。

## 12 Factor App 原则

| 原则 | 主张 | OCR 对应机制 | 结论 |
|---|---|---|---|
| app-codebase | 一个代码库，多环境部署，版本控制跟踪一切 | 单仓库 monorepo（alibaba/open-code-review），Git 版本控制跟踪一切；图谱资产化：关键源码节选进 assets/code/ 供离线研读 | **合规** |
| app-deps | 显式声明并隔离依赖，绝不依赖系统级隐式包 | go.mod 显式声明全部 Go 依赖（cobra/anthropic-sdk-go/openai-go/MCP go-sdk/otel），npm 侧 optionalDependencies 按平台隔离原生二进制 | **合规** |
| app-config | 配置存于环境变量，与代码严格分离 | 5 级配置优先级（--flag > config.json > OCR_LLM_* 环境变量 > ANTHROPIC_* > shell RC），密钥走 env/api_key_cmd 不进代码 | **合规** |
| app-backing | 后端服务作为附加资源，可随时替换连接 | 27 内置 provider + custom_providers 自定义端点：LLM 服务是纯附加资源，切换 provider 只改配置不改代码 | **合规** |
| app-build-run | 严格分离构建、发布、运行三阶段 | Makefile build/test/coverage 门禁 → GitHub Release 产物 + npm 包 → 安装脚本/自动更新（update.js 18 分钟冷却）三阶段分离 | **合规** |
| app-processes | 以一个或多个无状态进程执行应用 | 审查子任务无状态化：每文件独立上下文、独立超时、panic 隔离、manifest 状态外置（可重放可续跑） | **合规** |
| app-port | 通过端口绑定自含导出服务，不依赖注入的 Web 服务器 | ocr viewer 自含 WebUI（默认 localhost:5483），Go 内嵌 HTTP 服务，无外部 Web 服务器依赖 | **合规** |
| app-concurrency | 通过进程模型横向扩展 | 文件级并行：semaphore 默认 8 并发 goroutine，每文件独立任务单元，横向扩展审查吞吐 | **合规** |
| app-disposability | 快速启动与优雅终止，最大化鲁棒性 | 审查可中断可恢复：SealedInput 冻结 commit 端点、JSONL 会话持久化、--resume 断点续审、预算截断记 pending 而非失败 | **合规** |
| app-dev-prod | 保持开发、预发布、生产环境尽可能相似 | 同一 ocr 二进制跑本地与 CI（ocr_version 固定 latest 可锁版本）；OCR_* 环境变量在 CI/本地一致生效 | **部分合规** |
| app-logs | 将日志视为事件流，不关心存储格式 | 会话 JSONL 即事件流（Plan/Main/压缩/重定位/反思任务记录）+ OpenTelemetry trace/metric 双管道 | **合规** |
| app-admin | 管理/维护任务作为一次性进程运行 | ocr delegate（委托审查）/ ocr scan（整库扫描）/ ocr session comments（审计导出）均一次性命令形态 | **合规** |

## 12 Factor Agent 原则

| 原则 | 主张 | OCR 对应机制 | 结论 |
|---|---|---|---|
| ag-nl2tool | LLM 将自然语言转换为结构化工具调用对象 | 受限 6 工具 ReAct 循环：模型输出结构化工具调用（file_read/file_find/code_search/file_read_diff/code_comment/task_done） | **合规** |
| ag-prompts | 像管理代码一样版本化、测试、部署 prompt | 场景化提示词模板（internal/config/template/prompts/）随仓库版本化，图谱资产化（assets/prompts/），plan/main/filter 相位分离 | **合规** |
| ag-context | 对上下文进行工程化管理（上下文工程） | 三区压缩（frozen/compress/active 60%/80% 阈值）+ 预算前瞻（estimate.go）+ filterLargeDiffs 80% 丢弃 + prompt-cache 亲和键 | **合规** |
| ag-tools | 工具只是模型的结构化输出，可无限组合 | tools.json 定义 schema，工具注册表 Registry + MCP 动态工具扩展（ToToolDef 统一转换） | **合规** |
| ag-state | 将执行状态与业务状态统一为单一事实源 | Run Manifest（ocr.run-manifest/v1）作为覆盖度单一事实源 + JSONL 会话作为执行轨迹事实源 | **合规** |
| ag-pause | 用简单 API 管理 Agent 生命周期 | ocr review --resume <session-id> / ocr scan --resume：指纹复用跳过已完成，未决项重跑 | **合规** |
| ag-human | 把人类接入作为一类工具调用，主动寻求批准 | --audience human\|agent 双受众输出 + CI 评论回贴（GitHub/GitLab discussion）将审查结论送到人类面前 | **部分合规** |
| ag-control | 控制流由代码决定，LLM 只做决策点 | 确定性流水线（8 步时序）+ 规则引导分派（四层规则链）决定控制流，LLM 只在『看 diff 出评论』决策点工作 | **合规** |
| ag-errors | 把错误摘要压缩回上下文窗口供模型反思 | q-retry 错误分类（ErrorClass × FailurePhase）+ retry_report 压缩重试明细；LLM 调用失败结构化入报告而非原始堆栈 | **合规** |
| ag-small | 用多个小 Agent 而非一个巨型 Agent 解决问题 | 文件级子 Agent：每文件独立 Plan+ReAct+反思，8 并发，上下文隔离——多个小 Agent 而非一个巨型 Agent | **合规** |
| ag-trigger | 从任何触发源唤起 Agent，触达用户所在之处 | GitHub PR 事件/评论触发、GitLab MR、Gerrit、斜杠命令（Claude Code）、skill（Codex/Cursor/OpenCode）、VSCode 面板 | **合规** |
| ag-reducer | 将 Agent 建模为无状态 reducer（state, event）→ state | reviewItemFingerprint=sha256(mode+old+new+diffText) + manifest 状态机：同输入同指纹同结果，事件流可重放（JSONL 回放） | **合规** |
