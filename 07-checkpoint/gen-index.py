#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成根入口：index.html（统计 + 导航 + 快速开始）——OpenCodeReview 图谱版"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_common import ROOT, TITLE, SUBTITLE, load_all, esc, src_badge, BASE_CSS, SRC_STYLE

OUT = os.path.join(ROOT, 'index.html')


def main():
    dag, content, by_id, c_by_id, group_by_id = load_all()
    stats = ('<div class="stat"><b>%d</b><span>节点</span></div>'
             '<div class="stat"><b>%d</b><span>分组</span></div>'
             '<div class="stat"><b>%d</b><span>关系边</span></div>'
             '<div class="stat"><b>%d</b><span>命令工具</span></div>'
             '<div class="stat"><b>%d</b><span>使用场景</span></div>'
             % (len(dag['nodes']), len(dag['groups']), len(dag['edges']),
                sum(1 for n in dag['nodes'] if n['src'] == 'cli'),
                sum(1 for n in dag['nodes'] if n['src'] == 'scenario')))

    src_desc = []
    for src, label in SRC_STYLE.items():
        cnt = sum(1 for n in dag['nodes'] if n['src'] == src)
        if cnt:
            src_desc.append('%d 个%s' % (cnt, label['label']))

    quick = ('<ol class="steps">'
             '<li><b>按任务找工具</b>：打开使用场景索引（05-views/02-scenarios.html），审 PR / 扫代码库 / 免 Key 委托 / CI 接入 / 配置规则 / 扩展能力，每个场景含命令速查。</li>'
             '<li><b>看架构全貌</b>：打开交互 DAG 总览（04-interactive/），7 组 %d 节点依赖拓扑，点击下钻。</li>'
             '<li><b>系统学习</b>：走分层架构视图（05-views/04-architecture.html）或学习路径（05-views/03-learning-path.html）。</li>'
             '<li><b>读节点</b>：每个节点页按 what（是什么）→ why（为什么）→ how（怎么做）→ 案例 → 反模式五段式详解。</li>'
             '</ol>' % (len(dag['nodes'])))

    cards = (
        '<div class="card"><h3>使用场景索引</h3><p>工具库索引入口：按任务查命令、参数与关联组件，兼作速查手册。</p>'
        '<p><a href="05-views/02-scenarios.html">打开场景索引</a></p></div>'
        '<div class="card"><h3>交互 DAG 总览</h3><p>组级视图 + 点击下钻组内 DAG + 关系边高亮，cytoscape 渲染。</p>'
        '<p><a href="04-interactive/index.html">打开交互总览</a></p></div>'
        '<div class="card"><h3>分组目录</h3><p>%d 个组：核心架构 / 审查引擎 / 命令行 / 配置模型 / 集成生态 / 工程保障 / 场景索引。</p>'
        '<p><a href="03-groups/index.html">打开分组目录</a></p></div>'
        '<div class="card"><h3>分层架构视图</h3><p>按层浏览：架构理念 → 引擎机制 → CLI → 配置 → 集成 → 保障。</p>'
        '<p><a href="05-views/04-architecture.html">按层浏览</a></p></div>'
        '<div class="card"><h3>学习路径</h3><p>基础 → 进阶 → 高级三档推进 + 全图谱拓扑学习路径。</p>'
        '<p><a href="05-views/03-learning-path.html">查看学习路径</a></p></div>'
        '<div class="card"><h3>AI 友好镜像</h3><p>Markdown 镜像（06-md/）：节点全文、分组索引、阶段视图、学习路径，供 AI 检索。</p>'
        '<p><a href="06-md/00-index.md">打开 MD 索引</a></p></div>'
        '<div class="card"><h3>实践资产</h3><p>42 个精选实践资产（CI 示例/源码节选/提示词/规则/插件/Skill/配置示例），节点页自动关联。</p>'
        '<p><a href="assets/index.html">打开资产总览</a></p></div>'
        '<div class="card"><h3>AI 可调用索引</h3><p>ai-index.json：node_index / asset_index / command_index 三段式，AI Agent 可直接调用检索。</p>'
        '<p><a href="ai-index.json">打开 ai-index.json</a></p></div>'
        '<div class="card"><h3>12 原则对照审查</h3><p>用 12 Factor App/Agent 原则审视 OCR 设计合规度。</p>'
        '<p><a href="05-views/05-principles.html">查看对照审查</a></p></div>'
        '<div class="card"><h3>源码</h3><p>本项目源码 clone：open-code-review/（alibaba/open-code-review @ 2026-08-23）。</p>'
        '<p><a href="open-code-review/">浏览源码</a></p></div>'
        % (len(dag['groups'])))

    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
{base_css}
.stat{{display:inline-block;background:#1d2a3f;border:1px solid #2b3d5f;border-radius:8px;padding:10px 16px;margin:4px;text-align:center;}}
.stat b{{display:block;font-size:22px;color:#fff;}}
.stat span{{font-size:12px;color:var(--dim);}}
.cards{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px;margin:12px 0;}}
.card{{background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:18px;}}
.card h3{{font-size:16px;color:var(--accent);margin:0 0 8px;}}
.card p{{font-size:13px;color:var(--dim);margin-bottom:12px;}}
.card a{{color:var(--accent);}}
.steps li{{margin:6px 0;font-size:14px;color:#cfd6e4;}}
.srcrow{{display:flex;gap:6px;flex-wrap:wrap;margin:6px 0 14px;}}
.srcrow .chip{{font-size:12px;background:#1d2a3f;border:1px solid #2b3d5f;border-radius:6px;padding:3px 10px;color:#9aa3b2;}}
</style>
</head>
<body>
<header>
  <h1>{title}</h1>
  <p class="sub">{subtitle}</p>
</header>
<main>
  <h2>核心统计</h2>
  <div>{stats}</div>
  <div class="srcrow">{src_desc}</div>
  <h2>快速开始</h2>
  {quick}
  <h2>导航</h2>
  <div class="cards">{cards}</div>
</main>
<footer>{title} · 由 07-checkpoint/gen-index.py 生成 · 数据源 01-dag-data/opencodereview-dag.json + node-content.json</footer>
</body>
</html>""".format(
        title=esc(TITLE), subtitle=esc(SUBTITLE), base_css=BASE_CSS,
        stats=stats, src_desc=''.join('<span class="chip">%s</span>' % esc(x) for x in src_desc),
        quick=quick, cards=cards)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(html)
    print('index.html:', len(html), 'bytes')


if __name__ == '__main__':
    main()