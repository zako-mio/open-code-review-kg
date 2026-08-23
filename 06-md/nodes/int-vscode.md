# VSCode 扩展 (VSCode Extension)

- ID: `int-vscode`
- 类型: 工具
- 来源: 集成生态
- 分组: G-E · 集成生态
- 阶段: 高级 advanced

> React webview（侧边栏/配置面板/评论面板）+ CliService 封装，i18n en/zh，webpack+jest

## 核心主张 (what)

- Open Code Review 提供 VSCode 官方扩展，代码位于仓库 extensions/vscode/ 目录，面向编辑器内审查场景
- UI 层基于 React webview 实现，包含三个 Provider：SidebarProvider（侧边栏）、ConfigPanelProvider（配置面板）、CommentProvider（评论视图），构成扩展的主要交互界面
- 服务层包含多个模块：CliService（封装 ocr CLI 调用并支持取消操作）、ConfigService（配置管理与读取）、ReviewSession（审查会话状态管理）、GitService（git 相关能力，如获取 diff/提交信息）
- 支持国际化（i18n），内置 en（英文）与 zh（中文）两种语言资源
- 工程体系采用 webpack 打包 + jest 测试，代码组织为典型的前端工程结构
- 作为编辑器集成入口，与 CLI、Skill、各 Agent 插件并列，覆盖「不想离开 IDE」的用户群体

## 为什么 (why)

- 大量开发者习惯在编辑器内完成从编码到审查的全流程，VSCode 扩展降低工具切换成本，审查结果直接呈现在 IDE 上下文中
- React webview + Provider 分层（Cli/Config/ReviewSession/Git 服务拆分）支撑起配置、会话、取消等交互细节，比纯终端体验更完整
- CliService 支持取消操作，说明设计上考虑了大范围审查的可中止性，避免阻塞用户
- i18n en/zh 双语言满足中英文用户群体，降低出海/国内团队的使用门槛
- webpack+jest 工程化保证扩展可构建、可测试、可持续维护，适合长期演进

## 如何实践 (how)

- 前置条件：安装 ocr CLI 并配置 API Key（与 CLI 用法一致），安装 VSCode
- 从仓库获取扩展产物：构建 extensions/vscode/（npm install 后执行构建脚本，webpack 打包生成 .vsix）或获取官方发布的 vsix 包
- 安装扩展：在 VSCode 扩展面板中选择「从 VSIX 安装…」并选择打包产物，或按官方说明安装
- 打开配置面板（ConfigPanelProvider）：通过侧边栏/命令入口进入，配置 ocr 命令路径、模型/API Key 等参数（ConfigService 持久化）
- 在侧边栏（SidebarProvider）中选择审查目标（文件/目录/提交），点击触发审查
- 审查执行由 CliService 封装调用，支持取消；审查过程中 ReviewSession 维护会话状态，如中途取消可保留进度
- 审查结果通过 CommentProvider 以评论/注解形式展示在代码中，用户可就地查看问题定位
- 涉及 git 上下文（如审查某次提交的 diff）时由 GitService 提供支持；验证：对单个文件发起一次审查，确认 webview 正常展示结果

## 案例 (cases)

- 开发者在 VSCode 中改完代码后，从侧边栏一键触发当前文件审查，结果以代码评论形式呈现，直接定位问题行
- 提交前审查：通过 GitService 获取待提交 diff，在提交动作前跑一轮审查并把结果留在评论视图，作为合并闸门
- 大范围审查中途发现范围不对：利用 CliService 的取消能力中止审查，调整范围后重新发起，避免浪费计算资源

## 反模式/易错点

- 跳过配置直接审查：不通过 ConfigPanel 配置 CLI 路径/Key，CliService 找不到可执行文件或凭证导致审查失败；首次使用必须先完成配置
- 忽略 ReviewSession 状态：取消或中断审查后不检查会话状态，再次触发可能基于过期上下文；应确认会话已结束或重置后再发起
- 在构建产物缺失时手动改源码目录：扩展需 webpack 构建产物（或 vsix）才能加载，直接加载源码目录会失败；应先执行构建
- 忘记 CLI 依赖：扩展的 CliService 是薄封装，本机没有 ocr 或 Key 未配置时扩展表现为「点击无反应」或报错，排障时应先回到终端验证 CLI 本身可用

## 相关关系

| 方向 | 类型 | 关系 |
|---|---|---|
| int-vscode → cli-review | 依赖关联 | VSCode 扩展封装 CLI |
