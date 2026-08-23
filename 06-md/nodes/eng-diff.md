# Git Diff 获取与解析 (Diff Acquisition & Parsing)

- ID: `eng-diff`
- 类型: 方法机制
- 来源: 审查引擎
- 分组: G-B · 审查引擎
- 阶段: 基础 basic

> 三种 diff 来源（workspace/range/commit）+ unified diff 解析器（ParseDiffText/ParseHunks）

## 核心主张 (what)

- diff 获取支持三种 Provider，按用户场景选择：range（区间对比）、commit（单提交审查）、workspace（工作区未提交改动）
- range 模式执行 git diff -U3 --find-renames merge-base..to：对比 merge base 到目标提交的完整差异，-U3 表示 3 行上下文，--find-renames 识别重命名文件
- commit 模式执行 git show --diff-merges=first-parent：审查单提交时用 first-parent 避免 merge 提交的组合 diff（combined diff）
- workspace 模式覆盖 tracked（已跟踪）与 untracked（未跟踪）文件：合并两者得到工作区全部改动
- ParseDiffText 状态机按 diff --git 头切分多个文件条目，ParseHunks 解析 @@ 行（hunk 头）拆分变更块
- finalizeDiff 读取新文件全文以补充上下文；DiffContextLines=3 为默认上下文行数，与 -U3 呼应

## 为什么 (why)

- 三种 Provider 覆盖三种真实审查入口：审查历史区间（range）、审查单个提交（commit）、审查未提交改动（workspace），单一模式无法适配全部场景
- --find-renames 保证重命名文件被识别为『移动+修改』而非『删除+新增』，避免审查对重命名文件产生误报
- --diff-merges=first-parent 规避 merge 组合 diff 的爆炸性体积与语义混乱：合并提交的 combined diff 会把多个父分支的变更混在一起，first-parent 只与主父分支对比
- -U3 与 DiffContextLines=3 统一上下文行数，既给模型足够上下文判断变更影响面，又不让 diff 体积失控
- ParseDiffText 状态机与 ParseHunks 是确定性解析：diff 文本结构稳定（--git 头、@@ 行），用代码解析比交给模型理解更可靠、更省 token

## 如何实践 (how)

- range 模式：执行 git diff -U3 --find-renames merge-base..to，其中 merge-base 取两端的合并基点，to 为目标提交，输出为统一 diff 格式文本
- commit 模式：执行 git show --diff-merges=first-parent <commit>，带 --diff-merges=first-parent 参数避免 merge 组合 diff
- workspace 模式：分别获取 tracked（git diff 无参数默认覆盖工作区已跟踪文件）与 untracked（新增未跟踪文件）两路改动后合并
- 解析流程：ParseDiffText 以 diff --git 为分隔标记按文件切分 diff 文本 → 每个文件条目内 ParseHunks 按 @@ -l,s +l,s @@ 头解析变更块 → 块内含 -U3 提供的上下文行与 +/- 变更行
- finalizeDiff 在 hunk 解析后读取新文件全文，用于后续 file_read/评论定位需要完整文件内容的场景
- 输出供下游：解析后的 diff 结构（文件、hunk、行号、变更类型）注入文件子任务上下文，供 Plan/MainTask 使用

## 案例 (cases)

- 审查一个 merge 提交：若用默认 git show 会得到 combined diff（多个父分支变更交织），改用 --diff-merges=first-parent 后 diff 体积与语义回归可控
- PR 中包含重命名+微改的文件：--find-renames 使其以 rename 形式呈现，过滤与评论定位按新路径处理，避免误判为删旧增新

## 反模式/易错点

- 审 merge 提交时不加 --diff-merges=first-parent——combined diff 体积爆炸且语义混乱，模型上下文被无关父分支变更污染
- 重命名文件被当成删除+新增——未加 --find-renames 时 rename 被拆成两条记录，过滤链与评论定位（path）都会产生误报
- 手工解析 diff 文本（正则硬抠）——diff 格式有边界情况（无新行文件、二进制标记、文件头差异），必须用 ParseDiffText/ParseHunks 状态机
- 上下文行数随意改大（如 -U10）——上下文增多使 diff 膨胀数倍，预算压力上升而收益有限，DiffContextLines=3 是验证过的平衡点

## 相关关系

| 方向 | 类型 | 关系 |
|---|---|---|
| arch-pipeline → eng-diff | 前置依赖 | 流水线第一环是 diff 获取 |
| eng-diff → eng-filter | 前置依赖 | 过滤基于解析后的 diff |
| eng-diff → eng-locator | 前置依赖 | 行号映射基于 hunk |
