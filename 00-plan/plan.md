# 00-plan · Open Code Review 项目解析知识图谱

## 目标
对阿里开源项目 `alibaba/open-code-review`（AI 代码审查 CLI，21k+ star）做全面解析：
1. **下载**：clone 源码到留档目录（open-code-review/）
2. **源码级解析**：双路 explore 子Agent 分析核心引擎（9 包）与外围集成（CLI/配置/CI/插件/发布）
3. **知识图谱**：参考 0820-algorithm-knowledge-graph / 0823-12factor-methodology 的「五层交付骨架」
   - 叶子页全部用 what-why-how 五段式详解（用户明确要求：全面且详细）
   - 图谱兼作**工具库索引**（使用场景索引视图：场景→命令速查→关联节点）

## 图谱设计
- **51 节点 / 7 组 / 68 边**（prerequisite 42 / variant 9 / combination 7 / cooccurrence 4 / dependency 4）
- 分组：G-A 核心架构(6) / G-B 审查引擎(10) / G-C 命令行(9) / G-D 配置模型(5) / G-E 集成生态(9) / G-F 工程保障(6) / G-S 使用场景索引(6)
- 学习阶段：basic 15 / intermediate 17 / advanced 19
- 五段式内容：what / why / how / cases / anti_patterns

## 执行步骤
1. clone 源码（HTTP/1.1 降级防超时，吸取 0823-12factor项目 教训）
2. 双路 explore 并行源码分析
3. 主 Agent 设计 DAG 数据（含 Kahn 无环预检）
4. 6 路 general 并行撰写节点内容（每路 7-11 节点，基于一手源码事实）
5. 子Agent 会话内落盘片段 → 主 Agent 聚合 node-content.json + stats.md
6. 适配 12factor 生成脚本（gen_common/gen-nodes/gen-groups/gen-interactive/gen-md/gen-index + 重写 gen-views）
7. 生成全部交付物
8. 质量门控（HTML 结构/断链/DAG 无环/四向覆盖/交互 DATA/内容抽查）
9. 双版本报告 report.md + report.html

## 交付物
index.html / quality-gate.md / report.{md,html} / 00-plan/ / 01-dag-data/ / 02-node-pages/(51) / 03-groups/(7+index) / 04-interactive/ / 05-views/(4) / 06-md/(4+51) / 07-checkpoint/(9 脚本) / open-code-review/（源码）