# Open Code Review 项目解析知识图谱

> 对阿里开源 AI 代码审查工具 **alibaba/open-code-review**（21k+ star）的全面解析：**知识 + 实践源码资产 + AI 可调用索引**三合一知识体系。以 DAG 组织 51 个知识点（架构 / 引擎 / CLI / 配置 / 集成 / 保障 / 使用场景），叶子页全部五段式详解（what / why / how / 案例 / 反模式）+ 正反实例论证 + 实践资产关联，并内置「12 Factor 原则对照审查」方法论定位。

[![GitHub Pages](https://img.shields.io/badge/在线预览-GitHub%20Pages-blue)](https://zako-mio.github.io/open-code-review-kg/)
[![License](https://img.shields.io/badge/License-Apache--2.0-blue)]()
[![Nodes](https://img.shields.io/badge/Nodes-51-orange)]()
[![Edges](https://img.shields.io/badge/Edges-68-yellow)]()
[![Assets](https://img.shields.io/badge/Assets-42-green)]()

## 三合一体系

| 层 | 内容 | 入口 |
|---|---|---|
| **知识** | 51 节点 / 7 组 / 68 边 DAG；叶子页五段式详解（平均 900 字）+ 正反实例论证（260 条，pro/con 各半，含代码块） | `02-node-pages/` |
| **实践源码资产** | 42 个精选资产：CI 示例 7 / 源码节选 16 / 插件 5 / 构建 5 / Skill 2 / 配置示例 2 / 工具 schema / 提示词 / 规则 / 脚本 / 文档；节点页「实践资产」区块 51/51 关联 | `assets/` |
| **AI 可调用索引** | `ai-index.json` 三段式：node_index（51）→ commands（72 条真实命令）→ asset_ids；AI Agent 可直接检索定位 | `ai-index.json` |

另附 **12 Factor 原则对照审查**（05-views/05-principles.html）：24 条原则（App 12 + Agent 12）逐条对照 OCR 机制，结论合规 22 / 部分合规 2。

## 图谱核心

| 构成 | 数量 | 说明 |
|---|---|---|
| 节点 | 51 | principle 20 / tool 18 / crosscut 6 / scenario 6 |
| 分组 | 7 | 核心架构 / 审查引擎 / 命令行 / 配置模型 / 集成生态 / 工程保障 / 使用场景索引 |
| 关系边 | 68 | prerequisite 42 / variant 9 / combination 7 / cooccurrence 4 / dependency 4 |
| 学习阶段 | 3 | basic 15 / intermediate 17 / advanced 19 |
| 正反实例 | 260 条 | 130 对 pro+con，命令类用真实 ocr 参数，机制类用伪代码/diff |

DAG 由 prerequisite 边构成无环主干（Kahn 校验通过），学习路径由拓扑序自动生成。

## 快速开始

1. 打开根入口 `index.html`（或在线预览），查看核心统计与导航。
2. **按任务找工具**：使用场景索引（`05-views/02-scenarios.html`）——审 PR / 扫代码库 / 免 Key 委托 / CI 接入 / 配置规则 / 扩展能力，每个场景含命令速查。
3. **看架构全貌**：交互 DAG 总览（`04-interactive/`）组级视图 + 点击下钻。
4. **读节点**：每个节点页按 what → why → how → 案例 → 反模式 → 正反实例论证 → 实践资产 七段式阅读。
5. **方法论定位**：12 原则对照审查（`05-views/05-principles.html`）。
6. **AI 调用**：直接读取 `ai-index.json` 定位知识 + 命令 + 资产。

## 目录结构

```
open-code-review-kg/
├── index.html                  # 根入口（统计 + 导航 + 快速开始）
├── ai-index.json               # AI 可调用索引（node_index / asset_index / command_index）
├── assets-manifest.json        # 资产清单（42 资产 × 节点关联）
├── assets/                     # 42 个实践源码资产（CI/源码节选/插件/Skill/配置示例/提示词/规则…）
│   └── index.html              # 资产总览页
├── quality-gate.md             # 质量门控报告（v3，10 项全 PASS）
├── report.md / report.html     # 项目报告（AI 友好 + 人类可读）
├── 00-plan/                    # 计划文档
├── 01-dag-data/                # DAG 数据 + 五段式内容 + 正反实例 + 12 原则映射
├── 02-node-pages/              # 51 个节点详情页（HTML，七段式）
├── 03-groups/                  # 7 组页 + 组总索引
├── 04-interactive/             # 交互 DAG 总览（cytoscape + dagre，本地渲染）
│   └── vendor/                 # 本地依赖（cytoscape.min.js + dagre）
├── 05-views/                   # 视图：场景索引 / 学习路径 / 架构分层 / 12 原则对照
├── 06-md/                      # AI 友好 Markdown 镜像（索引 + 节点 + 资产 + 原则）
├── 07-checkpoint/              # 生成脚本 gen-*.py（可重复构建全部交付物）
└── research/                   # （本任务为源码级分析，见 report.md）
```

## 可再构建性

所有交付物均由 `07-checkpoint/gen-*.py` 从 `01-dag-data/` 数据 + `assets-manifest.json` 生成：

```bash
cd 07-checkpoint
python3 gen-nodes.py        # 51 节点页（五段式 + 证据 + 资产区块）
python3 gen-groups.py       # 7 组页
python3 gen-views.py        # 场景索引 / 学习路径 / 架构分层 / 12 原则对照
python3 gen-interactive.py  # 交互图（cytoscape DATA 注入）
python3 gen-md.py           # AI 友好 MD 镜像
python3 gen-assets.py       # assets/index.html + ai-index.json + 06-md/04-assets.md
python3 gen-index.py        # 根入口
```

修改 `01-dag-data/` 后重跑即可全量更新。

## 数据来源

- **项目源码**：`github.com/alibaba/open-code-review`（Apache-2.0，@ 2026-08-23 快照，完整源码 clone 保留在本地留档目录）
- **图谱内容**：基于源码一手分析（核心引擎 9 包 + 外围集成 12 模块）+ 官方 README / 论文（arXiv 2608.09290）/ AACR-Bench 基准
- **方法论标尺**：12 Factor App / 12 Factor Agent 合并图谱（`0823-12factor-methodology`）

## 许可

- 图谱内容与生成代码：MIT
- 实践资产（assets/）：遵循原项目 **Apache-2.0** 许可（alibaba/open-code-review）