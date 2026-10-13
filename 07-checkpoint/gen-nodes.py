#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 34 个节点页：02-node-pages/{node_id}.html（五段式 / 桥接三栏对比）

principle 节点：what/why/how/cases/anti_patterns 五段
bridge 节点：what/why/how + App 侧 | Agent 侧 | 差异根源 三栏对比表
页头：来源体系徽章(App/Agent/桥接) + 阶段徽章 + 所属组徽章
面包屑：总览 > 组 > 节点；含相关边列表（按边类型分组）。
"""
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_common import (
    inject_shell,ROOT, TITLE, SUBTITLE, load_all, esc, build_indexes,
                        src_badge, stage_badge, group_badge, type_badge,
                        edge_chip, BASE_CSS, EDGE_STYLE)

EVIDENCE_PATH = os.path.join(ROOT, '01-dag-data', 'evidence.json')
ASSET_MANIFEST = os.path.join(ROOT, 'assets-manifest.json')
ASSET_TYPE_LABEL = {
    'ci': 'CI 集成', 'script': '脚本', 'tool': '工具 schema', 'prompt': '提示词',
    'rule': '规则', 'code': '源码节选', 'skill': 'Skill', 'plugin': '插件',
    'build': '构建发布', 'config': '配置示例', 'doc': '文档',
}

OUT_DIR = os.path.join(ROOT, '02-node-pages')


def build_edges_for_node(edges, nid):
    out = []
    for e in edges:
        if e['from'] == nid or e['to'] == nid:
            out.append(e)
    out.sort(key=lambda e: (e['type'], e['from']))
    return out


def node_html(nid, node, content, group, edges, node_by_id, evidence_map=None, asset_map=None):
    gid = group['id']
    gname = group['name']
    sections = []

    # ---------- What ----------
    what_items = content.get('what') or []
    what_lead = node['definition']
    w = ['<div class="section"><h2>What · 是什么</h2>']
    w.append('<div class="brieflead">%s</div>' % esc(what_lead))
    for item in what_items:
        w.append('<div class="bullet">%s</div>' % esc(item))
    w.append('</div>')
    sections.append(''.join(w))

    # ---------- Why ----------
    why_items = content.get('why') or []
    w = ['<div class="section"><h2>Why · 为什么</h2>']
    w.append('<div class="whybox" style="border-color:%s"><div class="tag" style="color:%s">原理 · Principle</div>'
             % (EDGE_STYLE['prerequisite']['brd'], EDGE_STYLE['prerequisite']['fg']))
    if why_items:
        for item in why_items:
            w.append('<p>%s</p>' % esc(item))
    else:
        w.append('<p class="dim">（本节点未展开原理说明）</p>')
    w.append('</div></div>')
    sections.append(''.join(w))

    # ---------- How ----------
    how_items = content.get('how') or []
    w = ['<div class="section"><h2>How · 怎么做</h2>']
    if how_items:
        for item in how_items:
            w.append('<div class="bullet">%s</div>' % esc(item))
    else:
        w.append('<div class="bullet" class="dim">（本节点未展开落地做法）</div>')
    w.append('</div>')
    sections.append(''.join(w))

    # ---------- bridge：三栏对比表 ----------
    if node['type'] == 'bridge':
        app_side = content.get('app_side') or []
        agent_side = content.get('agent_side') or []
        difference = content.get('difference') or []
        w = ['<div class="section"><h2>两体系对照 · App 侧 | Agent 侧 | 差异根源</h2>']
        w.append('<div class="tblwrap"><table class="cmp"><thead><tr>'
                 '<th style="width:33%%">App 侧</th>'
                 '<th style="width:33%%">Agent 侧</th>'
                 '<th style="width:34%%">差异根源</th></tr></thead><tbody>')
        rows = max(len(app_side), len(agent_side), len(difference))
        for i in range(rows):
            a = app_side[i] if i < len(app_side) else ''
            b = agent_side[i] if i < len(agent_side) else ''
            c = difference[i] if i < len(difference) else ''
            w.append('<tr><td>%s</td><td>%s</td><td class="diffsrc">%s</td></tr>'
                     % (esc(a), esc(b), esc(c)))
        w.append('</tbody></table></div></div>')
        sections.append(''.join(w))

    # ---------- cases / anti_patterns ----------
    cases = content.get('cases') or []
    anti = content.get('anti_patterns') or []
    if cases:
        w = ['<div class="section"><h2>案例 · Cases</h2><div class="tblwrap"><table>'
             '<tr><th>代表性案例</th></tr>']
        for c in cases:
            w.append('<tr><td>%s</td></tr>' % esc(c))
        w.append('</table></div></div>')
        sections.append(''.join(w))
    if anti:
        w = ['<div class="section"><h2>反模式 · Anti-patterns</h2><ul class="pit">']
        for a in anti:
            w.append('<li>%s</li>' % esc(a))
        w.append('</ul></div>')
        sections.append(''.join(w))

    # ---------- 正反实例论证 ----------
    ev_list = (evidence_map or {}).get(nid, [])
    if ev_list:
        w = ['<div class="section"><h2>正反实例论证 · Evidence</h2>']
        w.append('<div class="evgrid">')
        for ev in ev_list:
            is_pro = ev.get('type') == 'pro'
            cls = 'ev-pro' if is_pro else 'ev-con'
            tag = '正例 · Pro' if is_pro else '反例 · Con'
            code_html = ''
            for line in (ev.get('code') or []):
                code_html += '<code>%s</code>' % esc(line)
            w.append('<div class="evcard %s">' % cls)
            w.append('<div class="evtag">%s</div>' % tag)
            w.append('<div class="evtitle">%s</div>' % esc(ev.get('title', '')))
            if code_html:
                w.append('<div class="evcode">%s</div>' % code_html)
            w.append('<div class="evdesc">%s</div>' % esc(ev.get('desc', '')))
            w.append('</div>')
        w.append('</div></div>')
        sections.append(''.join(w))

    # ---------- 实践资产 ----------
    assets = (asset_map or {}).get(nid, [])
    if assets:
        w = ['<div class="section"><h2>实践资产 · Assets</h2>']
        w.append('<div class="assetgrid">')
        for a in assets:
            atype = ASSET_TYPE_LABEL.get(a['type'], a['type'])
            w.append('<div class="assetcard"><div class="asstype">%s</div>'
                     '<div class="assname"><a href="../%s" target="_blank">%s</a></div>'
                     '<div class="assdesc">%s</div>'
                     '<div class="assmeta">%s · %d B</div></div>'
                     % (esc(atype), esc(a['path']), esc(a['name']),
                        esc(a['desc']), esc(a['src_path']), a.get('size_bytes', 0)))
        w.append('</div></div>')
        sections.append(''.join(w))

    # ---------- 相关边 ----------
    my_edges = build_edges_for_node(edges, nid)
    groups_edges = {}
    for e in my_edges:
        groups_edges.setdefault(e['type'], []).append(e)
    w = ['<div class="section"><h2>相关边</h2>']
    if my_edges:
        w.append('<div class="chips">')
        for et in sorted(groups_edges.keys(), key=lambda x: EDGE_STYLE.get(x, {}).get('label', x)):
            for e in groups_edges[et]:
                w.append(edge_chip(e, nid, node_by_id))
        w.append('</div>')
    else:
        w.append('<p class="dim">本节点没有与其他节点的关系边。</p>')
    w.append('</div>')
    sections.append(''.join(w))

    body = '\n\n'.join(sections)

    crumb = ('<div class="crumb"><a href="../index.html">%s</a> / <a href="../03-groups/index.html">分组目录</a> / '
             '<a href="../03-groups/%s.html">%s</a> / <span>%s</span></div>'
             % (esc(TITLE), esc(gid), esc(gname), esc(node['name'])))

    badges = (src_badge(node['src']) + stage_badge(node['stage'])
              + type_badge(node) + group_badge(gid, gname))

    # 组内导航
    nav = ('<div class="navseq">'
           '<a class="nav-index" href="../04-interactive/index.html#%s"><span class="dir">全局</span><span class="v">交互总览</span></a>'
           '<a class="nav-index" href="../03-groups/%s.html"><span class="dir">返回组</span><span class="v">%s</span></a>'
           '<a class="nav-index" href="../04-interactive/index.html"><span class="dir">交互图</span><span class="v">打开总览</span></a>'
           '</div>'
           % (esc(gid), esc(gid), esc(gname)))

    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name} · {title}</title>
<style>
{extra_css}
table.cmp th{{text-align:center;}}
td.diffsrc{{color:#cfe8dd;background:#0d1a14;}}
.evgrid{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:8px 0;}}
@media (max-width:760px){{.evgrid{{grid-template-columns:1fr;}}}}
.evcard{{border-radius:8px;padding:12px 14px;border:1px solid;}}
.ev-pro{{background:#0d1a14;border-color:#2f5a4a;}}
.ev-con{{background:#1d1214;border-color:#5a2f33;}}
.evtag{{font-size:11px;font-weight:700;letter-spacing:1px;margin-bottom:6px;}}
.ev-pro .evtag{{color:#2fb98a;}}
.ev-con .evtag{{color:#e05563;}}
.evtitle{{font-size:13.5px;font-weight:600;color:#e6e8ee;margin-bottom:6px;}}
.evcode{{margin:6px 0;}}
.evcode code{{display:block;font-family:Consolas,monospace;font-size:12px;background:#0d1424;border:1px solid #24406e;border-radius:5px;padding:5px 9px;margin:3px 0;color:#9cc2ff;white-space:pre-wrap;word-break:break-all;}}
.ev-pro .evcode code{{background:#0d1a14;border-color:#2f5a4a;color:#8fe3c0;}}
.ev-con .evcode code{{background:#1d1214;border-color:#5a2f33;color:#f0a0a8;}}
.evdesc{{font-size:12.5px;color:#b6c0d0;}}
.assetgrid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:10px;margin:8px 0;}}
.assetcard{{background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:10px 12px;border-left:3px solid var(--accent);}}
.asstype{{font-size:10.5px;color:var(--accent);letter-spacing:.5px;margin-bottom:4px;}}
.assname a{{font-family:Consolas,monospace;font-size:12.5px;font-weight:600;color:#9cc2ff;word-break:break-all;}}
.assdesc{{font-size:12px;color:#b6c0d0;margin:4px 0;}}
.assmeta{{font-size:10.5px;color:var(--dim);}}
</style>
</head>
<body>
<header>
  {crumb}
  <h1>{name}</h1>
  <div class="badges">{badges}</div>
</header>
<main>
{nav}
{body}
</main>
<footer>{title} · 节点页由 07-checkpoint/gen-nodes.py 生成 · 数据源 01-dag-data/opencodereview-dag.json + node-content.json</footer>
</body>
</html>
""".format(
        name=esc(node['name']), title=esc(TITLE), extra_css=BASE_CSS,
        crumb=crumb, badges=badges, nav=nav, body=body)
    return html


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    dag, content, by_id, c_by_id, group_by_id = load_all()
    edges = dag['edges']
    evidence_map = {}
    if os.path.exists(EVIDENCE_PATH):
        evidence_map = {n['id']: n['evidence'] for n in json.load(open(EVIDENCE_PATH, encoding='utf-8'))['nodes']}
    asset_map = {}
    if os.path.exists(ASSET_MANIFEST):
        for a in json.load(open(ASSET_MANIFEST, encoding='utf-8'))['assets']:
            for nid in a['node_ids']:
                asset_map.setdefault(nid, []).append(a)
    written = 0
    for node in dag['nodes']:
        gid = node['group']
        group = group_by_id[gid]
        cnt = c_by_id[node['id']]
        html = inject_shell(
            node_html(node['id'], node, cnt, group, edges, by_id,
                      evidence_map=evidence_map, asset_map=asset_map),
            '02-node-pages/%s.html' % node['id'])
        path = os.path.join(OUT_DIR, node['id'] + '.html')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        written += 1
    print('node pages written:', written)


if __name__ == '__main__':
    main()
