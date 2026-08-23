# 跨文件与 LLM 重定位 (Cross-file Relocation)

- ID: `eng-relocate`
- 类型: 方法机制
- 来源: 审查引擎
- 分组: G-B · 审查引擎
- 阶段: 高级 advanced

> 评论目标代码在别处时：纯字符串匹配迁移（唯一命中才动）+ LLM 从 diff 重生成代码块再定位

## 核心主张 (what)

- 重定位机制负责把在原文件无法定位的评论迁移到正确的目标文件与行号，分确定性层（RelocateAcrossFiles）与推理层（ReLocateComment）
- RelocateAcrossFiles：将评论的 ExistingCode 逐字摘录，在其他文件的 diff 中做纯字符串匹配
- 0 命中或 >1 命中均拒绝（防歧义），恰好 1 命中则 Path+StartLine+EndLine 整体迁移
- ReLocateComment：通过 BuildReLocationMessages 构造 {diff}/{existing_code}/{suggestion_content} 提示消息交给 LLM
- LLM 输出代码块后经 extractCodeBlock 提取，再重试 ResolveComment；失败时回退到原 snippet
- 是 eng-locator 回退链的第四、五级实现

## 为什么 (why)

- 代码审查中评论位置与目标位置常因重构、移动、复制而不一致，机械匹配无法覆盖全部场景
- 纯字符串匹配零成本且确定性强，但只能处理文本完全一致的搬迁；语义等价但文本变化的场景必须借助 LLM
- 0/多命中双拒绝策略规避歧义风险——宁可放弃迁移也不把评论错误安放到无关代码上
- 失败保留原 snippet 保证『评论内容永远不丢』，位置错误可人工修正，内容丢失不可恢复

## 如何实践 (how)

- RelocateAcrossFiles 从评论摘录 ExistingCode 原文（逐字），遍历其他文件 diff 内容执行字符串匹配
- 命中数检查：恰好 1 命中才接受；0 命中（目标不在其他文件）与 >1 命中（目标代码存在多份拷贝）都拒绝迁移
- 接受后将评论的 Path、StartLine、EndLine 整体迁移到命中位置
- ReLocateComment 通过 BuildReLocationMessages 组装 {diff}/{existing_code}/{suggestion_content} 三要素提示词
- 请求 LLM 生成包含目标位置的代码块，经 extractCodeBlock 提取后重试 ResolveComment 完成定位
- 重试仍失败则回填原 snippet（原文件+原行号），交由用户或后续人工处置

## 案例 (cases)

- 工具函数从 a.go 复制到 b.go，评论原定位在 a.go，RelocateAcrossFiles 在 b.go diff 中恰好 1 命中，整体迁移成功
- 同一代码块在多个文件重复出现（>1 命中），迁移被拒绝避免歧义，降级走 LLM 或保留原位
- 函数被重命名+重构，字符串匹配无命中，LLM 根据 diff/现有代码/建议内容推理出真实目标位置
- 分布式 mock 代码被整体移动后文本一致，字符串匹配直接迁移成功，零 LLM 成本

## 反模式/易错点

- 采用『首次命中即接受』而非『恰好 1 命中』，把评论错误安放到同名代码的无关拷贝上
- 直接把 LLM 输出当最终答案而不经 extractCodeBlock 清洗，混入解释性文本导致定位失败
- 失败路径直接丢弃评论，破坏『评论不丢失』契约
- 用归一化（去空白/大小写）后的文本做字符串匹配，破坏逐字匹配的确定性语义

## 相关关系

| 方向 | 类型 | 关系 |
|---|---|---|
| eng-locator → eng-relocate | 前置依赖 | 定位失败才触发重定位 |
| eng-locator → eng-relocate | 变体 | 重定位是定位的升级路径 |
