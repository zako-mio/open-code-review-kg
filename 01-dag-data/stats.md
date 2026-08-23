# Open Code Review 图谱统计

| 指标 | 值 |
|---|---|
| 节点总数 | 51 |
| 分组数 | 7 |
| 关系边 | 68 |
| 内容字符量 | 76,466 |
| 节点类型 | crosscut 6, principle 21, scenario 6, tool 18 |
| 边类型 | combination 9, cooccurrence 4, dependency 4, prerequisite 42, variant 9 |
| DAG 无环 | Kahn 校验通过 |

## 分组

- **G-A** 核心架构（架构理念）：6 节点
- **G-B** 审查引擎（核心机制）：10 节点
- **G-C** 命令行工具（CLI）：9 节点
- **G-D** 配置与模型（配置体系）：5 节点
- **G-E** 集成生态（集成）：9 节点
- **G-F** 工程保障（质量与运营）：6 节点
- **G-S** 使用场景索引（工具索引）：6 节点
