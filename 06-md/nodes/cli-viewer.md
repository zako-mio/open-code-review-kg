# ocr viewer (ocr viewer)

- ID: `cli-viewer`
- 类型: 工具
- 来源: 命令行
- 分组: G-C · 命令行工具
- 阶段: 进阶 intermediate

> 本地 WebUI 会话查看器（默认 localhost:5483）：浏览器回放审查会话 JSONL，hostGuard 防 DNS-rebind

## 核心主张 (what)

- ocr viewer 是 WebUI 会话查看器，以本地网页形式可视化回放审查会话，默认监听 localhost:5483
- 只读回放 session 的 JSONL 数据，不修改任何会话内容，定位为审查过程的回放与审计工具
- 访问路由为 /r/{repo}/{sessionID}，按仓库与会话 ID 直接定位具体审查会话
- 内置 hostGuard 防护机制，防止 DNS-rebind 攻击（恶意域名解析回 localhost 后劫持本地服务）
- 界面按任务类型渲染卡片式视图，任务类型包括 Plan（计划）、Main（主审查）、压缩（context compaction）、重定位（relocation）、反思（reflection）等，还原审查流水线各阶段

## 为什么 (why)

- 命令行只能看到最终评论，无法直观浏览审查过程；viewer 把 JSONL 中的任务流水以卡片可视化，便于理解 AI 的审查步骤与决策路径
- 只读回放天然安全：不会误改会话数据，适合事后审计与向他人展示审查过程
- 默认绑定 localhost 保证审查数据不出本机，hostGuard 再挡一层 DNS-rebind 攻击，兼顾便利与安全

## 如何实践 (how)

- 启动查看器：ocr viewer，默认监听 localhost:5483
- 自定义监听地址与端口：ocr viewer --addr 0.0.0.0:9000（局域网共享时）或 ocr viewer --addr 127.0.0.1:8080
- 浏览器打开 http://localhost:5483，进入 /r/{repo}/{sessionID} 路由回放指定会话
- 结合 ocr session list 获取 repo 与 sessionID，再在 viewer 中定位对应会话
- 按任务类型（Plan/Main/压缩/重定位/反思）浏览卡片，逐阶段查看审查执行流水

## 案例 (cases)

- 审查过程复盘：大型审查完成后用 viewer 打开会话，逐卡片回放 Plan→Main→反思各阶段，理解模型在每个文件的判断依据
- 向同事展示审查结果：局域网内 ocr viewer --addr 0.0.0.0:9000 启动后共享 URL，对方无需安装工具即可查看
- 审计与留档：把本地 viewer 回放作为审查证据链，配合 session JSONL 原始数据留档备查

## 反模式/易错点

- 把 --addr 绑定到公网网卡暴露内网代码：viewer 回放的是完整源码变更内容，绑定 0.0.0.0 且无鉴权时等于把代码公开，应保持 localhost 或仅在可信内网临时使用
- 误以为 viewer 可以编辑/标记会话：viewer 是只读回放，修改会话需回到命令行操作（或另存数据），在界面上找不到编辑入口属正常
- 忘记 hostGuard 存在而测试自定义域名访问：把域名指向 localhost 访问会被 hostGuard 拦截（这是预期行为），本地访问应直接用 localhost/127.0.0.1

## 相关关系

| 方向 | 类型 | 关系 |
|---|---|---|
| eng-session → cli-viewer | 前置依赖 | 查看器回放 JSONL |
| cli-session → cli-viewer | 变体 | 会话管理 CLI 与 Web 查看器 |
