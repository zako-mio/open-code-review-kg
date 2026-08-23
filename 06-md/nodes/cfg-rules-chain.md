# 四层规则链 (Four-layer Rule Chain)

- ID: `cfg-rules-chain`
- 类型: 方法机制
- 来源: 配置模型
- 分组: G-D · 配置与模型
- 阶段: 进阶 intermediate

> custom(--rule) > project(.opencodereview/rule.json) > global(~/.opencodereview/rule.json) > system(内嵌)，doublestar glob 匹配

## 核心主张 (what)

- 四层规则链，优先级：custom（--rule 旗标）> project（<repo>/.opencodereview/rule.json）> global（~/.opencodereview/rule.json）> system（内嵌 system_rules.json + rule_docs/ 44 个语言规则 md）
- 首匹配优先：规则命中时按层序取最上层匹配
- 文件匹配支持 doublestar glob（** 递归匹配任意层目录）+ 花括号 {a,b} 展开
- merge_system_rule 选项控制是否合并系统内置规则
- 规则值可引用 .md/.txt 文件路径作为内容源；相对路径机制防目录穿越
- CanonicalConfig() 生成 rule_config_sha256 规则指纹；内置 10+ 语言规则集（Java/TS/Go/Python/Kotlin/Rust/C++/C）及 NPE、线程安全、XSS、SQL 注入专项规则

## 为什么 (why)

- 分层治理：个人/团队/仓库/内置四层隔离，不同范围各自演进不互相污染
- 多语言与专项安全规则开箱即用，无需从零编写
- glob 语法贴近开发者习惯（gitignore 风格），可精确圈定审查文件范围

## 如何实践 (how)

- 项目级：仓库根建 .opencodereview/rule.json 定义规则
- 全局级：~/.opencodereview/rule.json 供所有项目共享
- 临时级：ocr review --rule <自定义规则文件路径>
- 文件匹配：glob 支持 **（如 **/src/**/*.java）与 {a,b}（如 *.{ts,tsx}）
- 规则内容外置：rule 值指向 .md/.txt 路径（仅相对路径，防目录穿越）
- 系统规则控制：merge_system_rule 决定是否合并内置规则
- 验证指纹：CanonicalConfig() 输出的 rule_config_sha256 用于确认规则集版本与缓存一致性

## 案例 (cases)

- 团队统一规范：global 层放团队通用规则，项目层放仓库特有规则
- 专项安全审查：启用 NPE/线程安全/XSS/SQL 注入专项规则集
- 按语言分流：Java 规则匹配 **/*.java，TS 规则匹配 **/*.{ts,tsx}
- 长规则文本外置：写入 .md 文件，rule.json 只引用路径

## 反模式/易错点

- glob 写错导致规则静默失效：用 * 而非 ** 时匹配不到多层目录下的文件
- 误改 ~/.opencodereview/rule.json 以为是项目配置：实际影响本机所有项目
- 关闭 merge_system_rule 后安全专项规则（NPE/XSS 等）全部消失
- 规则值引用绝对路径或越级相对路径造成目录穿越风险：必须只用受限相对路径
- 多层同名规则并存时靠首匹配优先裁决：理解错层序会得到预期外的审查行为

## 相关关系

| 方向 | 类型 | 关系 |
|---|---|---|
| arch-dispatch → cfg-rules-chain | 前置依赖 | 规则链是分派的数据源 |
| cfg-rules-chain → cli-rules | 前置依赖 | rules 命令调试规则链 |
| cfg-rules-chain → use-extend | 前置依赖 | 扩展场景可加规则 |
