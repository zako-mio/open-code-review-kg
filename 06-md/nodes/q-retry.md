# 重试与错误分类 (Retry & Error Classification)

- ID: `q-retry`
- 类型: 工程保障
- 来源: 工程保障
- 分组: G-F · 工程保障
- 阶段: 高级 advanced

> SDK 内建 max-retries=5 + 可配置 RetryCodes；错误按 ErrorClass(timeout/cancelled/network/provider/unknown)+FailurePhase 分类入报告

## 核心主张 (what)

- 底层 SDK 内建 max-retries=5 重试策略，配合 retryCodesMiddleware 自动注入 x-should-retry 头驱动服务端重试语义
- retryObserver 采集每次 HTTP 尝试的明细（次数、耗时、结果），为重试报告提供数据源
- retry_boundary.go 提供 classifyBoundaryError / classifyStreamError 两类分类器，将错误归入 ErrorClass（timeout/cancelled/network/provider/unknown）并标注 FailurePhase（失败发生在哪个阶段）
- retry_report 汇总生成重试报告，展示各错误类别的重试次数与最终成败
- RetryCodes 可配置：允许自定义哪些 HTTP 状态码触发重试，适配不同 provider 的语义
- OCR_RETRY_* 环境变量族（GitLab 示例中可见）可在不改代码的情况下调节重试行为

## 为什么 (why)

- LLM API 是外部依赖，超时/限流/网络抖动是常态，无重试则一次抖动就导致整个审查失败
- 不同失败原因应对策略不同：网络错误值得重试，provider 侧 4xx 重试无意义——错误分类让重试策略有的放矢
- 把 ErrorClass 与 FailurePhase 分离，才能在报告中区分『重试后成功』与『彻底失败』，为成本与稳定性分析提供依据

## 如何实践 (how)

- 使用默认策略：无需配置即生效 max-retries=5 与 x-should-retry 注入，多数场景可直接依赖
- 调优重试：按 provider 语义配置 RetryCodes，如把 429 限流码与 5xx 服务端码加入重试集合
- 环境变量覆盖：通过 OCR_RETRY_* 系列变量在 CI 或生产环境调整重试参数，避免改代码重新发布
- 诊断失败：查看 retry_report，按 ErrorClass 分组定位是 timeout/network 还是 provider 侧问题，再决定调重试还是换 provider
- 结合遥测联动：重试次数与耗时进入 metric 管道，与 token 成本一起评估重试的经济性

## 案例 (cases)

- 模型 API 限流：429 命中 RetryCodes，自动退避重试后审查成功，报告显示重试 2 次均为 429
- 网络抖动：无重试时整批审查失败；开启重试后 classifyBoundaryError 识别为 network 类并成功恢复
- Provider 故障升级：报告显示 provider 类错误占大头且重试全失败，据此决策切换到备用模型端点
- CI 长任务稳定性：OCR_RETRY_* 注入让 5 次重试覆盖深夜限流高峰，减少人工重跑

## 反模式/易错点

- 把所有状态码都加入 RetryCodes：4xx 客户端错误（如 401/403）重试永远失败，纯浪费 token 与时间
- 忽略 retry_report 直接看表面报错：不区分 ErrorClass 就盲目调大重试次数，掩盖 provider 侧真实问题
- 在无重试语义的自建服务上依赖 x-should-retry，服务端不识别导致重试行为与预期不符
- 重试与超时配置不匹配：重试次数过多而单次超时过短，反而放大整体耗时
