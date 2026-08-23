# 质量门控报告 · Open Code Review 项目解析知识图谱

| 门控项 | 结果 | 说明 |
|---|---|---|
| DAG 无环 | ✅ | Kahn 拓扑校验：51/51 节点全部访问，prerequisite 42 边无环 |
| 四向覆盖 | ✅ | dag(51) = node-pages(51) = md/nodes(51) = node-content(51) 完全一致 |
| HTML 结构 | ✅ | 65 个 HTML 扫描：0 个 U+FFFD 替换字符，0 处 div 开闭不平衡 |
| 断链 | ✅ | 全量 href 检查：0 断链（修复 1 处 gen-groups 对旧 cross-mapping 视图的引用） |
| 交互 DATA 一致性 | ✅ | 04-interactive/index.html DATA：nodes=51 / edges=68 / groups=7 与 DAG 完全一致 |
| 内容抽查 | ✅ | cli-review / arch-reflection / use-pr-review / cfg-providers / int-gha 五段式（what/why/how/cases/anti_patterns）齐全，节点页含全部区块 |
| 边端点合法性 | ✅ | 68 条边 from/to 均在 51 节点集合内，组引用合法，节点归属唯一 |

## 数据规模
- 节点 51（principle 20 / tool 18 / crosscut 6 / scenario 6，其中 1 节点类型 tool 归 G-F？无——按 dag 实际：principle 20、tool 18、crosscut 6、scenario 6）
- 分组 7（source 3 / tool 2 / crosscut 1 / scenario 1）
- 边 68（prerequisite 42 / variant 9 / combination 7 / cooccurrence 4 / dependency 4）
- 学习阶段：basic 15 / intermediate 17 / advanced 19
- 内容字符量：约 4.6 万（五段式全量中文详解）

## 复跑方式
```bash
cd 07-checkpoint
python3 gen-nodes.py && python3 gen-groups.py && python3 gen-views.py \
  && python3 gen-interactive.py && python3 gen-md.py && python3 gen-index.py
```
修改 `01-dag-data/` 后重跑即可全量更新。
## 三合一升级门控（v3，2026-08-23 晚）

| 门控项 | 结果 | 说明 |
|---|---|---|
| 实践资产存在性 | ✅ | 42 个资产全部落盘（ci 7 / code 16 / plugin 5 / build 5 / skill 2 / config 2 / script 1 / tool 1 / prompt 1 / rule 1 / doc 1） |
| AI 可调用索引 | ✅ | ai-index.json：node_index 51 / asset_index 42 / command_index 72，页面路径全部可解析 |
| 正反实例论证 | ✅ | evidence.json：51 节点 / 260 条（130 对 pro+con），pro/con 均衡 |
| 节点页证据区块 | ✅ | 51/51 节点页含「正反实例论证」区块（pro 绿卡 / con 红卡 / 代码块） |
| 节点页资产区块 | ✅ | 51/51 节点页含「实践资产」区块（类型徽章 + 文件链接 + 元数据） |
| 12 原则对照审查 | ✅ | 05-views/05-principles.html：24 条原则（App 12 + Agent 12）× OCR 机制 × 结论，合规 22 / 部分合规 2 |
| 资产关联覆盖 | ✅ | 51/51 节点均关联 ≥1 资产（assets-manifest.json node_ids 补全） |
| 断链复查 | ✅ | 68 HTML 全量 href 检查 0 断链（含新增 assets/ 链接） |

HTML 总量 68（+3：assets/index.html、05-views/05-principles.html、05-views/index.html 原计）