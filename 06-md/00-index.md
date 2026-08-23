# Open Code Review 项目解析知识图谱 · AI 友好索引

版本 1.0.0 | 51 节点 | 68 边 | 7 组

## 节点总表

| ID | 名称 | 类型 | 来源 | 阶段 | 分组 | 定义 |
|---|---|---|---|---|---|---|
| arch-hybrid | 确定性工程 × Agent 混合架构 | 方法机制 | 核心架构 | 基础 basic | G-A | 核心设计理念：能工程化保证的环节交给确定性流水线，动态决策交给 LLM Agent，各司其职 |
| arch-pipeline | 审查流水线 | 方法机制 | 核心架构 | 基础 basic | G-A | 从 CLI 入口到评论输出的 8 步确定性+Agent 混合时序：diff→过滤→分派→并行子 Agent→反思→输出 |
| arch-dispatch | 规则引导分派 | 方法机制 | 核心架构 | 进阶 intermediate | G-A | 确定性文件选择/过滤/分束机制：用规则而非语言模型决定审什么、怎么分组 |
| arch-grounded-tools | 受限工具集审查 | 方法机制 | 核心架构 | 进阶 intermediate | G-A | 6 个审查专用工具（file_read/file_find/code_search/file_read_diff/code_comment/task_done）经 ReAct 循环驱动文件级子 Agent |
| arch-reflection | 独立反思 | 方法机制 | 核心架构 | 高级 advanced | G-A | 证伪优先的评论过滤器：只看到 diff 与评论，用 Ground A/B 双地面验证消除幻觉评论 |
| arch-parallel | 文件级并行与上下文隔离 | 方法机制 | 核心架构 | 高级 advanced | G-A | 每文件一个子 Agent 任务、独立上下文，信号量限流（默认 8 并发），防 token 雪球 |
| eng-diff | Git Diff 获取与解析 | 方法机制 | 审查引擎 | 基础 basic | G-B | 三种 diff 来源（workspace/range/commit）+ unified diff 解析器（ParseDiffText/ParseHunks） |
| eng-filter | 文件选择与过滤 | 方法机制 | 审查引擎 | 进阶 intermediate | G-B | whyExcluded 过滤链：binary→用户 exclude→include 覆盖→扩展名白名单→默认路径黑名单 |
| eng-bundling | 文件分束 | 方法机制 | 审查引擎 | 进阶 intermediate | G-B | 将关联文件归并为审查单元（en/zh properties 捆审）；scan 按 by-language/by-directory 分桶，delegate 按规则文本聚簇 |
| eng-locator | 行号定位回退链 | 方法机制 | 审查引擎 | 进阶 intermediate | G-B | 五级回退：hunk 新侧→hunk 旧侧→全文件滑动窗口→跨文件重定位→LLM 重定位，保证评论落在真实行 |
| eng-relocate | 跨文件与 LLM 重定位 | 方法机制 | 审查引擎 | 高级 advanced | G-B | 评论目标代码在别处时：纯字符串匹配迁移（唯一命中才动）+ LLM 从 diff 重生成代码块再定位 |
| eng-compression | 上下文三区压缩 | 方法机制 | 审查引擎 | 高级 advanced | G-B | frozen（前 2 条）+ compress（LLM 摘要进 previous_review_summary）+ active（最近 K 轮），60%/80% 双阈值触发 |
| eng-session | 会话 JSONL 持久化 | 方法机制 | 审查引擎 | 高级 advanced | G-B | ~/.opencodereview/sessions/ 下 JSONL 记录全部任务记录（Plan/Main/压缩/重定位/反思），可回放可审计 |
| eng-resume | 断点续审与指纹复用 | 方法机制 | 审查引擎 | 高级 advanced | G-B | sha256(mode+old+new+diffText) 指纹复用已完成文件评论；SealedInput 冻结 commit 端点防 ref 漂移 |
| eng-manifest | Run Manifest 覆盖度契约 | 方法机制 | 审查引擎 | 高级 advanced | G-B | ocr.run-manifest/v1：注册/封印/完成/失败四态跟踪每文件审查状态，8 类失败分类，预算截断≠运行失败 |
| eng-scan | 全文件扫描引擎 | 方法机制 | 审查引擎 | 高级 advanced | G-B | 无 diff 审查：枚举→过滤→分束→批处理→DEDUP 去重→项目总结，ScanItem 携带全文件内容 |
| cli-overview | ocr 命令总览与安装 | 工具 | 命令行 | 基础 basic | G-C | 安装方式（npm/脚本/二进制/源码）、cobra 命令树、全局参数与 version/completion 子命令 |
| cli-review | ocr review | 工具 | 命令行 | 基础 basic | G-C | 基于 git diff 的审查主命令：workspace/range/commit 三模式，--format text\|json\|sarif，--resume 断点续审 |
| cli-scan | ocr scan | 工具 | 命令行 | 基础 basic | G-C | 全文件扫描：无需 git 历史，--path 指定目录，--batch by-language/by-directory，PLAN/DEDUP/SUMMARY 三阶段 |
| cli-delegate | ocr delegate | 工具 | 命令行 | 进阶 intermediate | G-C | 委托模式：OCR 只做文件选择+规则解析输出 spec JSON，编码 Agent 用自己的 LLM 审查，无需 OCR API Key |
| cli-config | ocr config | 工具 | 命令行 | 基础 basic | G-C | 配置管理：set/unset 键值 + provider/model 交互式 TUI 向导（Bubble Tea），自动测试连通性 |
| cli-session | ocr session | 工具 | 命令行 | 进阶 intermediate | G-C | 会话管理：list/show/comments 子命令，--json 输出，按 severity/category 过滤评论 |
| cli-viewer | ocr viewer | 工具 | 命令行 | 进阶 intermediate | G-C | 本地 WebUI 会话查看器（默认 localhost:5483）：浏览器回放审查会话 JSONL，hostGuard 防 DNS-rebind |
| cli-rules | ocr rules | 工具 | 命令行 | 高级 advanced | G-C | 规则调试：rules check <file> 显示命中规则层（custom/project/global/system）与匹配模式 |
| cli-llm | ocr llm | 工具 | 命令行 | 高级 advanced | G-C | LLM 工具：test 发送测试对话、providers 列出全部 27 个内置 provider |
| cfg-providers | Provider 体系 | 方法机制 | 配置模型 | 基础 basic | G-D | 27 个内置 LLM provider（anthropic/openai/dashscope/deepseek/z-ai/kimi/...）+ 自定义端点，覆盖国内外主流模型 |
| cfg-protocol | LLM 协议层 | 方法机制 | 配置模型 | 进阶 intermediate | G-D | 4 种协议：Anthropic Messages / OpenAI Chat Completions / OpenAI Responses / Bedrock SigV4，统一 CompletionsWithCtx 接口 |
| cfg-priority | 配置优先级 | 方法机制 | 配置模型 | 进阶 intermediate | G-D | 5 级解析：显式 --provider/--model > config.json > OCR_LLM_* 环境变量 > ANTHROPIC_* 环境变量 > shell RC |
| cfg-rules-chain | 四层规则链 | 方法机制 | 配置模型 | 进阶 intermediate | G-D | custom(--rule) > project(.opencodereview/rule.json) > global(~/.opencodereview/rule.json) > system(内嵌)，doublestar glob 匹配 |
| cfg-mcp | MCP 扩展 | 方法机制 | 配置模型 | 高级 advanced | G-D | Model Context Protocol：stdio 子进程 + remote Streamable HTTP 双传输，外部工具接入审查工具链（allowlist 过滤） |
| int-gha | GitHub Actions 集成 | 工具 | 集成生态 | 进阶 intermediate | G-E | composite action（action.yml）：24 入参/6 出参，fork-safe PR 解析，评论发布脚本（sticky/增量 IoU 去重/路由） |
| int-cicd | 其他 CI 集成 | 工具 | 集成生态 | 高级 advanced | G-E | GitLab CI / Gerrit Jenkinsfile / GitFlic CI / Bitbucket Pipelines / 阿里云 Codeup CI + post_review.py 评论回贴 |
| int-claude | Claude Code 插件 | 工具 | 集成生态 | 高级 advanced | G-E | claude-code 插件：/open-code-review:review 与 :delegate-review 斜杠命令，marketplace 安装 |
| int-codex | Codex 插件 | 工具 | 集成生态 | 高级 advanced | G-E | .codex-plugin/plugin.json + skills：以 @Open Code Review review ... 调用，interface Read capability |
| int-cursor | Cursor 插件 | 工具 | 集成生态 | 高级 advanced | G-E | .cursor-plugin/plugin.json + 可移植 skill，复制到 ~/.cursor/plugins/local/ 手动安装 |
| int-opencode | OpenCode 原生插件 | 工具 | 集成生态 | 高级 advanced | G-E | @opencode-ai/plugin：tool() 注册原生审查工具，spawn 'ocr review --audience agent --format json'，参数互斥校验 |
| int-qca | QCA Forward 委托 | 工具 | 集成生态 | 高级 advanced | G-E | QCA 宿主模型运行委托模式：只允许 ocr delegate preview/rule（只读），OCR 侧零 LLM 调用 |
| int-skill | 通用 Agent Skill | 工具 | 集成生态 | 高级 advanced | G-E | skills/open-code-review/SKILL.md：四步 review/filter/fix/report 工作流 + delegate 六步 skill，兼容任意 skill 型 Agent |
| int-vscode | VSCode 扩展 | 工具 | 集成生态 | 高级 advanced | G-E | React webview（侧边栏/配置面板/评论面板）+ CliService 封装，i18n en/zh，webpack+jest |
| q-bench | AACR-Bench 基准 | 工程保障 | 工程保障 | 进阶 intermediate | G-F | 50 仓库/200 真实 PR/10 语言/1505 人工标注问题的审查基准（HuggingFace 开源），驱动 Precision/F1/token 量化优化 |
| q-telemetry | OpenTelemetry 遥测 | 工程保障 | 工程保障 | 高级 advanced | G-F | console/OTLP 双导出（grpc/http），审查事件与指标埋点，OCR_ENABLE_TELEMETRY 环境变量开启 |
| q-security | 安全设计 | 工程保障 | 工程保障 | 高级 advanced | G-F | 路径穿越防护（WithinBase+EvalSymlinks）、git grep 拒 '..'、viewer hostGuard 防 DNS-rebind、manifest 哈希不含密钥 |
| q-retry | 重试与错误分类 | 工程保障 | 工程保障 | 高级 advanced | G-F | SDK 内建 max-retries=5 + 可配置 RetryCodes；错误按 ErrorClass(timeout/cancelled/network/provider/unknown)+FailurePhase 分类入报告 |
| q-release | 构建与发布体系 | 工程保障 | 工程保障 | 高级 advanced | G-F | npm 包（6 平台 optionalDependencies）+ GitHub Release 二进制 + install.sh/ps1，Makefile 覆盖率 90% 门禁 |
| q-token | Token 计费与成本控制 | 工程保障 | 工程保障 | 进阶 intermediate | G-F | tiktoken-go 计费（o200k/cl100k_base），预算前瞻截断、80% token 大文件丢弃、prompt-cache 亲和键命中前缀缓存 |
| use-pr-review | 场景：审查 PR/分支变更 | 场景索引 | 使用场景 | 基础 basic | G-S | 日常审查入口：合并基准模式审 feature 分支、单 commit 审查、GitHub PR 上自动触发 |
| use-scan-codebase | 场景：审计陌生代码库 | 场景索引 | 使用场景 | 基础 basic | G-S | 无 git 历史/无有意义 diff 时：全文件扫描，按语言/目录分束，DEDUP 去重，项目级总结 |
| use-no-key | 场景：免 Key 委托审查 | 场景索引 | 使用场景 | 进阶 intermediate | G-S | 没有 LLM API Key 或想用宿主 Agent 模型：ocr delegate preview/rule 输出 spec，编码 Agent 自己审 |
| use-ci | 场景：接入 CI 流水线 | 场景索引 | 使用场景 | 进阶 intermediate | G-S | 让审查自动跑在每个 MR/PR：GitHub Actions 一步复用、GitLab/Gerrit 等加 post_review.py 回贴评论 |
| use-configure | 场景：配置模型与规则 | 场景索引 | 使用场景 | 进阶 intermediate | G-S | 首次上手必做：选 provider/模型/API Key，按项目定制规则（rule.json）、过滤路径、调并发与预算 |
| use-extend | 场景：扩展审查能力 | 场景索引 | 使用场景 | 高级 advanced | G-S | 规则不够用？MCP 接入外部工具、自定义规则文件、--rule 临时规则、委托模式喂给任意 Agent |
