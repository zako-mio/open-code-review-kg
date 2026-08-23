# 文件选择与过滤 (File Selection & Filtering)

- ID: `eng-filter`
- 类型: 方法机制
- 来源: 审查引擎
- 分组: G-B · 审查引擎
- 阶段: 进阶 intermediate

> whyExcluded 过滤链：binary→用户 exclude→include 覆盖→扩展名白名单→默认路径黑名单

## 核心主张 (what)

- 文件过滤由 whyExcluded 过滤链完成，按固定顺序执行：binary（二进制）→ 用户 exclude（显式排除）→ 用户 include（显式包含覆盖）→ 扩展名白名单（unsupported_ext）→ 默认路径黑名单（default_path）
- 每条被排除的文件都带 ExcludeReason 记录原因：user_exclude/unsupported_ext/default_path/deleted/binary 五类
- 大小上限 2MiB：超过该体积的文件不进审查流程，防止超大文件撑爆上下文
- 8000 字节二进制嗅探：读取文件前 8000 字节判断是否为二进制，规避误判与二进制内容注入上下文
- 过滤链完全确定性：同一输入必然产生同一过滤结果，可单测、可审计
- 过滤与分派衔接：通过过滤的文件进入分派队列（信号量并发），被过滤文件可经 injectDiffMap 供 file_read_diff 按需读取

## 为什么 (why)

- 二进制文件（图片、编译产物、资源文件）对代码审查无意义且会污染上下文，二进制嗅探（8000 字节采样）比扩展名判断更可靠（改名二进制仍可识别）
- 用户 exclude 处理『我不想审的』，用户 include 处理『默认规则误伤的』，两者构成用户层覆盖能力，且 include 优先级高于 exclude 是明确语义
- 扩展名白名单限定支持语言集合：白名单外的扩展名（unsupported_ext）不进审查，保证审查聚焦于代码文件
- 默认路径黑名单内置常见噪声路径（vendor、依赖目录、生成目录等），开箱即用无需用户配置
- 2MiB 上限是上下文预算的工程保障：大文件即使只进 diff 也消耗巨量 token，上限从源头规避；8000 字节嗅探是性能与准确率的平衡采样

## 如何实践 (how)

- binary 检测：读取文件前 8000 字节做二进制嗅探（NUL 字节/不可打印字符比例），命中即排除并记 ExcludeReason=binary
- 用户 exclude：用户配置的排除路径/模式逐条匹配，命中即排除（ExcludeReason=user_exclude），如明确排除测试目录
- 用户 include：用户 include 配置可覆盖前面排除的条目（ExcludeReason 相应记录），用于把默认/排除规则误伤的文件拉回审查
- 扩展名白名单：文件扩展名不在支持列表内则排除（ExcludeReason=unsupported_ext），如 .min.js、.map、各类生成物
- 默认路径黑名单：路径匹配内置黑名单（依赖/生成/构建目录等）则排除（ExcludeReason=default_path）；deleted 标记用于 diff 中已删除文件
- 大小检查：文件 diff 或内容超过 2MiB 上限直接排除（配合 filterLargeDiffs 的 80% MaxTokens 规则形成双层大文件防线）
- 结果输出：每个文件条目携带是否排除与 ExcludeReason，manifest 中可审计『为什么没审这个文件』

## 案例 (cases)

- 图片被改名成 .go 后缀混进 PR：扩展名白名单无法拦截，但 8000 字节二进制嗅探检测到不可打印内容，按 binary 排除，避免二进制内容进入模型上下文
- 用户仓库依赖 vendor 目录，默认路径黑名单排除之；但某次需要核对 vendor 内特定文件的改动，用户 include 覆盖后该文件进入审查，其余 vendor 文件仍被排除

## 反模式/易错点

- 只用扩展名判断二进制（如 .png/.jpg 列表）——改名二进制绕过白名单，必须用 8000 字节内容嗅探兜底
- include 与 exclude 优先级设计反了——若 exclude 覆盖 include，用户将无法把误伤文件拉回审查，include 覆盖 exclude 是必须语义
- 大文件过滤阈值只依赖 filterLargeDiffs 的 80% MaxTokens——单一大文件即使小于 80% 也可能吃掉大半预算，2MiB 硬上限是必要补充
- 过滤后不记录原因（无 ExcludeReason）——用户无法审计『为什么这个文件没被审』，过滤链的可解释性丢失，排障困难

## 相关关系

| 方向 | 类型 | 关系 |
|---|---|---|
| arch-dispatch → eng-filter | 前置依赖 | 分派先做文件选择过滤 |
| eng-diff → eng-filter | 前置依赖 | 过滤基于解析后的 diff |
| eng-filter → eng-locator | 前置依赖 | 定位发生在保留文件上 |
| eng-filter → arch-dispatch | 组合 | 选择+分束组合成分派 |
