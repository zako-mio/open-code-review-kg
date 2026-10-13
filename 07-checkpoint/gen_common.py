#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""12 Factor 方法论图谱生成 —— 公共工具模块（数据加载 / 拓扑 / 样式 / HTML 片段）

被 gen-nodes.py / gen-groups.py / gen-views.py / gen-interactive.py 共享。
数据源：01-dag-data/methodology-dag.json + 01-dag-data/node-content.json，不硬编码节点数据。
"""
import html as html_mod
import json
import os
from collections import defaultdict, deque

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, '01-dag-data')
DAG_PATH = os.path.join(DATA_DIR, 'opencodereview-dag.json')
CONTENT_PATH = os.path.join(DATA_DIR, 'node-content.json')

TITLE = 'Open Code Review 项目解析知识图谱'
SUBTITLE = '阿里开源 AI 代码审查工具 — 架构理解 × 工具索引'


def load_dag():
    with open(DAG_PATH, encoding='utf-8') as f:
        return json.load(f)


def load_content():
    with open(CONTENT_PATH, encoding='utf-8') as f:
        return json.load(f)


def load_all():
    dag = load_dag()
    content = load_content()
    by_id = {n['id']: n for n in dag['nodes']}
    c_by_id = {n['id']: n for n in content['nodes']}
    group_by_id = {g['id']: g for g in dag['groups']}
    return dag, content, by_id, c_by_id, group_by_id


def esc(s):
    return html_mod.escape(str(s), quote=True)


def build_indexes(dag):
    group_by_id = {g['id']: g for g in dag['groups']}
    node_by_id = {n['id']: n for n in dag['nodes']}
    node_to_group = {}
    for g in dag['groups']:
        for nid in g['node_ids']:
            node_to_group[nid] = g['id']
    group_node_index = {}
    for g in dag['groups']:
        for i, nid in enumerate(g['node_ids']):
            group_node_index[nid] = i
    return group_by_id, node_by_id, node_to_group, group_node_index


def topo_sort(node_ids, edges):
    """对给定节点集合，用 prerequisite 边做 Kahn 拓扑排序（返回稳定顺序，DAG 保证无环）。"""
    idset = set(node_ids)
    adj = defaultdict(list)
    indeg = {n: 0 for n in node_ids}
    for e in edges:
        f, t = e['from'], e['to']
        if e['type'] == 'prerequisite' and f in idset and t in idset:
            adj[f].append(t)
            indeg[t] += 1
    q = deque(sorted(n for n in node_ids if indeg[n] == 0))
    order = []
    while q:
        u = q.popleft()
        order.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    for n in node_ids:
        if n not in order:
            order.append(n)
    return order


# ---------------------------------------------------------------- 样式常量
STAGE_STYLE = {
    'basic':        {'fg': '#2fb98a',  'bg': '#122b22', 'brd': '#2fb98a',  'label': '基础'},
    'intermediate': {'fg': '#e0a75e',  'bg': '#332412', 'brd': '#e8933b',  'label': '进阶'},
    'advanced':     {'fg': '#c9a8ef',  'bg': '#2b2040', 'brd': '#b48ae0',  'label': '高级'},
}

SRC_STYLE = {
    'core':        {'fg': '#9cc2ff', 'bg': '#16273f', 'brd': '#4f8cff', 'label': '核心架构'},
    'engine':      {'fg': '#7fe0d8', 'bg': '#12302c', 'brd': '#5ad0d0', 'label': '审查引擎'},
    'cli':         {'fg': '#e8c66a', 'bg': '#3a2f12', 'brd': '#e0c35e', 'label': '命令行'},
    'config':      {'fg': '#c9a8ef', 'bg': '#2b2040', 'brd': '#b48ae0', 'label': '配置模型'},
    'integration': {'fg': '#ff8a97', 'bg': '#3a1520', 'brd': '#e05563', 'label': '集成生态'},
    'quality':     {'fg': '#2fb98a', 'bg': '#122b22', 'brd': '#2fb98a', 'label': '工程保障'},
    'scenario':    {'fg': '#ffb86b', 'bg': '#3a2f12', 'brd': '#e8933b', 'label': '使用场景'},
}

KIND_STYLE = {
    'source':    {'fg': '#9cc2ff', 'bg': '#16273f', 'brd': '#4f8cff', 'label': '架构/机制'},
    'tool':      {'fg': '#e8c66a', 'bg': '#3a2f12', 'brd': '#e0c35e', 'label': '工具'},
    'crosscut':  {'fg': '#2fb98a', 'bg': '#122b22', 'brd': '#2fb98a', 'label': '保障'},
    'scenario':  {'fg': '#ff8a97', 'bg': '#3a1520', 'brd': '#e05563', 'label': '场景索引'},
}

EDGE_STYLE = {
    'prerequisite': {'fg': '#8fb5ff', 'bg': '#16273f', 'brd': '#4f8cff', 'label': '前置依赖'},
    'variant':      {'fg': '#e8c66a', 'bg': '#3a2f12', 'brd': '#e0c35e', 'label': '变体'},
    'combination':  {'fg': '#c9a8ef', 'bg': '#2b2040', 'brd': '#b48ae0', 'label': '组合'},
    'cooccurrence': {'fg': '#7fe0d8', 'bg': '#12302c', 'brd': '#5ad0d0', 'label': '共现'},
    'dependency':   {'fg': '#e8a25e', 'bg': '#332412', 'brd': '#e8933b', 'label': '依赖关联'},
}

GROUP_COLOR = {}
KIND_ORDER = ['source', 'tool', 'crosscut', 'scenario']


def stage_badge(stage):
    st = STAGE_STYLE.get(stage, STAGE_STYLE['basic'])
    return ('<span class="badge st" style="color:%s;background:%s;border-color:%s">%s</span>'
            % (st['fg'], st['bg'], st['brd'], st['label']))


def src_badge(src):
    s = SRC_STYLE.get(src, SRC_STYLE['core'])
    return ('<span class="badge src" style="color:%s;background:%s;border-color:%s">%s</span>'
            % (s['fg'], s['bg'], s['brd'], s['label']))


def kind_badge(kind):
    k = KIND_STYLE.get(kind, KIND_STYLE['source'])
    return ('<span class="badge kind" style="color:%s;background:%s;border-color:%s">%s</span>'
            % (k['fg'], k['bg'], k['brd'], k['label']))


def group_badge(gid, gname):
    return ('<span class="badge grp">%s · %s</span>' % (esc(gid), esc(gname)))


def type_badge(node):
    if node['type'] == 'tool':
        return '<span class="badge tp" style="color:#e8c66a;background:#3a2f12;border-color:#e0c35e">工具</span>'
    if node['type'] == 'scenario':
        return '<span class="badge tp" style="color:#ff8a97;background:#3a1520;border-color:#e05563">场景索引</span>'
    if node['type'] == 'crosscut':
        return '<span class="badge tp" style="color:#2fb98a;background:#122b22;border-color:#2fb98a">工程保障</span>'
    return '<span class="badge tp" style="color:#9cc2ff;background:#16273f;border-color:#4f8cff">方法机制</span>'


def edge_chip(e, node_id, node_by_id, other_dir_ok=True):
    st = EDGE_STYLE.get(e['type'], EDGE_STYLE['dependency'])
    other = e['to'] if e['from'] == node_id else e['from']
    arrow = '&#8594;' if e['from'] == node_id else '&#8592;'
    oname = node_by_id.get(other, {}).get('name', other)
    return ('<a class="chip e-%s" href="%s.html">%s%s%s<span class="etype">%s</span></a>'
            % (e['type'], esc(other), esc(oname), arrow, esc(e['label']), st['label']))


# ---------------------------------------------------------------- 共享 CSS
# ★ 批 H（标准档）说明：本常量首行即令牌块（形如「冒号 root 加大括号」），是 default / 05-views /
#   assets 三族的**唯一字面落点**；令牌块由 pipeline 派生器从站点值件写入（⛔ 不手改）。
#   `gen-index.py` 按「首个非空行即该令牌块」这一约定取用（由站点侧 gate_tokens.py 的 G8 看住）。
#   ★ 注意：本注释**不得**写出令牌块的字面形状 —— 派生器的块定位正则会把注释里的字样当成
#     第二个块，从而拒写（B1「恰有 1 个 :root 块」）。本步实测踩到过这一条。
#   ★ Q8-A 留痕：`.navseq .spacer` 是实测**唯一**零引用选择器（审计点名的 5 组多数在用），
#     按裁定**登记保留**、⛔ 不删除——删除会让「审计整改行号不可照抄」这一教训失去实证样本。
BASE_CSS = """
:root{--text:#e6e8ee;--dim:#9aa3b2;--text-3:#7d8798;--link:#6ea8ff;--accent:#4f8cff;--border:#6b7280;--border-subtle:#2a2f3a;--bg:#0f1117;--panel:#161a22;--surface-2:#1d2330;--stripe:#141821;--ok:#2fb98a;--warn:#e8933b;--err:#ff6b6b;--ext:#c9a227;--upgrade:#b48a3c;--disabled:#6b7280;--focus-ring:#4f8cff;}
*{box-sizing:border-box;margin:0;padding:0;}
body{background:var(--bg);color:var(--text);font-family:'Segoe UI',system-ui,'PingFang SC','Microsoft YaHei',sans-serif;line-height:1.7;}
header{background:var(--panel);border-bottom:1px solid var(--border);padding:14px 24px;}
header .crumb{color:var(--dim);font-size:13px;margin-bottom:6px;}
header .crumb a{color:var(--accent);text-decoration:none;}
header .crumb a:hover{text-decoration:underline;}
header h1{font-size:20px;font-weight:650;color:#f0f3f9;display:inline-block;margin-right:12px;}
.badges{display:inline-flex;gap:6px;flex-wrap:wrap;vertical-align:middle;}
.badge{display:inline-block;padding:2px 10px;border-radius:20px;font-size:12px;font-weight:600;border:1px solid transparent;letter-spacing:.3px;}
.badge.grp{background:#1d2a3f;color:#7fb0ff;border-color:#2b3d5f;}
.badge.cnt{background:#23272f;color:#9aa0ab;border-color:#3a3f4a;}
main{padding:24px;max-width:1150px;margin:0 auto;}
h2{font-size:18px;margin:34px 0 12px;color:#cfd6e4;border-bottom:1px solid var(--border);padding-bottom:8px;}
h2 .dim{font-size:13px;font-weight:400;}
h3{font-size:15px;margin:20px 0 8px;color:#b8c2d4;}
p,li{font-size:14px;}
ul{padding-left:22px;}
a{color:var(--accent);text-decoration:none;}
a:hover{text-decoration:underline;}
.dim{color:var(--dim);}
.section{scroll-margin-top:8px;}
.brieflead{background:#0d1a14;border:1px solid #2f5a4a;border-left:4px solid var(--ok);border-radius:8px;padding:12px 16px;font-size:15px;color:#cfe8dd;margin:12px 0;}
.whybox{background:var(--panel);border:1px solid var(--border);border-left-width:4px;border-radius:8px;padding:14px 18px;margin:10px 0;}
.bullet{background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:10px 16px;margin:6px 0;font-size:14px;color:#d3d9e4;}
.pit li{margin:5px 0;font-size:14px;}
.pit li::marker{color:var(--warn);}
.tblwrap{overflow-x:auto;margin:8px 0;}
table{border-collapse:collapse;width:100%;}
th,td{border:1px solid var(--border);padding:7px 11px;font-size:13px;text-align:left;vertical-align:top;}
th{background:var(--panel);color:#b8c2d4;white-space:nowrap;}
td.nid{white-space:nowrap;font-family:Consolas,monospace;font-size:12px;}
td.nid a{color:#8fb5ff;}
td .nname{font-weight:600;color:var(--text);}
td.brief{font-size:12.5px;color:#b6c0d0;}
.navseq{display:flex;gap:10px;margin:16px 0;flex-wrap:wrap;}
.navseq a{display:inline-block;background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:10px 18px;font-size:14px;color:#b8c2d4;text-align:center;min-width:150px;}
.navseq a .dir{display:block;font-size:11px;color:var(--dim);margin-bottom:2px;}
.navseq a .v{font-weight:600;color:var(--accent);}
.navseq a.nav-index .v{color:var(--ok);}
.navseq .spacer{flex:1;min-width:60px;}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin:6px 0;}
.chip{font-size:12px;background:#1d2a3f;border:1px solid #2b3d5f;border-radius:6px;padding:2px 8px;color:#7fb0ff;text-decoration:none;}
.chip:hover{background:#2b3d5f;}
.chip .etype{font-size:10px;opacity:.85;margin-left:4px;}
.chip.e-prerequisite{background:#16273f;border-color:#2b3d5f;color:#9cc2ff;}
.chip.e-variant{background:#3a2f12;border-color:#4a3f20;color:#e8c66a;}
.chip.e-combination{background:#2b2040;border-color:#4a3560;color:#c9a8ef;}
.chip.e-cooccurrence{background:#12302c;border-color:#2b4a44;color:#7fe0d8;}
.chip.e-dependency{background:#332412;border-color:#4a3a20;color:#e8a25e;}
.pathbox{background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:12px 16px;margin:10px 0;}
.path-label{font-size:12px;color:var(--dim);margin-bottom:8px;}
.path-seq{display:flex;flex-wrap:wrap;gap:4px 0;font-size:13px;}
.path-seq a{display:inline-block;background:#16273f;border:1px solid #2b3d5f;border-radius:6px;padding:2px 8px;color:#7fb0ff;text-decoration:none;margin:2px;}
.path-seq a:hover{background:#2b3d5f;}
.dep-list{list-style:none;padding-left:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:8px;margin-top:8px;}
.dep-list li{background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:8px 12px;font-size:13px;border-left:3px solid var(--warn);}
.dep-list .evi{display:block;font-size:11px;color:var(--dim);margin-top:2px;}
.treenav{background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:10px 16px;margin:6px 0 18px;display:flex;flex-wrap:wrap;gap:2px 10px;}
.treenav .label{font-size:12px;color:var(--dim);align-self:center;flex-shrink:0;}
.treenav a{color:var(--dim);font-size:12px;text-decoration:none;border-radius:5px;padding:1px 6px;}
.treenav a:hover{color:var(--accent);background:#1d2a3f;}
footer{margin-top:44px;padding:16px 24px;border-top:1px solid var(--border);color:var(--dim);font-size:12px;text-align:center;}
@media (max-width:720px){
  main{padding:14px;}
  header{padding:12px 14px;}
  header h1{font-size:17px;}
  .navseq a{min-width:100%;}
  .badges{display:flex;margin-top:6px;}
}
@media print{
  body{background:#fff;color:#000;}
  header,footer,.navseq,.treenav{display:none;}
  th,td{border-color:#999;color:#000;}
}
"""
