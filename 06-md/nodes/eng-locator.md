# 行号定位回退链 (Line Number Resolution)

- ID: `eng-locator`
- 类型: 方法机制
- 来源: 审查引擎
- 分组: G-B · 审查引擎
- 阶段: 进阶 intermediate

> 五级回退：hunk 新侧→hunk 旧侧→全文件滑动窗口→跨文件重定位→LLM 重定位，保证评论落在真实行

## 核心主张 (what)

- 行号定位回退链解决『审查评论最终必须落在哪个文件的哪几行』的定位问题，是评论回填 Collector 前的最后一步精确对齐
- 采用五级回退策略，优先级从同文件精确匹配逐步降级到跨文件匹配，最终由 LLM 兜底
- 第一级：同文件 hunk 新侧（context+added 行→新行号）精确连续匹配
- 第二级：hunk 旧侧（context+deleted 行→旧行号）匹配
- 第三级：NewFileContent 全文件滑动窗口匹配，窗口可跳空行容忍格式噪音
- 第四级：跨文件 RelocateAcrossFiles 纯字符串匹配；第五级：LLM ReLocateComment 生成目标代码块定位
- 配套 normalizeLine 清洗（去 +/- 前缀与首尾空白）与 matchConsecutive 精确连续匹配保证匹配严格性

## 为什么 (why)

- 单一匹配策略在真实 diff 中常失效（行号漂移、文件改名、上下文被截断），需要多级回退链逐级降级兜底
- 新侧优先因为评论目标是『改动后的新代码』，新行号对用户可点击跳转最有效
- 全文件滑动窗口解决 diff 上下文不足以唯一匹配的模糊场景，跳空行容忍格式噪音
- LLM 兜底保证极端场景（跨文件、语义等价但文本不同）下仍能给出定位结果，避免评论无处安放

## 如何实践 (how)

- 一级：在目标文件各 hunk 的新侧（context+added 行集合）按行顺序做精确连续匹配（matchConsecutive），命中返回新行号区间
- 二级：一级失败后转向 hunk 旧侧（context+deleted 行→旧行号）执行同样的连续匹配
- 三级：两级 hunk 匹配失败后，以 NewFileContent 全文件为文本，用滑动窗口匹配目标行片段（可跳过空行）
- 四级：仍失败则调用 RelocateAcrossFiles 在其他文件 diff 中做纯字符串匹配迁移
- 五级：最终由 LLM ReLocateComment 推理定位，返回代码块后 resolve 评论行号
- 全程先 normalizeLine 清洗行内容（去 +/- 前缀、首尾空白），再交给 matchConsecutive 严格精确匹配，杜绝模糊子串误命中

## 案例 (cases)

- 开发者把被注释的代码块上下移动了 20 行，一级新侧匹配失败，二级旧侧按旧行号定位成功
- diff 仅含少量上下文行导致片段被截断，三级全文件滑动窗口找到唯一匹配位置
- 评论针对的函数被抽到另一个文件，四级跨文件 RelocateAcrossFiles 纯字符串匹配命中新文件
- 重构后文本面目全非，四级 0/多命中被拒绝，最终五级 LLM 推理出目标位置

## 反模式/易错点

- 跳过 normalizeLine 直接匹配带 +/- 前缀的行，导致全链路匹配失败
- 用子串/模糊匹配代替 matchConsecutive 精确连续匹配，误命中行号污染评论落点
- 五级链路不逐级降级、直接跳级，导致本可用旧侧定位的评论被 LLM 高成本兜底
- 忽略滑动窗口的跳空行能力，把格式噪音当失败原因，过早进入跨文件/LLM 兜底

## 相关关系

| 方向 | 类型 | 关系 |
|---|---|---|
| arch-grounded-tools → eng-locator | 前置依赖 | 工具评论需行号定位 |
| arch-reflection → eng-locator | 前置依赖 | 反思依赖评论定位结果 |
| eng-diff → eng-locator | 前置依赖 | 行号映射基于 hunk |
| eng-filter → eng-locator | 前置依赖 | 定位发生在保留文件上 |
| eng-locator → eng-relocate | 前置依赖 | 定位失败才触发重定位 |
| eng-locator → eng-relocate | 变体 | 重定位是定位的升级路径 |
