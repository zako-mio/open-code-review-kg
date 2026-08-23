# 场景：接入 CI 流水线 (Scenario: CI Integration)

- ID: `use-ci`
- 类型: 场景索引
- 来源: 使用场景
- 分组: G-S · 使用场景索引
- 阶段: 进阶 intermediate

> 让审查自动跑在每个 MR/PR：GitHub Actions 一步复用、GitLab/Gerrit 等加 post_review.py 回贴评论

## 核心主张 (what)

- 让 AI 审查自动跑在每次 MR/PR 上，无需人工触发，是规模化落地的标准形态
- GitHub Actions：uses: alibaba/open-code-review@main，三个必填输入 llm_url / llm_auth_token / llm_model，Anthropic 协议模型需加 llm_use_anthropic
- GitLab：在 .gitlab-ci.yml 中配置审查作业，结合 post_review.py 把审查结果回贴为 discussion 评论
- Gerrit / Codeup / GitFlic / Bitbucket 等平台遵循同一模式：CI 作业执行审查 + 脚本回贴结果
- 审查产物：.ocr/ocr-stats.env（统计信息，如评论数/token 数）与 result.json（结构化审查结果），供下游消费
- 配置陷阱：action 输入中 'true'/'false' 必须写成字符串字面量，裸布尔会被 YAML 解析为布尔类型导致传参失败

## 为什么 (why)

- 人工 review 无法保证每个 MR 都覆盖，CI 自动化把审查变成合并的必经环节而非可选项
- 回贴讨论（GitLab discussion / GitHub comment）让审查结论与代码行绑定，开发者在原处即可处理
- 统计产物（ocr-stats.env）支撑团队度量：审查覆盖率、评论密度、token 成本都可量化
- 多平台一致模式降低落地成本：学会一套（Actions）即可复制到其他平台

## 如何实践 (how)

- GitHub Actions 接入：在工作流中 steps 内 uses: alibaba/open-code-review@main，配置 llm_url、llm_auth_token、llm_model 三个必填项，Anthropic 协议模型再加 llm_use_anthropic（注意 'true' 写字符串字面量）
- GitLab 接入：在 .gitlab-ci.yml 新增审查 stage，作业内运行审查命令，随后用 post_review.py 将 result.json 回贴为 MR discussion
- 其他平台：仿照同一模式，CI 作业跑审查 + 读取 result.json + 平台 API 回贴评论
- 消费产物：审查后读取 .ocr/ocr-stats.env 与 result.json，接入通知（如机器人推送摘要）或度量面板
- 配置检查：审查 job 配置中所有布尔型输入用引号包裹（'true'/'false'），避免 YAML 布尔解析问题

## 案例 (cases)

- GitHub 团队落地：每个 PR 自动审查并评论，Precision 优先保证评论值得处理
- GitLab 合规流程：审查结果回贴为 discussion，合并前必须处理高严重度评论
- 多平台统一：同一仓库在 GitLab 与 Gerrit 双平台使用，产物格式一致便于脚本复用
- 度量驱动：CI 产物汇总到面板，按月看评论采纳率与 token 成本趋势

## 反模式/易错点

- 把 llm_auth_token 明文写进工作流文件而非 secrets 注入，凭据随仓库泄漏
- 布尔输入不写字符串字面量：llm_use_anthropic: true 被 YAML 解析为布尔，action 收到类型错误而静默失败
- 忽略 .ocr/ 产物，审查结果只留在日志里，无法被通知/度量/归档消费
- 把回贴脚本写死在审查 job 里而不做失败降级：审查失败时流水线全红，阻塞正常合并

## 相关关系

| 方向 | 类型 | 关系 |
|---|---|---|
| int-gha → use-ci | 前置依赖 | CI 场景首选 GitHub Actions |
| int-cicd → use-ci | 前置依赖 | 其他 CI 平台也支持 |
