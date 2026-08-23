#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""适配 12factor 生成脚本 → OpenCodeReview 图谱（批量替换 + 校验）"""
import os

BASE = os.path.dirname(os.path.abspath(__file__))
CP = BASE


def patch(path, pairs):
    p = os.path.join(CP, path)
    s = open(p, encoding='utf-8').read()
    for old, new in pairs:
        assert old in s, f'{path}: NOT FOUND >>> {old[:80]}'
        s = s.replace(old, new)
    open(p, 'w', encoding='utf-8').write(s)
    print('patched', path)


patch('gen_common.py', [
    ("TITLE = '12 Factor 方法论合并知识图谱'", "TITLE = 'Open Code Review 项目解析知识图谱'"),
    ("SUBTITLE = '12 Factor App × 12 Factor Agent — 软件工程方法论统一图谱'",
     "SUBTITLE = '阿里开源 AI 代码审查工具 — 架构理解 × 工具索引'"),
    ("DAG_PATH = os.path.join(DATA_DIR, 'methodology-dag.json')",
     "DAG_PATH = os.path.join(DATA_DIR, 'opencodereview-dag.json')"),
    ("""SRC_STYLE = {
    'app':    {'fg': '#9cc2ff', 'bg': '#16273f', 'brd': '#4f8cff', 'label': 'App 体系'},
    'agent':  {'fg': '#ff8a97', 'bg': '#3a1520', 'brd': '#e05563', 'label': 'Agent 体系'},
    'bridge': {'fg': '#6fd3ae', 'bg': '#0f2b1f', 'brd': '#2fb98a', 'label': '桥接主题'},
    'tool':   {'fg': '#e8c66a', 'bg': '#3a2f12', 'brd': '#e0c35e', 'label': '工具'},
}""",
     """SRC_STYLE = {
    'core':        {'fg': '#9cc2ff', 'bg': '#16273f', 'brd': '#4f8cff', 'label': '核心架构'},
    'engine':      {'fg': '#7fe0d8', 'bg': '#12302c', 'brd': '#5ad0d0', 'label': '审查引擎'},
    'cli':         {'fg': '#e8c66a', 'bg': '#3a2f12', 'brd': '#e0c35e', 'label': '命令行'},
    'config':      {'fg': '#c9a8ef', 'bg': '#2b2040', 'brd': '#b48ae0', 'label': '配置模型'},
    'integration': {'fg': '#ff8a97', 'bg': '#3a1520', 'brd': '#e05563', 'label': '集成生态'},
    'quality':     {'fg': '#2fb98a', 'bg': '#122b22', 'brd': '#2fb98a', 'label': '工程保障'},
    'scenario':    {'fg': '#ffb86b', 'bg': '#3a2f12', 'brd': '#e8933b', 'label': '使用场景'},
}"""),
    ("""KIND_STYLE = {
    'source':    {'fg': '#9cc2ff', 'bg': '#16273f', 'brd': '#4f8cff', 'label': '来源组'},
    'bridge':    {'fg': '#6fd3ae', 'bg': '#0f2b1f', 'brd': '#2fb98a', 'label': '主题组'},
    'crosscut':  {'fg': '#c9a8ef', 'bg': '#2b2040', 'brd': '#b48ae0', 'label': '横切组'},
    'tool':      {'fg': '#e8c66a', 'bg': '#3a2f12', 'brd': '#e0c35e', 'label': '工具组'},
}""",
     """KIND_STYLE = {
    'source':    {'fg': '#9cc2ff', 'bg': '#16273f', 'brd': '#4f8cff', 'label': '架构/机制'},
    'tool':      {'fg': '#e8c66a', 'bg': '#3a2f12', 'brd': '#e0c35e', 'label': '工具'},
    'crosscut':  {'fg': '#2fb98a', 'bg': '#122b22', 'brd': '#2fb98a', 'label': '保障'},
    'scenario':  {'fg': '#ff8a97', 'bg': '#3a1520', 'brd': '#e05563', 'label': '场景索引'},
}"""),
    ("KIND_ORDER = ['source', 'bridge', 'crosscut', 'tool']",
     "KIND_ORDER = ['source', 'tool', 'crosscut', 'scenario']"),
    ("""def type_badge(node):
    if node['type'] == 'bridge':
        return '<span class="badge tp" style="color:#6fd3ae;background:#0f2b1f;border-color:#2fb98a">桥接主题</span>'
    if node['type'] == 'tool':
        return '<span class="badge tp" style="color:#e8c66a;background:#3a2f12;border-color:#e0c35e">工具</span>'
    return '<span class="badge tp" style="color:#9cc2ff;background:#16273f;border-color:#4f8cff">方法原则</span>'""",
     """def type_badge(node):
    if node['type'] == 'tool':
        return '<span class="badge tp" style="color:#e8c66a;background:#3a2f12;border-color:#e0c35e">工具</span>'
    if node['type'] == 'scenario':
        return '<span class="badge tp" style="color:#ff8a97;background:#3a1520;border-color:#e05563">场景索引</span>'
    if node['type'] == 'crosscut':
        return '<span class="badge tp" style="color:#2fb98a;background:#122b22;border-color:#2fb98a">工程保障</span>'
    return '<span class="badge tp" style="color:#9cc2ff;background:#16273f;border-color:#4f8cff">方法机制</span>'"""),
])

patch('gen-nodes.py', [
    ("数据源 01-dag-data/methodology-dag.json + node-content.json",
     "数据源 01-dag-data/opencodereview-dag.json + node-content.json"),
])

patch('gen-groups.py', [
    ("数据源 01-dag-data/methodology-dag.json",
     "数据源 01-dag-data/opencodereview-dag.json"),
])

patch('gen-interactive.py', [
    ("<title>12 Factor 方法论图谱 · 交互式 DAG 总览</title>",
     "<title>Open Code Review 图谱 · 交互式 DAG 总览</title>"),
    ('<h1>12 Factor 方法论图谱 <span class="badge">交互 DAG</span></h1>',
     '<h1>Open Code Review 图谱 <span class="badge">交互 DAG</span></h1>'),
    ("""GROUP_COLOR_MAP = {
    'GA': '#4f8cff', 'GB': '#e05563',
    'GT01': '#2fb98a', 'GT02': '#2fb98a', 'GT03': '#2fb98a', 'GT04': '#2fb98a', 'GT05': '#2fb98a',
    'GT06': '#2fb98a', 'GT07': '#2fb98a', 'GT08': '#2fb98a', 'GT09': '#2fb98a', 'GT10': '#2fb98a',
    'GX1': '#b48ae0', 'GX2': '#b48ae0', 'GX3': '#b48ae0',
}""",
     """GROUP_COLOR_MAP = {
    'G-A': '#4f8cff', 'G-B': '#7fe0d8', 'G-C': '#e8c66a',
    'G-D': '#c9a8ef', 'G-E': '#e05563', 'G-F': '#2fb98a', 'G-S': '#ffb86b',
}"""),
    ("""SRC_VENDOR = os.path.join(ROOT, '..', '0820-algorithm-knowledge-graph', '04-interactive', 'vendor')
SRC_VENDOR_ABS = os.path.normpath(os.path.join(ROOT, os.pardir, '0820-algorithm-knowledge-graph', '04-interactive', 'vendor'))""",
     """SRC_VENDOR = os.path.join(INTER_DIR, 'vendor')
SRC_VENDOR_ABS = os.path.join(INTER_DIR, 'vendor')"""),
])

patch('gen-md.py', [
    ("dag = json.load(open('01-dag-data/methodology-dag.json', encoding='utf-8'))",
     "dag = json.load(open('01-dag-data/opencodereview-dag.json', encoding='utf-8'))"),
    ("TYPE_LABEL = {'principle': '方法原则', 'bridge': '桥接主题', 'tool': '工具'}",
     "TYPE_LABEL = {'principle': '方法机制', 'tool': '工具', 'crosscut': '工程保障', 'scenario': '场景索引'}"),
    ("SRC_LABEL = {'app': 'App 体系', 'agent': 'Agent 体系', 'bridge': '桥接', 'tool': '工具'}",
     "SRC_LABEL = {'core': '核心架构', 'engine': '审查引擎', 'cli': '命令行', 'config': '配置模型', 'integration': '集成生态', 'quality': '工程保障', 'scenario': '使用场景'}"),
    ("lines = ['# 12 Factor 方法论合并知识图谱 · AI 友好索引', '']",
     "lines = ['# Open Code Review 项目解析知识图谱 · AI 友好索引', '']"),
    ("kind_label = {'source': '来源组', 'bridge': '主题组', 'crosscut': '横切组', 'tool': '工具组'}.get(g['kind'], g['kind'])",
     "kind_label = {'source': '架构/机制组', 'tool': '工具组', 'crosscut': '保障组', 'scenario': '场景索引组'}.get(g['kind'], g['kind'])"),
    ("""app_nodes = [n for n in dag['nodes'] if n['src'] == 'app']
ag_nodes = [n for n in dag['nodes'] if n['src'] == 'agent']
order_app = topo(app_nodes, edges)
order_ag = topo(ag_nodes, edges)
# 打通路径：App → bridge 主题 → Agent（全 prerequisite 拓扑）
order_all = topo(dag['nodes'], edges)

lines = ['# 学习路径（自动生成，基于 prerequisite 拓扑序）', '']
lines.append('## 路径 A：传统工程入门（App 体系）')
lines.append('')
for i, nid in enumerate(order_app, 1):
    n = nodes[nid]
    lines.append(f"{i}. [{nid}] {n['name']}")
lines.append('')
lines.append('## 路径 B：LLM Agent 工程入门（Agent 体系）')
lines.append('')
for i, nid in enumerate(order_ag, 1):
    n = nodes[nid]
    lines.append(f"{i}. [{nid}] {n['name']}")
lines.append('')
lines.append('## 路径 C：两者打通（全图谱拓扑序）')""",
     """cli_nodes = [n for n in dag['nodes'] if n['src'] == 'cli']
order_cli = topo(cli_nodes, edges)
order_all = topo(dag['nodes'], edges)

lines = ['# 学习路径（自动生成，基于 prerequisite 拓扑序）', '']
lines.append('## 路径 A：命令行上手（CLI 工具）')
lines.append('')
for i, nid in enumerate(order_cli, 1):
    n = nodes[nid]
    lines.append(f"{i}. [{nid}] {n['name']}")
lines.append('')
lines.append('## 路径 B：从入门到精通（全图谱拓扑序）')"""),
])

print('ALL PATCHED OK')