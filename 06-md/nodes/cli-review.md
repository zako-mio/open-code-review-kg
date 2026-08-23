# ocr review (ocr review)

- ID: `cli-review`
- 类型: 工具
- 来源: 命令行
- 分组: G-C · 命令行工具
- 阶段: 基础 basic

> 基于 git diff 的审查主命令：workspace/range/commit 三模式，--format text|json|sarif，--resume 断点续审

## 核心主张 (what)

- ocr review 是工具的主命令，基于 git 变更执行 AI 代码审查，是日常使用频率最高的入口
- 支持三种审查模式：裸运行 ocr review 审查 workspace（暂存 + 未暂存 + 未跟踪的改动）；--from/--to 指定合并基准（如 --from main --to feature-branch）做分支对比；--commit <hash> 针对单个 commit 审查
- 输出格式可选 text（默认，人类可读）、json（结构化，供脚本消费）、sarif（供 CI/静态分析工具集成）
- 受众维度通过 --audience 控制：human 面向人类阅读、agent 面向 AI Agent 消费，输出详略与措辞不同
- 资源控制参数齐全：--concurrency（默认 8）控制并行度、--timeout（默认 10 分钟）控制单次审查超时、--max-tokens / --max-tokens-budget / --max-tools / --max-git-procs 约束 token 预算、工具调用数与 git 子进程数
- 支持 --resume 断点续审（配合 session）、--background(-b)/--background-file(-B) 后台执行、--preview(-p) 预演不实际调用 LLM、--provider/--model 指定模型、--no-filter 关闭结果过滤、--rule/--exclude 控制规则与排除路径

## 为什么 (why)

- 三种模式精确对应日常开发流程：提交前看工作区改动、合并前看分支差异、复盘时看单次提交，无需切换工具
- json/sarif 输出使审查结果可被 CI 流水线、缺陷管理平台与其他工具链消费，而不只是给人看的文本
- 并发、超时、token 预算等参数让大仓库审查可控可预期，避免长时间无响应或预算超支

## 如何实践 (how)

- 审查当前工作区全部改动：ocr review
- 分支合并前对比审查：ocr review --from main --to feature-branch
- 审查单个提交：ocr review --commit abc123
- 结构化输出：ocr review --format json 或 ocr review --format sarif（CI 集成）
- 面向 Agent 消费：ocr review --audience agent
- 精细控制范围：ocr review --rule <rule-id> --exclude '<glob>' 指定规则并排除路径
- 控制资源：ocr review --concurrency 8 --timeout 30m --max-tokens-budget 200000 --max-git-procs 4
- 指定模型与预演：ocr review --provider openai --model gpt-4o；ocr review --preview 查看将审查的变更而不调用 LLM
- 后台执行：ocr review --background --background-file review.jsonl，之后用 ocr session 查看进度与结果
- 中断后续审：ocr review --resume <session-id> 从断点继续

## 案例 (cases)

- 提交前自查：改完代码直接 ocr review，快速获得 AI 对暂存与未暂存改动的审查意见，修复后再提交
- PR 合并前把关：在 feature 分支上执行 ocr review --from main --to feature-branch，聚焦本次合并将引入的全部差异
- CI 集成：流水线中执行 ocr review --format sarif --audience agent，将 SARIF 上报给代码平台或缺陷系统
- 大仓库长时间审查：开启 ocr review --background --background-file out.jsonl 后台跑，配合 --concurrency/--timeout 调整，随后用 session 查看并 --resume 续审

## 反模式/易错点

- 不调 --timeout 直接审超大仓库：默认 10 分钟超时对大型变更远远不够，中途超时后未用 --resume 续审，导致已消耗的 token 与时间全部浪费，应预估规模后显式设置 --timeout 与 --max-tokens-budget
- --concurrency 与 --max-git-procs 拉满追求速度：并发过高导致 LLM API 限流报错或 git 进程冲突、diff 计算互相干扰，应结合仓库规模与限流阈值保守设置
- 依赖默认文本输出对接自动化：管道消费 text 格式脆弱，脚本应显式使用 --format json 或 sarif，并留意 --audience 对输出结构的影响
- 后台模式不使用 --background-file 指定输出路径：默认位置不易定位，结果文件被清理后无处恢复，应显式指定并记录路径

## 相关关系

| 方向 | 类型 | 关系 |
|---|---|---|
| eng-resume → cli-review | 前置依赖 | review 支持 --resume 续审 |
| cli-overview → cli-review | 前置依赖 | 安装后先学 review |
| cli-review → use-pr-review | 前置依赖 | PR 审查场景指向 review 命令 |
| cli-review → cli-scan | 变体 | 两种审查模式互为变体 |
| cli-delegate → cli-review | 变体 | 委托 vs OCR 驱动 |
| cli-review → use-pr-review | 组合 | Action+review 组合成 PR 自动审查 |
| int-vscode → cli-review | 依赖关联 | VSCode 扩展封装 CLI |
| int-opencode → cli-review | 依赖关联 | OpenCode 插件 spawn CLI |
| cli-review → eng-session | 依赖关联 | review 产生会话记录 |
