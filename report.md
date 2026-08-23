# Mission 报告：Open Code Review 项目解析知识图谱

- **日期**: 2026-08-23
- **任务目录**: `~/opencode/archive/Mission-file/2026-08/0823-open-code-review/`
- **GATE**: 范围=5 深度=5 操作=5 风险=2 → 总分=17 → Deep

## 一、当时情况

用户提出"查找 GitHub 开源项目 Open Code Review（据说是阿里团队的代码审查工具）并深入了解"。第一轮调研子Agent 确认项目为 `alibaba/open-code-review`（21k+ star、Apache-2.0、Go 编写、源自阿里内部两年规模化验证的 AI 代码审查 CLI）。随后用户在选择留档方式时明确指示："下载到留档目录，参考最近的知识图谱任务，对该项目进行全面解析"，并在交付规模确认中选择**全套知识图谱**，要求"每个叶子 HTML 用 what-why-how 法则解释，要全面而且详细，同时该知识图谱也应该能够作为工具库索引"。

## 二、制定计划

1. GATE 自评 17 分 → Deep variant。
2. **下载**：git clone --depth 1 源码到留档目录（吸取 0823-12factor项目 教训：HTTP/1.1 降级、无管道吞错、显式验证工作树）。
3. **源码级解析**：双路并行 explore 子Agent——核心引擎（internal/agent、llmloop、tool、diff、gitcmd、scan、suggestdiff、session、viewer）与外围集成（cmd CLI、config、llm、model、delegate、mcp、telemetry、action.yml、examples、plugins、skills、npm/发布、go.mod）。
4. **图谱设计**（主 Agent）：51 节点 / 7 组 / 68 边；分组 = 核心架构 / 审查引擎 / 命令行工具 / 配置模型 / 集成生态 / 工程保障 / **使用场景索引**（G-S 承担"工具库索引"需求）；每节点五段式内容。
5. **内容创作**：6 路并行 general 子Agent，每路 7-11 节点，prompt 内置一手源码事实要点防编造；子Agent 会话内落盘片段（resume task），主 Agent 聚合校验。
6. **生成脚本**：复用 0823-12factor-methodology 的 07-checkpoint 全套脚本（gen_common/gen-nodes/gen-groups/gen-interactive/gen-md/gen-index），批量适配数据路径/样式体系；**重写 gen-views.py**（场景索引视图为核心新增）+ 重写 gen-index.py。
7. **质量门控**：DAG 无环（Kahn）/ HTML 结构（UTF-8 无 U+FFFD、div 平衡）/ 断链 / 四向覆盖（dag↔pages↔md↔content）/ 交互 DATA 一致性 / 内容抽查。
8. **报告**：report.md + report.html 双版本。

## 三、执行情况

1. **clone**：首次 clone 超时 300s（无残留），ls-remote 探路确认网络通，改用 `git -c http.version=HTTP/1.1 -c http.postBuffer=524288000` 重试成功，772 文件，验证工作树非空。
2. **源码分析**：两个 explore 子Agent 返回超详报告（agent.go 1899 行核心、REVIEW_FILTER 反思五步法、行号五级回退链、三区压缩、27 provider/4 协议/5 级配置优先级、GitHub Action 24 入参、6 套 CI 示例、6 个 Agent 插件、AACR-Bench 基准等）。
3. **图谱数据**：主 Agent 手写 opencodereview-dag.json（51 节点/7 组/68 边），脚本预检通过（无环/无坏引用）。
4. **内容创作**：6 路并行子Agent 全部 success；发现片段落盘时并行子Agent 脚本名冲突（/tmp/opencode 共享目录），子Agent 自愈（唯一文件名）。聚合后 51/51 节点匹配、无缺失无多余、字段全非空。
5. **脚本适配**：adapt_scripts.py 批量替换 5 个脚本（含 2 处修复：src_badge 默认值引用已删除的 'bridge' 键、learning_html 误用节点索引取组名）。
6. **生成**：51 节点页 + 7 组页 + 4 视图（场景索引 18KB）+ 交互 DAG + 51 MD + 根入口全部成功。
7. **门控**：首轮发现 2 个问题——①门控脚本自身 bug（'open-code-review' in root 误排除全部 HTML，修复为精确路径判断）②1 处断链（gen-groups 残留对旧 04-cross-mapping.html 引用，改为 04-architecture.html）。复查全 PASS。
8. **报告**：report.md 手写；report.html 委派子Agent 生成（走 HTML 质量门控）。

## 四、完成情况

| 交付物 | 规模 | 位置 |
|---|---|---|
| 源码 clone | 772 文件 | `open-code-review/` |
| DAG 数据 | 51 节点/7 组/68 边 + stats.md | `01-dag-data/` |
| 节点页 | 51 页（五段式：what/why/how/案例/反模式） | `02-node-pages/` |
| 组页 | 7 组页 + 组总索引 | `03-groups/` |
| 交互 DAG | cytoscape + dagre（51/68/7） | `04-interactive/` |
| 视图 | 场景索引（工具库索引）/ 学习路径 / 架构分层 / 入口 | `05-views/` |
| MD 镜像 | 00-index + 01-groups + 02-stage + 03-learning-path + 51 节点 | `06-md/` |
| 生成脚本 | 9 个（可复跑） | `07-checkpoint/` |
| 根入口 | index.html | 根目录 |
| 报告 | report.md + report.html | 根目录 |

质量门控 7 项全 PASS。用户核心需求落实：①叶子页五段式详述（51 页平均约 900 字/页）②G-S 使用场景索引视图（场景→命令速查→关联节点，兼作工具手册）。

## 五（补）、三合一升级（2026-08-23 晚，用户二轮需求）

用户提出升级：图谱不应只承载知识，应携带**全部实践源码资产**与 **AI 可调用索引**，升级为「知识 + 实践 + 工具索引」三合一；且叶子页知识承载量要充足（正反实例论证 + 实践工具索引）。

1. **实践资产层**：gen-assets-extract.py 从源码精选 42 个资产（CI 示例 7 / 源码节选 16 / 插件 5 / 构建 5 / Skill 2 / 配置示例 2 自建 / 脚本 1 / 工具 schema 1 / 提示词 1 / 规则 1 / 文档 1）复制/节选到 assets/；大文件（agent.go 1899 行等）自动节选为「头部 + 关键符号表」MD。
2. **正反实例论证**：恢复 6 个内容创作会话（保留上下文），基于自写五段式内容补充 evidence——51 节点 / 260 条（130 对 pro+con），命令类节点用真实 ocr 参数，机制类用伪代码/diff 论证。
3. **AI 可调用索引**：ai-index.json 三段式（node_index 51 + asset_index 42 + command_index 72），节点→命令→资产→页面全连通；命令提取用「ocr + 已知子命令」正则过滤噪音。
4. **叶子页增强**：gen-nodes.py 注入两个新区块——「正反实例论证」（pro 绿卡/con 红卡 + 代码块）与「实践资产」（类型徽章 + 文件链接 + 元数据），51/51 全渲染；资产关联补全至 51/51。
5. **12 原则应用**：用户指示学习 12factor-methodology 的 12 原则并应用——精读 00-index.md 提取 24 条原则（App 12 + Agent 12），设计 principles-mapping.json 逐条对照 OCR 机制给出审查结论（合规 22 / 部分合规 2），生成 05-views/05-principles.html + 06-md/05-principles.md；审查发现 OCR 与 12 Factor Agent 高度同构（ag-control/ag-context/ag-small/ag-reducer 全合规）。
6. **门控 v3**：新增 8 项校验（资产存在/索引合法/证据覆盖/区块渲染/原则视图），全 PASS；68 HTML 0 结构问题 0 断链。

## 五、反思 / 分析 / 建议

1. **知识图谱模式复用效率极高**：12factor-methodology 的脚本骨架（gen_common + 5 生成器 + vendor）在仅改样式映射/路径后即可支撑全新项目图谱，本次从零到全量交付约 40 分钟。建议沉淀"项目解析图谱"标准模板（含场景索引视图），后续项目直接套用。
2. **"工具库索引"需求的新解法**：在标准五层骨架上新增 G-S 场景组 + 05-views/02-scenarios.html 命令速查视图，把"理解型图谱"升级为"可用型手册"。场景节点与工具节点用 prerequisite/combination 边互联，索引与架构自然打通。
3. **并行子Agent 写文件的共享目录冲突**：/tmp/opencode 下多个子Agent 用同名脚本/输出文件会互相覆盖（本次 B/F 路都踩到）。规则应固化为：并行任务的文件名必须唯一（按片段号命名），或统一让主 Agent 写聚合。
4. **门控脚本自身也要门控**：首轮门控因 walk 排除条件误伤（'open-code-review' 出现在基目录路径中）导致 HTML=0 假 PASS，复查才暴露。排查逻辑：门控输出与预期数量差异巨大时（65 vs 0）先怀疑门控本身。
5. **Reflection 联动**：本任务可沉淀经验——多路内容创作委派的 prompt 要点（内置一手事实防编造）、五层骨架复用清单、工具索引视图设计模式。待用户 /reflection 审阅后写入 MEMORY.md。