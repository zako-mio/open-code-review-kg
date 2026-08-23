# Codex 插件 (Codex Plugin)

- ID: `int-codex`
- 类型: 工具
- 来源: 集成生态
- 分组: G-E · 集成生态
- 阶段: 高级 advanced

> .codex-plugin/plugin.json + skills：以 @Open Code Review review ... 调用，interface Read capability

## 核心主张 (what)

- Alibaba Open Code Review 为 OpenAI Codex（CLI/Agent 形态）提供的官方集成，插件清单 .codex-plugin/plugin.json 声明 skills: ./skills/ 目录，即通过 Skill 机制暴露审查能力
- 插件 interface 声明了 capabilities Read，即仅请求读取类能力，不申请文件写入等更高级权限，符合审查工具只读分析定位
- defaultPrompt 内置 3 条默认提示词，为插件预置了开箱即用的调用模板，用户可在此基础上扩展
- 安装并启用后，用户在 Codex 会话中以 @Open Code Review review ... 的形式调用，将审查作为 Agent 的一个可调用技能
- 属于多 Agent 生态中的 Codex 官方入口，与 Claude Code 插件、Cursor 插件等并列，保证同一套 OCR 能力在不同 Agent 宿主间复用

## 为什么 (why)

- Codex 与 Claude Code 一样占据主流 AI 编码工具生态位，但两者的插件协议不同（Claude 用 .claude-plugin 斜杠命令，Codex 用 .codex-plugin Skill），需要独立的适配层
- 通过 Skill + defaultPrompt 的方式，将 ocr 的复杂命令序列封装为 @Open Code Review 一次调用，用户无需了解底层参数细节
- interface 仅声明 Read capability 体现了最小权限原则：审查只需读代码与输出结果，降低插件在宿主中的安全风险面
- 面向已有 Codex 使用习惯的团队，可让审查能力直接并入现有 Agent 工作流，避免工具切换成本

## 如何实践 (how)

- 前置条件：安装并登录 Codex CLI，同时在环境中准备好可运行的 ocr CLI 与对应 API Key
- 添加插件市场：执行 codex plugin marketplace add alibaba/open-code-review，将官方仓库注册为 Codex 插件市场源
- 安装插件：执行 codex plugin install open-code-review（或按 Codex 版本对应的 /plugins 交互流程操作），随后在 /plugins 面板中启用该插件
- 插件启用后，在任意 Codex 会话中输入 @Open Code Review review <目标>，其中 <目标> 可为文件路径、目录、提交范围或 git diff 范围
- Codex 会加载插件 defaultPrompt 并执行审查流程，审查输出以 Agent 回复形式返回，可在会话内追问细节
- 如需调整审查深度或范围，可结合 defaultPrompt 的既有模板，在调用指令中附加说明，让 Codex 自动映射到 ocr 对应参数
- 审查完成后将结果与人工确认结合，再决定修复动作；插件本身不申请写入权限，修改需在宿主中显式执行

## 案例 (cases)

- Codex 用户完成编码任务后，在会话中直接输入 @Open Code Review review src/ 对改动目录发起一轮审查，先于 CI 发现隐患
- 团队把审查能力纳入 Codex 的日常开发循环：每次功能完成、提交之前固定调用 @Open Code Review，审查结果作为合并前的质量闸门之一
- 依赖 Codex 进行大规模重构时，用 @Open Code Review review <diff 范围> 精准限定审查对象，避免无关文件噪音

## 反模式/易错点

- 忽略插件的 Read-only 能力边界：想当然地让插件「顺便修复问题」，实际插件不申请写入权限，修复必须在宿主中另行执行
- 跳过 /plugins 启用步骤：只 add marketplace 却不在 /plugins 面板启用，导致 @Open Code Review 不可用；两个步骤缺一不可
- 把 @Open Code Review 当万能命令：它按 defaultPrompt 模板工作，随意附加与模板冲突的语义可能让 Codex 映射出错误的 ocr 参数，应先跑一次默认调用再定制
- 在无 Key/无 CLI 环境直接调用：插件调用依赖本机 ocr 与模型 Key，环境未就绪时表现为静默失败或超时，应先做最小可用性验证

## 相关关系

| 方向 | 类型 | 关系 |
|---|---|---|
| int-claude → int-codex | 变体 | 同为插件生态 |
| int-codex → int-opencode | 变体 | 同为插件生态 |
