# 其他 CI 集成 (Other CI Integrations)

- ID: `int-cicd`
- 类型: 工具
- 来源: 集成生态
- 分组: G-E · 集成生态
- 阶段: 高级 advanced

> GitLab CI / Gerrit Jenkinsfile / GitFlic CI / Bitbucket Pipelines / 阿里云 Codeup CI + post_review.py 评论回贴

## 核心主张 (what)

- examples/ 目录提供 6 套非 GitHub CI 集成模板：gitlab_ci、gerrit_ci、gitflic_ci、bitbucket_pipelines、codeup_ci
- gitlab_ci：.gitlab-ci.yml + post_review.py，环境变量 OCR_LLM_URL/OCR_LLM_TOKEN/OCR_LLM_MODEL + 重试系列 OCR_RETRY_BASE_DELAY/OCR_MAX_RETRIES + OCR_STICKY_SUMMARY/OCR_INCREMENTAL/OCR_ROUTE_*/OCR_FAIL_ON_SEVERITY
- gitlab_ci 产物：.ocr/ocr-stats.env + result.json + stderr.log，支持 fork MR
- gerrit_ci：Jenkinsfile + post_review.py
- gitflic_ci：gitflic-ci.yaml + post_review.py
- bitbucket_pipelines：bitbucket-pipelines.yml；codeup_ci：阿里云 Codeup codeup-flow.yml + post_review.py

## 为什么 (why)

- 覆盖国内常用平台：阿里云 Codeup、GitLab、Bitbucket 等，多平台审查体验一致
- 环境变量式配置天然适配各 CI 平台的 secrets/变量注入机制
- gitlab_ci 支持 fork MR，保证开源协作场景可用

## 如何实践 (how)

- GitLab：参考 examples/gitlab_ci/.gitlab-ci.yml 配置 job，变量经 GitLab CI/CD Variables 注入
- 重试控制：OCR_RETRY_BASE_DELAY 与 OCR_MAX_RETRIES 配合调 API 重试策略
- 增量/粘性对齐：OCR_INCREMENTAL / OCR_STICKY_SUMMARY 行为与 GHA 版一致
- 路由：OCR_ROUTE_* 系列按严重级/类别分流 finding
- 失败策略：OCR_FAIL_ON_SEVERITY 设定达到某严重度即令 CI 失败
- 阿里云用户：直接套用 examples/codeup_ci/codeup-flow.yml
- 结果消费：解析 .ocr/ocr-stats.env 与 result.json 供下游步骤使用

## 案例 (cases)

- GitLab 私有仓库 MR 审查：gitlab_ci 模板 + CI/CD Variables 注入三件套
- 阿里云 Codeup 用户：codeup-flow.yml 开箱即用
- Gerrit 评审流：Jenkinsfile + post_review.py 集成
- fork MR 场景：gitlab_ci 支持 fork MR 解析

## 反模式/易错点

- 忘记设置 OCR_LLM_URL/OCR_LLM_TOKEN/OCR_LLM_MODEL 三件套，任务启动即鉴权失败
- 不配重试参数：网络抖动时一次性失败；OCR_MAX_RETRIES 应配合 OCR_RETRY_BASE_DELAY 使用
- 乱设 OCR_FAIL_ON_SEVERITY：低危问题也会让 CI 失败，阻塞流水线
- CI 清理策略删掉 .ocr/ 产物目录，result.json/stderr.log 丢失无法事后排查
- 照抄 GHA 的输入参数名（如 llm_url）到其他 CI：非 GitHub 集成用 OCR_* 环境变量体系，混用不生效

## 相关关系

| 方向 | 类型 | 关系 |
|---|---|---|
| int-cicd → use-ci | 前置依赖 | 其他 CI 平台也支持 |
| int-gha → int-cicd | 变体 | 不同 CI 平台变体 |
