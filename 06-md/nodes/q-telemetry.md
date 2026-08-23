# OpenTelemetry 遥测 (OpenTelemetry Telemetry)

- ID: `q-telemetry`
- 类型: 工程保障
- 来源: 工程保障
- 分组: G-F · 工程保障
- 阶段: 高级 advanced

> console/OTLP 双导出（grpc/http），审查事件与指标埋点，OCR_ENABLE_TELEMETRY 环境变量开启

## 核心主张 (what)

- OCR 内置 OpenTelemetry 双管道（trace + metric），所有审查事件与指标均通过统一遥测框架埋点
- 支持两种导出方式：console 输出（本地调试直观可见）与 OTLP 导出（gRPC / HTTP-protobuf / HTTP-JSON 三种 wire protocol）
- 配置优先级为 defaults < config.json 的 telemetry 段 < 环境变量，环境变量拥有最终覆盖权
- 核心环境变量：OCR_ENABLE_TELEMETRY=1 开启遥测、OTEL_SERVICE_NAME 服务名、OTEL_EXPORTER_OTLP_ENDPOINT OTLP 端点、OTEL_EXPORTER_OTLP_PROTOCOL 协议选择、OCR_CONTENT_LOGGING=1 输出审查内容日志
- 埋点覆盖完整审查生命周期：任务开始/结束、每次模型调用、检索/过滤/压缩各阶段、token 消耗与重试事件
- metric 侧聚焦成本与性能：token 计数、耗时、重试次数等可观测指标，便于与成本分析（token 计费）联动

## 为什么 (why)

- 审查流程横跨本地文件读取、git 操作、模型 API 调用等多个环节，无遥测则故障只能靠黑盒排查，定位慢
- token 消耗是成本核心，通过 metric 管道持续观测 token 用量才能做成本治理与预算预警
- 支持 OTLP 导出意味着可无缝接入现有可观测性平台（Jaeger/Tempo/Prometheus 等），企业级集成零成本
- 环境变量优先的配置设计让 CI/CD 场景下无需改配置文件即可按流水线注入遥测开关

## 如何实践 (how)

- 本地快速验证：设置 OCR_ENABLE_TELEMETRY=1 后运行 ocr review，在 console 观察 trace 输出，确认埋点链路完整
- 接入 OTLP 平台：设置 OCR_ENABLE_TELEMETRY=1、OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4318、OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf，启动后到平台查看 span
- 切换协议：按需将 OTEL_EXPORTER_OTLP_PROTOCOL 设为 grpc 或 http/json，匹配后端 Collector 的接收端口
- 命名服务：设置 OTEL_SERVICE_NAME 区分不同仓库/流水线的遥测数据，避免多项目数据混淆
- 审计内容：设置 OCR_CONTENT_LOGGING=1 记录审查内容，用于事后核查模型看到了什么（注意隐私合规）
- 通过 config.json 的 telemetry 段配置默认值，再按环境用环境变量覆盖，形成可复用的分层配置

## 案例 (cases)

- 本地调试：开启 console 输出，排查某次审查为何未产出评论，从 trace 中定位是检索失败还是模型调用异常
- 接入企业 APM：CI 中注入 OTLP 端点，让每次 MR 审查的 token 消耗与耗时进入统一大盘，按服务名区分项目
- 成本审计：通过 metric 中的 token 计数与重试次数，验证 prompt-cache 命中率与重试开销
- 回归对比：升级模型或改规则后，对比前后 trace 中各阶段耗时，量化优化效果

## 反模式/易错点

- 在 CI 中误用 config.json 配置遥测而忽略环境变量注入，导致每个流水线任务覆盖不生效或泄露本地配置
- OCR_CONTENT_LOGGING=1 与 OTLP 出口同时开启却未考虑数据合规：源码内容可能被导出到远端平台，生产环境需谨慎或脱敏
- 协议选错导致数据静默丢失：OTLP 端点与协议不匹配（如 gRPC 端点了却配 http/json）时无报错但无数据，排查时先核对协议与端口
- 未设置 OTEL_SERVICE_NAME 就把多仓库数据混入同一 Collector，后续无法按项目拆分指标

## 相关关系

| 方向 | 类型 | 关系 |
|---|---|---|
| q-telemetry → eng-session | 共现 | 会话 JSONL 是遥测素材 |
