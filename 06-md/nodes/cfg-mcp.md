# MCP 扩展 (MCP Extension)

- ID: `cfg-mcp`
- 类型: 方法机制
- 来源: 配置模型
- 分组: G-D · 配置与模型
- 阶段: 高级 advanced

> Model Context Protocol：stdio 子进程 + remote Streamable HTTP 双传输，外部工具接入审查工具链（allowlist 过滤）

## 核心主张 (what)

- 通过 Model Context Protocol（MCP）接入外部工具，扩展模型能力
- 双传输：stdio 子进程（mcp.CommandTransport）+ remote Streamable HTTP（headerTransport）
- remote 的 headerTransport 支持 $ENV_VAR 环境变量展开，且对 401/403 返回友好报错
- config.json 的 mcp_servers.<name> 配置节点：type(stdio\|remote)、command、args、env、url、headers、tools、setup 字段
- RegisterAll 注册时带 allowlist 过滤，保留名冲突自动跳过（不覆盖内置工具）
- 工具经 ToToolDef 转换为 llm.ToolDef 接入统一工具调用链路，基于 github.com/modelcontextprotocol/go-sdk 实现

## 为什么 (why)

- 让审查模型能调用外部工具（漏洞库查询、内部 API 等），突破纯文本审查边界
- stdio 与 remote 双模式覆盖本地子进程与远端服务两种部署形态
- 安全边界：allowlist 过滤 + 保留名冲突跳过，防止恶意或重复工具定义干扰

## 如何实践 (how)

- stdio 模式：mcp_servers.<name> 配 type=stdio + command/args/env，启动子进程 MCP server
- remote 模式：type=remote + url 走 Streamable HTTP，headers 中用 $ENV_VAR 注入密钥
- 工具过滤：tools 字段列允许的工具名；setup 字段做启动准备
- 冲突规避：RegisterAll 遇保留名自动跳过，无需手动处理
- 鉴权排障：401/403 时查看友好报错信息定位问题
- 验证工具接入：确认工具经 ToToolDef 转换后在模型工具列表中可见

## 案例 (cases)

- 接入本地 CLI 型 MCP server：stdio 模式拉起子进程
- 接入远端 MCP 网关：remote + HTTP，headers 里 $TOKEN 展开注入密钥
- 白名单管控：tools 字段只开放少量工具，缩小攻击面
- 企业内部工具：私有 MCP server 挂入审查链路

## 反模式/易错点

- 密钥明文写进 headers 而非用 $ENV_VAR 展开，造成密钥泄露
- 忽略 401/403 友好报错：鉴权失败应看报错提示定位，而非盲目重试
- 自定义工具与内置工具重名：RegisterAll 会跳过保留名冲突，误以为注册成功
- stdio 模式没配全 command/args/env，子进程启动失败且无明确提示
- 不配 tools allowlist：工具面过大引入不必要的安全风险

## 相关关系

| 方向 | 类型 | 关系 |
|---|---|---|
| cfg-mcp → use-extend | 前置依赖 | 扩展场景可接 MCP |
