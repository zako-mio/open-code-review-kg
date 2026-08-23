# 通用 Agent Skill (Portable Agent Skill)

- ID: `int-skill`
- 类型: 工具
- 来源: 集成生态
- 分组: G-E · 集成生态
- 阶段: 高级 advanced

> skills/open-code-review/SKILL.md：四步 review/filter/fix/report 工作流 + delegate 六步 skill，兼容任意 skill 型 Agent

## 核心主张 (what)

- Open Code Review 以 Skill 形态向任意支持 skill 机制的 Agent 暴露能力，核心文件为 skills/open-code-review/SKILL.md 与 skills/open-code-review-delegate/SKILL.md
- skills/open-code-review/SKILL.md 定义标准审查工作流：以 --audience agent --background 模式运行，包含四步——review（审查）、filter（过滤）、fix（修复）、report（报告）
- 审查结果按 severity（严重度）× category（类别）二维矩阵分级，便于按风险优先级处理
- skills/open-code-review-delegate/SKILL.md 定义委托审查六步流程：preview（预览）→ rule（规则检查）→ git diff（差异分析）→ 逐文件审查 → 格式化（输出整理）→ 覆盖率报告
- plugins/open-code-review/skills/ 目录存放同款双份 skill 文件，供插件体系（如 Cursor 插件）复用，保证 CLI 与插件入口行为一致
- 兼容任意 skill 型 Agent：Claude Code、Cursor、Codex 及自定义 Agent 均可通过加载同一份 skill 获得一致审查能力

## 为什么 (why)

- Skill 是跨宿主的标准能力封装形态，一次编写即可被多种 Agent 加载，避免为每个工具重复造轮子（单源多宿主）
- --audience agent --background 的参数组合专为 Agent 消费设计：输出面向 Agent 可解析、运行不阻塞交互，是机器友好集成的前提
- severity×category 分级让审查结果可排序可筛选，Agent 可优先处理高严重度问题，配合 filter 步骤控制噪音
- delegate 六步流程把「预览→规则→diff→逐文件→格式化→覆盖率」拆成可独立校验的阶段，适合需要精细控制与审计的委托场景
- plugins/open-code-review/skills/ 双份存放保证插件化入口与纯 Skill 入口共享同一份工作流定义，降低维护漂移

## 如何实践 (how)

- 前置条件：安装 ocr CLI 并配置 API Key，确认 ocr 可独立运行
- 获取 skill 文件：从仓库复制 skills/open-code-review/ 目录（或使用 plugins/open-code-review/skills/ 下的同款副本）到目标 Agent 的 skills 目录
- 在目标 Agent 中启用 skill（具体方式取决于宿主，如 Cursor 通过插件机制、自定义 Agent 通过技能目录注册）
- 按 SKILL.md 定义发起审查：以 ocr review --audience agent --background <范围> 作为核心调用，覆盖目标文件、目录或提交范围
- 对返回结果执行四步流程：先 review 获得初始报告，再 filter 按 severity×category 过滤噪音，必要时 fix 修复，最后 report 汇总给用户
- 需要委托审查时加载 open-code-review-delegate skill，按六步执行：先用 preview 预览委托、再 rule 检查规则、分析 git diff、逐文件审查、格式化输出、最后生成覆盖率报告
- 根据宿主 Agent 的 skill 协议调整调用封装（如参数传递方式），保证 ocr 命令行参数正确透传
- 验证：以一个小范围 diff 跑通完整流程，确认 JSON 输出可被 Agent 正确解析与汇报

## 案例 (cases)

- 自定义 Agent（非三大商业工具）需要审查能力：直接加载 skills/open-code-review/SKILL.md，获得与官方集成一致的审查工作流
- Cursor 插件场景：插件 skills 字段指向 ../skills/，复用同一份 skill，保证编辑器内与 CLI 审查口径一致
- 精细委托场景：审计团队按 delegate 六步流程执行，先 preview 确认范围、再 rule + git diff 定位、逐文件审查后产出格式化报告与覆盖率报告，形成可归档的审查档案
- 自动化流水线：CI 或 Agent 编排中以 --audience agent --background 调用并解析 JSON，按 severity×category 自动升级高严重度问题到人工

## 反模式/易错点

- 只复制 SKILL.md 不复制配套文件：skill 目录常含辅助脚本/示例，缺文件会导致工作流中途失败；应整目录复制
- 忽略 --audience agent --background：默认模式面向人类阅读，Agent 消费会解析困难或阻塞等待；自动化场景必须显式带上这两个参数
- 把 review skill 与 delegate skill 混用：前者是四步直审，后者是六步委托（含 git diff 与覆盖率报告），流程与产物不同，按场景选型而非随意互换
- 跳过 filter 直接全量汇报：低严重度问题淹没高严重度问题，失去 severity×category 分级的意义；四步流程中 filter 是控制噪音的关键环节，不应省略

## 相关关系

| 方向 | 类型 | 关系 |
|---|---|---|
| int-skill → int-claude | 共现 | Skill 机制与插件生态共现 |
