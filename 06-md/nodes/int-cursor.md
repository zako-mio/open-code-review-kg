# Cursor 插件 (Cursor Plugin)

- ID: `int-cursor`
- 类型: 工具
- 来源: 集成生态
- 分组: G-E · 集成生态
- 阶段: 高级 advanced

> .cursor-plugin/plugin.json + 可移植 skill，复制到 ~/.cursor/plugins/local/ 手动安装

## 核心主张 (what)

- Alibaba Open Code Review 为 Cursor（AI 编辑器）提供的集成插件，清单文件 .cursor-plugin/plugin.json，其 skills 字段指向 ../skills/ 目录，即复用仓库通用 skills 目录中的同一份 Skill 定义
- 安装方式为手动复制：将 plugins/open-code-review/ 整个目录复制到 ~/.cursor/plugins/local/open-code-review/ 路径下，即可被 Cursor 识别为本地插件
- 其核心是可移植 skill 机制：同一份 skill 定义可被 Cursor、通用 Agent 等不同宿主共享，实现「一份技能、多处复用」
- 插件本质是把通用 open-code-review Skill（含 --audience agent --background 等工作流）挂载进 Cursor 的插件体系，使 Cursor 用户获得与 CLI 一致的审查能力
- 作为多生态集成的一环，Cursor 路径代表了面向编辑器的轻量集成方式：无插件市场依赖、纯本地文件复制

## 为什么 (why)

- Cursor 是市场占有率高的 AI 编辑器，其本地插件机制支持从目录直接加载，手动复制是最低摩擦的交付方式，无需上架插件市场
- 通过复用 ../skills/ 指向的同一份 skill 定义，避免为每个宿主维护多份重复技能文件，保证 Cursor 与通用 Agent 的行为一致（单源维护）
- 可移植 skill 机制使技能资产跨宿主沉淀：无论用户切到 Cursor、Claude Code 还是其他支持 skill 的 Agent，审查工作流保持一致
- 本地插件方式便于企业内网/受限网络环境离线安装，不依赖外网插件市场

## 如何实践 (how)

- 前置条件：本机安装 ocr CLI 并配置好模型 API Key，确保 ocr 命令可独立运行
- 定位仓库中的插件目录：找到 open-code-review 仓库下的 plugins/open-code-review/ 目录（内含 .cursor-plugin/plugin.json）
- 创建目标目录：mkdir -p ~/.cursor/plugins/local/open-code-review/
- 执行复制安装：将插件目录内容复制到 ~/.cursor/plugins/local/open-code-review/（如 cp -r plugins/open-code-review/* ~/.cursor/plugins/local/open-code-review/），确保 .cursor-plugin 子目录一并复制
- 重启 Cursor 或触发插件重载，使 Cursor 扫描并加载本地插件目录
- 在 Cursor 中按插件注册的方式调用审查技能（通常通过 Agent/Skill 面板或命令入口触发），审查流程将复用通用 SKILL.md 中定义的 review 工作流（--audience agent --background 等）
- 验证：发起一次小范围审查确认插件被正确加载且 ocr 调用链路通畅
- 升级插件时重新复制新版本目录并重启 Cursor，覆盖旧文件

## 案例 (cases)

- Cursor 用户希望在编辑器内完成审查而无需切终端：复制插件后，直接在编辑会话中触发 review 技能即可
- 团队统一在 Cursor 中使用审查：把插件目录随初始化脚本（如 dotfiles/bootstrap 脚本）分发到每台开发机 ~/.cursor/plugins/local/，实现团队级开箱即用
- 内网开发环境无法访问插件市场：采用手动复制方式离线安装，实现受限网络下的审查能力落地

## 反模式/易错点

- 复制路径错误：把 plugins/open-code-review/ 之外的文件或把目录内容散落复制到其他位置，导致 Cursor 无法识别；必须整体复制且 .cursor-plugin 子目录结构保持完整
- 复制后不重启：Cursor 对本地插件的扫描通常发生在启动/重载时，直接使用会提示插件不存在，应先重启再调用
- 忽略 skill 文件依赖：plugin.json 的 skills 指向 ../skills/，若复制时裁剪了上级 skills 目录或改变相对路径，技能加载将失败；应按仓库原始结构完整搬运
- 以为改一处配置即可全局生效：本地插件是每机器复制模式，改动后需在所有目标机器重新同步，没有插件市场式的自动更新

## 相关关系

| 方向 | 类型 | 关系 |
|---|---|---|
| int-claude → int-cursor | 变体 | 同为插件生态 |
