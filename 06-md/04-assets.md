# 实践资产索引

| ID | 类型 | 名称 | 路径 | 关联节点 |
|---|---|---|---|---|
| asset-00 | CI 集成 | github_actions-ocr-review.yml | `assets/ci/github_actions-ocr-review.yml` | `int-gha`, `use-pr-review`, `use-ci` |
| asset-01 | CI 集成 | gitlab-ci.yml | `assets/ci/gitlab-ci.yml` | `int-cicd`, `use-ci` |
| asset-02 | CI 集成 | gerrit-Jenkinsfile | `assets/ci/gerrit-Jenkinsfile` | `int-cicd` |
| asset-03 | CI 集成 | codeup-flow.yml | `assets/ci/codeup-flow.yml` | `int-cicd` |
| asset-04 | CI 集成 | gitflic-ci.yaml | `assets/ci/gitflic-ci.yaml` | `int-cicd` |
| asset-05 | CI 集成 | bitbucket-pipelines.yml | `assets/ci/bitbucket-pipelines.yml` | `int-cicd` |
| asset-06 | CI 集成 | action.yml | `assets/ci/action.yml` | `int-gha`, `use-ci`, `q-bench` |
| asset-07 | 脚本 | post-review-comments.js | `assets/scripts/post-review-comments.js` | `int-gha` |
| asset-08 | 工具 schema | tools.json | `assets/tools/tools.json` | `arch-grounded-tools`, `cli-review`, `cli-scan`, `cli-delegate`, `eng-bundling` |
| asset-09 | 提示词 | review_filter_task_user.md | `assets/prompts/review_filter_task_user.md` | `arch-reflection` |
| asset-10 | 规则 | system_rules.json | `assets/rules/system_rules.json` | `cfg-rules-chain`, `arch-dispatch`, `eng-bundling`, `cli-rules` |
| asset-11 | 源码节选 | agent.go.md | `assets/code/agent.go.md` | `arch-pipeline`, `arch-dispatch`, `arch-parallel`, `arch-reflection`, `eng-session`, `eng-resume`, `eng-manifest`, `q-retry` |
| asset-12 | 源码节选 | llmloop-loop.go.md | `assets/code/llmloop-loop.go.md` | `arch-grounded-tools`, `eng-compression`, `eng-scan`, `eng-locator` |
| asset-13 | 源码节选 | llmloop-compression.go.md | `assets/code/llmloop-compression.go.md` | `eng-compression` |
| asset-14 | 源码节选 | diff-resolver.go.md | `assets/code/diff-resolver.go.md` | `eng-locator`, `eng-filter`, `cli-review` |
| asset-15 | 源码节选 | diff-relocation.go.md | `assets/code/diff-relocation.go.md` | `eng-relocate` |
| asset-16 | 源码节选 | diff-git.go.md | `assets/code/diff-git.go.md` | `eng-diff` |
| asset-17 | 源码节选 | scan-agent.go.md | `assets/code/scan-agent.go.md` | `eng-scan`, `cli-scan` |
| asset-18 | 源码节选 | session-manifest.go.md | `assets/code/session-manifest.go.md` | `eng-manifest`, `eng-session`, `cli-review`, `cli-scan` |
| asset-19 | 源码节选 | session-resume.go.md | `assets/code/session-resume.go.md` | `eng-resume`, `cli-session` |
| asset-20 | 源码节选 | llm-resolver.go.md | `assets/code/llm-resolver.go.md` | `cfg-priority`, `cli-config`, `cli-llm`, `q-token` |
| asset-21 | 源码节选 | llm-providers.go.md | `assets/code/llm-providers.go.md` | `cfg-providers`, `cli-llm`, `use-configure` |
| asset-22 | 源码节选 | llm-protocol.go.md | `assets/code/llm-protocol.go.md` | `cfg-protocol` |
| asset-23 | 源码节选 | mcp-client.go.md | `assets/code/mcp-client.go.md` | `cfg-mcp` |
| asset-24 | 源码节选 | viewer-server.go.md | `assets/code/viewer-server.go.md` | `cli-viewer`, `q-security`, `eng-session`, `use-pr-review` |
| asset-25 | 源码节选 | telemetry-provider.go.md | `assets/code/telemetry-provider.go.md` | `q-telemetry`, `eng-session` |
| asset-26 | 源码节选 | gitcmd-runner.go.md | `assets/code/gitcmd-runner.go.md` | `eng-diff`, `eng-scan`, `arch-parallel` |
| asset-27 | Skill | SKILL-review.md | `assets/skills/SKILL-review.md` | `int-skill`, `use-no-key`, `use-scan-codebase` |
| asset-28 | Skill | SKILL-delegate.md | `assets/skills/SKILL-delegate.md` | `int-skill`, `cli-delegate`, `use-extend` |
| asset-29 | 插件 | opencode-plugin.ts | `assets/plugins/opencode-plugin.ts` | `int-opencode`, `use-scan-codebase` |
| asset-30 | 插件 | claude-slash-command.md | `assets/plugins/claude-slash-command.md` | `int-claude` |
| asset-31 | 构建发布 | Makefile | `assets/build/Makefile` | `q-release` |
| asset-32 | 构建发布 | install.sh | `assets/build/install.sh` | `cli-overview`, `q-release` |
| asset-33 | 构建发布 | install.ps1 | `assets/build/install.ps1` | `cli-overview`, `q-release` |
| asset-34 | 构建发布 | package.json | `assets/build/package.json` | `q-release`, `cli-overview` |
| asset-35 | 构建发布 | go.mod | `assets/build/go.mod` | `q-release` |
| asset-36 | 文档 | README.zh-CN.md | `assets/doc/README.zh-CN.md` | `cli-overview`, `arch-hybrid`, `int-vscode` |
| asset-37 | 插件 | codex-plugin.json | `assets/plugins/codex-plugin.json` | `int-codex` |
| asset-38 | 插件 | cursor-plugin.json | `assets/plugins/cursor-plugin.json` | `int-cursor` |
| asset-39 | 插件 | qca-system-prompt.md | `assets/plugins/qca-system-prompt.md` | `int-qca` |
| asset-40 | 配置示例 | rule.example.json | `assets/configs/rule.example.json` | `cfg-rules-chain`, `use-configure`, `use-extend` |
| asset-41 | 配置示例 | config.example.json | `assets/configs/config.example.json` | `cfg-providers`, `cfg-priority`, `cfg-mcp`, `use-configure` |

## 构建发布

- `Makefile` — 构建链：build / test(race) / coverage(90% 门禁) / build-all 6 平台交叉编译（关联：q-release）
- `install.sh` — Linux/macOS 安装脚本（latest tag + sha256 校验 + OCR_GITHUB_MIRROR）（关联：cli-overview, q-release）
- `install.ps1` — Windows 安装脚本（PowerShell 5.1+）（关联：cli-overview, q-release）
- `package.json` — npm 包定义（bin: ocr → bin/ocr.js）（关联：q-release, cli-overview）
- `go.mod` — Go 依赖清单（cobra / anthropic-sdk-go / openai-go / MCP go-sdk / otel 等）（关联：q-release）

## CI 集成

- `github_actions-ocr-review.yml` — GitHub Actions 自动审查 workflow 示例（PR 事件+评论触发，并发组防重）（关联：int-gha, use-pr-review, use-ci）
- `gitlab-ci.yml` — GitLab CI 审查作业示例（含 OCR_* 环境变量族）（关联：int-cicd, use-ci）
- `gerrit-Jenkinsfile` — Gerrit 评审流 Jenkinsfile 示例（关联：int-cicd）
- `codeup-flow.yml` — 阿里云 Codeup CI 示例（关联：int-cicd）
- `gitflic-ci.yaml` — GitFlic CI 示例（关联：int-cicd）
- `bitbucket-pipelines.yml` — Bitbucket Pipelines 示例（关联：int-cicd）
- `action.yml` — GitHub Actions composite action 完整定义（24 入参 / 6 出参）（关联：int-gha, use-ci, q-bench）

## 源码节选

- `agent.go.md` — agent.go 核心节选：Run 流水线 / dispatchSubtasks / executeSubtask / REVIEW_FILTER（关联：arch-pipeline, arch-dispatch, arch-parallel, arch-reflection, eng-session, eng-resume, eng-manifest, q-retry）
- `llmloop-loop.go.md` — ReAct 主循环节选：RunPerFile / 终止条件 / 工具分派 / 异步评论（关联：arch-grounded-tools, eng-compression, eng-scan, eng-locator）
- `llmloop-compression.go.md` — 三区内存压缩节选：frozen/compress/active + 60%/80% 双阈值（关联：eng-compression）
- `diff-resolver.go.md` — 行号解析五级回退链节选：ResolveComment / matchConsecutive（关联：eng-locator, eng-filter, cli-review）
- `diff-relocation.go.md` — 跨文件与 LLM 重定位节选：RelocateAcrossFiles / ReLocateComment（关联：eng-relocate）
- `diff-git.go.md` — 三种 diff Provider 节选：range / commit / workspace（关联：eng-diff）
- `scan-agent.go.md` — 全文件扫描引擎节选：Run 时序 / DEDUP / PROJECT_SUMMARY（关联：eng-scan, cli-scan）
- `session-manifest.go.md` — Run Manifest 覆盖度契约节选：RegisterSelected / FailureClass（关联：eng-manifest, eng-session, cli-review, cli-scan）
- `session-resume.go.md` — 断点续审节选：指纹复用 / SealedInput 冻结（关联：eng-resume, cli-session）
- `llm-resolver.go.md` — 5 级配置优先级解析节选：ResolveEndpointWithOptions（关联：cfg-priority, cli-config, cli-llm, q-token）
- `llm-providers.go.md` — 27 个内置 provider 注册表节选（关联：cfg-providers, cli-llm, use-configure）
- `llm-protocol.go.md` — 4 种 LLM 协议定义节选（关联：cfg-protocol）
- `mcp-client.go.md` — MCP 双传输客户端节选：stdio / Streamable HTTP（关联：cfg-mcp）
- `viewer-server.go.md` — viewer 服务器节选：路由 / hostGuard 防 DNS-rebind（关联：cli-viewer, q-security, eng-session, use-pr-review）
- `telemetry-provider.go.md` — OpenTelemetry 双管道初始化节选（关联：q-telemetry, eng-session）
- `gitcmd-runner.go.md` — git 子进程并发限流（默认 16）（关联：eng-diff, eng-scan, arch-parallel）

## 配置示例

- `rule.example.json` — 项目级规则示例（rule.json：include/exclude + 四规则含 glob/docs 外置）（关联：cfg-rules-chain, use-configure, use-extend）
- `config.example.json` — 全局配置示例（provider/自定义端点/LLM/MCP/遥测）（关联：cfg-providers, cfg-priority, cfg-mcp, use-configure）

## 文档

- `README.zh-CN.md` — 官方中文 README（定位/基准/设计理念/快速开始）（关联：cli-overview, arch-hybrid, int-vscode）

## 插件

- `opencode-plugin.ts` — OpenCode 原生插件源码（@opencode-ai/plugin，参数互斥校验）（关联：int-opencode, use-scan-codebase）
- `claude-slash-command.md` — Claude Code 斜杠命令定义（关联：int-claude）
- `codex-plugin.json` — Codex 插件清单（skills + Read capability + defaultPrompt）（关联：int-codex）
- `cursor-plugin.json` — Cursor 插件清单（复用 ../skills/）（关联：int-cursor）
- `qca-system-prompt.md` — QCA Forward 委托系统提示（只允许 delegate preview/rule）（关联：int-qca）

## 提示词

- `review_filter_task_user.md` — 独立反思过滤 prompt 原文（五步法 / Ground A/B / 非对称信息边界）（关联：arch-reflection）

## 规则

- `system_rules.json` — 内置系统规则（四层规则链最底层，首匹配优先）（关联：cfg-rules-chain, arch-dispatch, eng-bundling, cli-rules）

## 脚本

- `post-review-comments.js` — GHA 评论发布脚本（sticky 摘要 / 增量 IoU 去重 / 50 条批量 / severity 路由）（关联：int-gha）

## Skill

- `SKILL-review.md` — 通用 review skill：四步 review/filter/fix/report + severity×category 分级（关联：int-skill, use-no-key, use-scan-codebase）
- `SKILL-delegate.md` — 委托审查 skill：preview→rule→git diff→逐文件→格式化→覆盖率（关联：int-skill, cli-delegate, use-extend）

## 工具 schema

- `tools.json` — 6 个审查专用工具 schema 权威源（plan_task/main_task 相位旗标）（关联：arch-grounded-tools, cli-review, cli-scan, cli-delegate, eng-bundling）
