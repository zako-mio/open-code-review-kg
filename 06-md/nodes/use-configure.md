# 场景：配置模型与规则 (Scenario: Configure & Rules)

- ID: `use-configure`
- 类型: 场景索引
- 来源: 使用场景
- 分组: G-S · 使用场景索引
- 阶段: 进阶 intermediate

> 首次上手必做：选 provider/模型/API Key，按项目定制规则（rule.json）、过滤路径、调并发与预算

## 核心主张 (what)

- 首次上手必做步骤：配置模型提供方与审查规则，决定审查的语言、范围与标准
- ocr config provider 选择模型提供方：内置 DashScope、DeepSeek 等选项，也支持自定义端点接入任意兼容服务
- ocr config model 配置具体模型，工具会自动测试连通性，失败即反馈，避免配错模型名
- ocr config set language zh-CN 设置审查语言（如中文输出评论）
- 项目级规则文件 .opencodereview/rule.json：include/exclude 控制文件范围 + 规则内容，路径匹配用 doublestar glob（支持 ** 多级匹配）
- 全局规则 ~/.opencodereview/rule.json：跨项目生效的默认规则；--rule 提供临时规则，单次命令生效
- ocr rules check 验证规则命中：确认规则确实匹配到了目标文件，避免规则写错而静默失效

## 为什么 (why)

- 审查质量的上限由模型与规则决定：不配置模型则无法运行，不配置规则则审查无差异化
- 项目级与全局级分层让『团队标准』与『个人偏好』共存：全局规则兜底，项目规则精确
- 连通性自动测试与 rules check 都是防『静默失败』设计：配错模型/规则当场报错而非审查时才发现

## 如何实践 (how)

- 配置模型：ocr config provider 选择内置 provider（如 DashScope/DeepSeek）或按自定义端点配置 → 随后 ocr config model 指定模型并自动测连通
- 设置语言：ocr config set language zh-CN，让审查评论以中文输出
- 配置项目规则：在仓库根目录编写 .opencodereview/rule.json，include/exclude 用 doublestar glob（如 **/internal/**）限定范围，并填写规则内容
- 配置全局规则：在 ~/.opencodereview/rule.json 编写跨项目默认规则，新仓库自动继承
- 临时规则：单次命令加 --rule，如 ocr review --rule '禁止硬编码密钥'，不污染仓库配置
- 验证规则：运行 ocr rules check，确认规则命中目标文件，输出与实际匹配一致后再正式审查

## 案例 (cases)

- 团队统一标准：项目 .opencodereview/rule.json 内置团队编码规范（如禁止 TODO 合并、必须错误处理），所有开发者共享
- 个人偏好：全局规则加入个人关注点（如注释语言、命名风格），跨项目生效
- 新成员上手：按 provider → model → language 顺序完成配置，rules check 确认规则生效后即可开始审查
- 多语言仓库：include/exclude 配合 doublestar glob 限定仅审查 Go/Python 目录，避免无关文件噪音

## 反模式/易错点

- 跳过 ocr config model 的连通性测试直接使用，配错模型名/端点后审查静默失败，排查成本高
- doublestar glob 写错（如用单 * 期望匹配多级目录），include/exclude 不生效，规则范围失控
- 规则写好后不跑 ocr rules check，等审查时才发现规则从未命中目标文件
- 把全局与项目规则语义混淆：想项目内生效却写入全局文件，污染其他仓库的审查行为

## 相关关系

| 方向 | 类型 | 关系 |
|---|---|---|
| cfg-providers → use-configure | 组合 | provider+config 命令组合成配置场景 |
| cli-config → use-configure | 组合 | provider+config 命令组合成配置场景 |
