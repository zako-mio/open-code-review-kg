# ocr llm (ocr llm)

- ID: `cli-llm`
- 类型: 工具
- 来源: 命令行
- 分组: G-C · 命令行工具
- 阶段: 高级 advanced

> LLM 工具：test 发送测试对话、providers 列出全部 27 个内置 provider

## 核心主张 (what)

- ocr llm 是 LLM 工具命令，用于模型层的连通性验证与能力查询，是排查模型配置问题的第一站
- 子命令 test：发送测试对话验证模型连通性，覆盖 API key 有效性、网络可达性、模型名正确性、响应解析等环节
- 子命令 providers：列出全部 27 个内置 provider 及其信息，供核对 provider 名称与字段配置
- 与 ocr config 联动：配置改动（set provider/model 等）后可用 ocr llm test 立即验证是否生效
- 在 review/scan 前先行 test，可将模型层问题与工具层问题快速隔离

## 为什么 (why)

- 模型配置错误（key 失效、网络不通、模型名拼错、baseURL 错误）是审查失败的最高频根因，独立 test 命令把这类问题从完整审查流程中剥离出来
- 27 个内置 provider 的名称与字段容易记错，providers 子命令提供权威清单，避免配置时编造名称
- test 失败信息聚焦模型层（认证/网络/模型名），比在 review 的超长日志中翻找根因高效得多

## 如何实践 (how)

- 验证当前配置连通性：ocr llm test，观察返回的测试对话结果或错误信息
- 列出内置 provider：ocr llm providers，核对当前 provider 名称是否在清单内
- 确认 provider 后修正配置：ocr config set provider <name> 与 ocr config set model <model-id>
- 修正后复测：再次 ocr llm test，确认认证与响应正常后再进入 review/scan
- 多 provider 切换验证：分别配置后用 ocr llm test 逐一验证，选出可用的模型组合

## 案例 (cases)

- 401 报错排查：review 报认证失败，先 ocr llm test 确认是 API key 无效，再用 ocr config set providers.<name>.apiKey 更新后复测通过
- 新提供商接入：先 ocr llm providers 确认真实名称，再按清单字段配置 custom_providers 或官方字段，最后 test 验证
- 网络环境变更后恢复：换网络后 review 全挂，ocr llm test 秒级定位网络层问题，处理后再继续
- review 前预热：CI 中先 ocr llm test 快速失败（fail fast），避免整轮 review 因模型不可用而空耗

## 反模式/易错点

- 跳过 test 直接 review：模型不可用时整轮 review 在超时后才失败，浪费大量时间与上下文，应先 test 秒级验证
- 编造 provider 名称：凭记忆输入不存在的 provider 名，配置静默不生效，应先 ocr llm providers 核对清单
- 忽视 test 的失败细节：test 错误信息区分了认证/网络/模型名三类问题，笼统地反复改 key 而不看错误类别，导致问题无法收敛，应按错误类别对症修改

## 相关关系

| 方向 | 类型 | 关系 |
|---|---|---|
| cfg-providers → cli-llm | 前置依赖 | llm providers 列出内置注册表 |
