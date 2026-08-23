# 场景：审查 PR/分支变更 (Scenario: PR Review)

- ID: `use-pr-review`
- 类型: 场景索引
- 来源: 使用场景
- 分组: G-S · 使用场景索引
- 阶段: 基础 basic

> 日常审查入口：合并基准模式审 feature 分支、单 commit 审查、GitHub PR 上自动触发

## 核心主张 (what)

- 日常审查入口：对当前工作区、分支 diff 或指定 commit 进行 AI 代码审查，是使用频率最高的场景
- 支持三种触发方式：ocr review（审查当前工作区改动）、ocr review --from main --to feature-branch（审查分支间 diff）、ocr review --commit abc123（审查单个 commit）
- GitHub PR 自动触发：examples/github_actions/ocr-review.yml 监听 pull_request_target 的 opened/synchronize/reopened 事件，以及 issue_comment 中出现 '/open-code-review' 命令时触发
- 评论触发权限受限：仅 MEMBER/OWNER/COLLABORATOR 可触发，防止陌生人滥用工作流
- 并发控制：以 ocr-<pr> 为并发组 key，同一 PR 同时只跑一个审查，避免重复评论
- 审查评论质量以 Precision 为核心指标：宁缺毋滥，减少开发者人工确认『假阳性』的成本

## 为什么 (why)

- PR 审查是代码质量的咽喉，手动逐行 review 耗时且易漏，AI 预审把高频问题挡在合并前
- 分支/commit 级触发让审查可以发生在合并前的任意时点，而不仅限于 CI 阶段
- Precision 优先是工程化决策：开发者对每条评论都有确认成本，低精度评论会让人逐渐无视工具输出

## 如何实践 (how)

- 本地审查工作区改动：在仓库目录运行 ocr review，工具自动收集当前改动并产出评论
- 审查分支 diff：ocr review --from main --to feature-branch，无需 checkout 即可审查任意分支间的变更
- 审查单个 commit：ocr review --commit abc123，适合对历史提交定点复核
- 接入 GitHub 自动触发：复制 examples/github_actions/ocr-review.yml 到 .github/workflows/，配置好三个必填输入（llm_url/llm_auth_token/llm_model），PR 事件与 '/open-code-review' 评论即可自动触发
- 利用并发组：并发控制已内置为 ocr-<pr>，同一 PR 反复 push 时不会产生重复审查风暴

## 案例 (cases)

- 日常开发流：提交 PR 后 AI 自动审查，synchronize 时增量复查，开发者专注修评论
- Merge 前复查：在合并按钮前于 PR 评论输入 '/open-code-review' 手动触发一次全量复核
- 分支对比：--from main --to feature-branch 审查特性分支全部改动，无需等待 PR 创建
- 历史提交复核：--commit 对敏感 commit 单独审查，追溯问题引入点

## 反模式/易错点

- 在 GitHub Actions 中把触发权限放开给所有人（不加 MEMBER/OWNER/COLLABORATOR 限制），外部贡献者可用评论触发你的工作流消耗 token
- 忽略并发组配置导致同一 PR 多次触发并发审查，评论重复且账单翻倍
- 只看评论数量不看 Precision，为凑覆盖率引入大量低质量评论，反而增加开发者负担
- 在超大 PR 上直接审查而不依赖 filterLargeDiffs，成本失控且审查质量下降

## 相关关系

| 方向 | 类型 | 关系 |
|---|---|---|
| cli-review → use-pr-review | 前置依赖 | PR 审查场景指向 review 命令 |
| int-gha → use-pr-review | 组合 | Action+review 组合成 PR 自动审查 |
| cli-review → use-pr-review | 组合 | Action+review 组合成 PR 自动审查 |
