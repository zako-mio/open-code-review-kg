# GitHub Actions 集成 (GitHub Actions)

- ID: `int-gha`
- 类型: 工具
- 来源: 集成生态
- 分组: G-E · 集成生态
- 阶段: 进阶 intermediate

> composite action（action.yml）：24 入参/6 出参，fork-safe PR 解析，评论发布脚本（sticky/增量 IoU 去重/路由）

## 核心主张 (what)

- composite action（action.yml）封装完整审查流程，workflow 中一行引用即可接入
- 必填入参：llm_url、llm_auth_token、llm_model、llm_use_anthropic
- 可选入参：language（默认 English）、ocr_version（默认 latest）、review_concurrency、background、rule、upload_artifacts、sticky_summary、incremental（默认 false）、incremental_overlap_threshold（默认 0.6 IoU）、review_comment_batch_size（默认 50）、route_severity_below、route_categories、base_ref、head_sha
- 输出：comments_total、comments_inline、comments_skipped、comments_routed、comments_failed、summary_comment_url
- 流程：fork-safe PR 解析（checkout base + fetch pull/N/head）→ merge-base → ocr review --from MERGE_BASE --to HEAD_SHA --audience agent --format json → post-review-comments.js 发评论
- post-review-comments.js 实现：sticky 摘要、增量 IoU 去重、50 条批量、severity+category 路由，fail-open 设计不丢 finding；upload_artifacts/sticky_summary/incremental 必须用字面字符串 'true'/'false'

## 为什么 (why)

- PR 场景自动审查：push/pull_request 触发即审，评论直达 diff
- fork-safe：外部贡献者 PR 也能正确解析 base 与 head，不因 fork 结构失败
- fail-open：后处理脚本出错也不丢 finding，审查结果可事后回看
- 去重+批量+路由控制评论噪音：IoU 0.6 增量去重、50 条批量、按严重级/类别分流

## 如何实践 (how)

- 基础接入：workflow 中 uses: alibaba/open-code-review@<版本>，配齐 4 个必填入参
- 增量审查：incremental: 'true' 只审新增/变更区域，IoU 阈值用 incremental_overlap_threshold 调（默认 0.6）
- sticky 摘要：sticky_summary: 'true' 固定摘要评论位置
- 路由分流：route_severity_below / route_categories 按严重级/类别分发
- 后台模式：background: true 异步执行不阻塞 CI
- 结果消费：读取 outputs.comments_total/comments_inline 等统计驱动后续步骤
- 版本与语言：ocr_version 指定 CLI 版本，language 指定评论语言
- 并发控制：review_concurrency 限制同时审查的任务数

## 案例 (cases)

- 标准 PR 审查：pull_request 事件 + 4 个必填入参即可上线
- 大型 PR 控噪：incremental 'true' + 调小 review_comment_batch_size + route 分流
- 只关注高危：route_severity_below 屏蔽低危 finding 的评论
- 外部贡献者 fork PR：内置 fork-safe 解析自动处理 base/head

## 反模式/易错点

- 把 incremental/sticky_summary/upload_artifacts 写成布尔 true/false 而非字符串 'true'/'false'，参数解析失效
- fork PR 场景不用内置 fork-safe 解析而自行 checkout，导致 base 分支取错
- 误解 fail-open 语义：后处理失败=审查失败，实际 finding 不丢但评论可能未发
- 不配 route 参数导致所有 finding 全量刷评论，PR 噪音过大
- background 模式忘记收集 outputs，后续步骤拿不到审查统计

## 相关关系

| 方向 | 类型 | 关系 |
|---|---|---|
| int-gha → use-ci | 前置依赖 | CI 场景首选 GitHub Actions |
| int-gha → int-cicd | 变体 | 不同 CI 平台变体 |
| int-gha → use-pr-review | 组合 | Action+review 组合成 PR 自动审查 |
