# 场景：免 Key 委托审查 (Scenario: Delegated Review)

- ID: `use-no-key`
- 类型: 场景索引
- 来源: 使用场景
- 分组: G-S · 使用场景索引
- 阶段: 进阶 intermediate

> 没有 LLM API Key 或想用宿主 Agent 模型：ocr delegate preview/rule 输出 spec，编码 Agent 自己审

## 核心主张 (what)

- 面向没有 LLM API Key 或希望复用宿主 Agent（如 QCA、Claude Code）模型能力的场景
- ocr delegate preview --format json 输出当前可审查的文件清单，供委托前确认范围
- ocr delegate rule src/main.go src/handler.go 输出针对指定文件的审查规则，作为委托审查的标准
- 委托流程：编码 Agent 用 git diff 取到 diff → 按 delegate 给出的规则审查 → 输出结构化评论，OCR 只做规则与编排
- QCA / Claude Code 等宿主 Agent 插件内嵌委托命令，让审查能力融入已有工作流

## 为什么 (why)

- 很多开发者没有直接可用的 LLM API Key，或已有宿主 Agent 的模型额度，重复付费不划算
- 把『规则生成』与『审查执行』分离：OCR 负责高质量规则，宿主 Agent 负责执行，各用所长
- 委托模式让 OCR 审查能力可嵌入任何 Agent 工作流，而不局限于 OCR 自身的模型连接

## 如何实践 (how)

- 查看可审查清单：运行 ocr delegate preview --format json，确认当前仓库哪些文件可进入委托范围
- 获取审查规则：运行 ocr delegate rule src/main.go src/handler.go，得到针对这两个文件的规则文本
- 执行委托审查：在编码 Agent 内用 git diff 取 diff，将 delegate rule 输出的规则与 diff 一起交给宿主 Agent，令其按规则输出结构化评论
- 嵌入插件：在 QCA / Claude Code 插件中内嵌 ocr delegate 命令，实现『宿主模型 + OCR 规则』的混合审查流

## 案例 (cases)

- 无 Key 环境：只有宿主 Agent（如 Claude Code）模型可用，通过 delegate 获取规则后由宿主执行审查
- 规则标准化：团队把 delegate rule 输出固化为审查 checklist，所有成员与 Agent 共用同一套标准
- 插件集成：Claude Code 插件内调用 delegate 命令，审查能力一键获得
- 批量预审：preview 先圈定文件范围，避免委托审查覆盖无关文件

## 反模式/易错点

- 把 delegate preview 当审查结果：preview 只是文件清单，真正的审查结论仍需 Agent 按规则执行
- 用宿主 Agent 直接审查而不取 delegate rule，等于放弃 OCR 沉淀的审查规则，质量回到裸模型水平
- 在委托链中丢失 git diff 上下文，宿主 Agent 只拿到文件全文而非变更，审查失去 diff 焦点
- 忽视输出结构化约束，宿主 Agent 返回自由文本评论，无法被下游解析与回贴

## 相关关系

| 方向 | 类型 | 关系 |
|---|---|---|
| cli-delegate → use-no-key | 前置依赖 | 免 Key 场景指向 delegate |
| cli-delegate → use-no-key | 共现 | 委托模式即免 Key 场景 |
