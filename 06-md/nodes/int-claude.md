# Claude Code 插件 (Claude Code Plugin)

- ID: `int-claude`
- 类型: 工具
- 来源: 集成生态
- 分组: G-E · 集成生态
- 阶段: 高级 advanced

> claude-code 插件：/open-code-review:review 与 :delegate-review 斜杠命令，marketplace 安装

## 核心主张 (what)

- Alibaba Open Code Review 为 Claude Code 提供的官方集成插件，仓库路径为 plugins/open-code-review/claude-code/，核心清单文件为 .claude-plugin/plugin.json，其中 commands 字段指向 ./commands 目录，即插件以斜杠命令（slash command）形式暴露能力
- 插件安装后为 Claude Code 注入两条核心斜杠命令：/open-code-review:review（触发代码审查）与 /open-code-review:delegate-review（触发委托审查），命令定义位于插件 commands 目录下
- 除插件注册的命令外，仓库根目录还内置 .claude/commands/open-code-review.md 作为开箱即用的斜杠命令，同目录另有 commit.md（提交辅助）与 tag.md（打标签辅助）两条配套命令
- 该插件本质是把 ocr CLI 的能力以 Claude Code 原生命令的方式暴露，让用户在会话中直接输入斜杠命令即可启动审查流程，无需记忆 CLI 参数
- 属于仓库多 IDE/多 Agent 生态中的 Claude Code 官方入口，与 Codex、Cursor、OpenCode 等集成并列

## 为什么 (why)

- Claude Code 是当前主流 AI 编码 Agent 之一，用户习惯以斜杠命令触发工作流，插件化集成可让审查能力零门槛融入既有会话，无需切换到终端手动执行 CLI
- 斜杠命令封装了 ocr 的复杂参数与调用链，降低使用门槛，同时通过 /open-code-review:delegate-review 提供委托审查路径，适应「宿主模型把关、OCR 干活」的组织分工场景
- 内置 .claude/commands/open-code-review.md 与 commit.md/tag.md 命令形成「审查—提交—打标签」的完整闭环，覆盖代码合并前的主要操作环节

## 如何实践 (how)

- 前置条件：确保已安装 ocr CLI（ocr --version 可验证），并完成 API Key 配置，使 ocr 命令可独立运行
- 从 Claude Code 的插件市场安装：执行 /plugin marketplace add alibaba/open-code-review 将阿里官方仓库添加为插件市场源
- 随后执行 /plugin install open-code-review@open-code-review 安装插件本体，安装后插件命令即注册到当前会话
- 重启或刷新 Claude Code 会话后，输入 /open-code-review:review 并附加目标范围参数（如文件、提交或目录）即可发起审查
- 需要委托审查时，使用 /open-code-review:delegate-review 命令，按提示指定审查范围与委托配置
- 若不想走插件市场，也可直接依赖仓库根目录内置命令：将仓库中的 .claude/commands/open-code-review.md（以及 commit.md、tag.md）复制到本地项目的 .claude/commands/ 目录，即可获得同等的斜杠命令体验
- 执行审查后，Claude Code 会在会话内呈现审查结果，可继续以对话方式追问、过滤或修复发现的问题

## 案例 (cases)

- 开发者在 Claude Code 会话中完成一个 feature 分支的编码后，直接输入 /open-code-review:review 审查改动文件，在提交前拦截潜在缺陷
- 团队采用「AI 审查 + 人工确认」流程：开发者在合并前先跑 /open-code-review:review，再针对高严重度问题与 Claude 讨论修复方案，最后用内置 commit.md 生成规范提交信息
- 安全敏感仓库中，开发者通过 /open-code-review:delegate-review 将审查委托给 OCR 模型执行，Claude 仅负责汇总与裁决，实现职责分离

## 反模式/易错点

- 只装插件不装 CLI：插件本质是 CLI 的薄封装，若本机缺少 ocr 可执行文件或未配置 Key，命令会直接失败；应先用终端验证 ocr --version 与一次最小审查通过
- 重复安装源：先 add marketplace 又手动复制 .claude/commands 文件，可能导致同一命令被注册两次、行为冲突；二选一即可
- 在会话中混淆 review 与 delegate-review：两者审查范围与权限模型不同，普通代码审查误用 delegate-review 可能走不到预期模型配置，应先明确两条命令的差异再选用
- 忽略内置命令差异：误以为只有插件才有命令，实际仓库根的 .claude/commands 已内置 open-code-review.md，直接复制即可用，无需为简单场景搭建插件市场流程

## 相关关系

| 方向 | 类型 | 关系 |
|---|---|---|
| int-claude → cli-delegate | 前置依赖 | Claude 插件可走委托模式 |
| int-claude → int-codex | 变体 | 同为插件生态 |
| int-claude → int-cursor | 变体 | 同为插件生态 |
| int-skill → int-claude | 共现 | Skill 机制与插件生态共现 |
