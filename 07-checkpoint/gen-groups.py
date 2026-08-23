#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 15 个组页 + 组总索引：03-groups/{group_id}.html + 03-groups/index.html

组页：节点目录表 + 组内 prerequisite 拓扑推荐顺序 + 前置依赖列表
index.html：组总索引，来源组/主题组/横切组不同配色区分。
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_common import (ROOT, TITLE, SUBTITLE, load_all, esc, build_indexes,
                        topo_sort, stage_badge, kind_badge, BASE_CSS,
                        KIND_STYLE, STAGE_STYLE, EDGE_STYLE, KIND_ORDER)

GROUPS_DIR = os.path.join(ROOT, '03-groups')


def group_html(gid, group, dag, by_id, c_by_id, group_by_id):
    edges = dag['edges']
    node_ids = group['node_ids']
    members = set(node_ids)
    stages = [n['stage'] for n in dag['nodes'] if n['id'] in members]
    stage_set = sorted(set(stages), key=lambda s: ('basic', 'intermediate', 'advanced').index(s))

    # 组内 prerequisite 边
    in_prereq = [e for e in edges if e['type'] == 'prerequisite' and e['from'] in members and e['to'] in members]
    topo = topo_sort(node_ids, edges)

    # 入组前置依赖（来自组外节点的 prerequisite 指向本组成员）
    external_in = [e for e in edges if e['type'] == 'prerequisite' and e['from'] not in members and e['to'] in members]
    external_in.sort(key=lambda e: e['to'])

    # 出组依赖（本组成员 prerequisite 指向组外）
    external_out = [e for e in edges if e['type'] == 'prerequisite' and e['from'] in members and e['to'] not in members]
    external_out.sort(key=lambda e: e['from'])

    cnt_by_id = {n['id']: n for n in dag['nodes']}

    # ---- 节点目录表 ----
    rows = []
    for nid in node_ids:
        n = by_id[nid]
        c = c_by_id.get(nid, {})
        brief = c.get('what', [''])[0] if c.get('what') else n['definition']
        rows.append(
            '<tr><td class="nid"><a href="../02-node-pages/%s.html">%s</a></td>'
            '<td><a href="../02-node-pages/%s.html" class="nname">%s</a></td>'
            '<td>%s</td>'
            '<td>%s</td>'
            '<td class="brief">%s</td></tr>'
            % (esc(nid), esc(nid), esc(nid), esc(n['name']),
               src_badge_inline(n['src']), stage_badge(n['stage']), esc(brief)))
    catalog = ('<div class="section"><h2>节点目录 <span class="dim">(%d 个)</span></h2>'
               '<div class="tblwrap"><table>'
               '<tr><th>节点 ID</th><th>名称</th><th>来源</th><th>阶段</th><th>简介</th></tr>'
               '%s</table></div></div>' % (len(node_ids), ''.join(rows)))

    # ---- 学习路径（拓扑推荐顺序）----
    seq = ' &rarr; '.join(
        '<a href="../02-node-pages/%s.html">%s</a>' % (esc(nid), esc(by_id[nid]['name']))
        for nid in topo)
    prereq_list = []
    for e in in_prereq:
        prereq_list.append(
            '<li><a href="../02-node-pages/%s.html">%s</a> &rarr; <a href="../02-node-pages/%s.html">%s</a>'
            '<span class="evi">%s</span></li>'
            % (esc(e['from']), esc(by_id[e['from']]['name']),
               esc(e['to']), esc(by_id[e['to']]['name']), esc(e['label'])))
    ext_in_list = []
    for e in external_in:
        ext_in_list.append(
            '<li><a href="../02-node-pages/%s.html">%s</a> &rarr; <a href="../02-node-pages/%s.html">%s</a>'
            '<span class="evi">%s</span></li>'
            % (esc(e['from']), esc(by_id[e['from']]['name']),
               esc(e['to']), esc(by_id[e['to']]['name']), esc(e['label'])))
    ext_out_list = []
    for e in external_out:
        ext_out_list.append(
            '<li><a href="../02-node-pages/%s.html">%s</a> &rarr; <a href="../02-node-pages/%s.html">%s</a>'
            '<span class="evi">%s</span></li>'
            % (esc(e['from']), esc(by_id[e['from']]['name']),
               esc(e['to']), esc(by_id[e['to']]['name']), esc(e['label'])))

    learn = ['<div class="section"><h2>学习路径提示</h2>']
    learn.append('<p class="dim">本组内存在 <strong>%d</strong> 条前置依赖边（prerequisite），'
                 '推荐先掌握前置知识点，再进入依赖它的节点。</p>' % len(in_prereq))
    learn.append('<div class="pathbox"><div class="path-label">推荐阅读顺序（拓扑序）</div>'
                 '<div class="path-seq">%s</div></div>' % seq)
    if prereq_list:
        learn.append('<ul class="dep-list">%s</ul>' % ''.join(prereq_list))
    if ext_in_list:
        learn.append('<h3>入组前置依赖（组外节点 → 本组成员）</h3><ul class="dep-list">%s</ul>'
                     % ''.join(ext_in_list))
    if ext_out_list:
        learn.append('<h3>出组依赖（本组成员 → 组外节点）</h3><ul class="dep-list">%s</ul>'
                     % ''.join(ext_out_list))
    learn.append('</div>')
    learn_html = ''.join(learn)

    kind_st = KIND_STYLE.get(group['kind'], KIND_STYLE['source'])
    badges = (kind_badge(group['kind']) + ' '.join(
        stage_badge(s) for s in stage_set)
        + '<span class="badge cnt" style="color:#9aa0ab;background:#23272f;border-color:#3a3f4a">%d 节点</span>'
        % len(node_ids))

    crumb = ('<div class="crumb"><a href="../index.html">%s</a> / <a href="../03-groups/index.html">分组目录</a>'
             ' / <span>%s</span></div>' % (esc(TITLE), esc(group['name'])))

    treenav = build_treenav(group_by_id)

    navseq = ('<div class="navseq">'
              '<a class="nav-index" href="../03-groups/index.html"><span class="dir">&#8592; 上一页</span><span class="v">组总索引</span></a>'
              '<a class="nav-index" href="../04-interactive/index.html"><span class="dir">全局</span><span class="v">交互总览</span></a>'
              '<a class="nav-node" href="../02-node-pages/%s.html"><span class="dir">进入本组首个节点</span><span class="v">%s</span></a>'
              '</div>'
              % (esc(topo[0]) if topo else esc(node_ids[0]),
                 esc(by_id[topo[0]]['name']) if topo else esc(by_id[node_ids[0]]['name'])))

    intro = ('<div class="section"><h2>组简介</h2><p>本组 <strong>%d</strong> 个节点，属于 <strong>%s</strong> 域'
             '，类型为 <strong>%s</strong>，覆盖阶段 <strong>%s</strong>。</p>'
             '<p class="dim">组节点：%s</p></div>'
             % (len(node_ids), esc(group['domain']),
                KIND_STYLE.get(group['kind'], {}).get('label', group['kind']),
                ' / '.join(STAGE_STYLE[s]['label'] for s in stage_set),
                '、'.join(esc(by_id[nid]['name']) for nid in node_ids)))

    body = '\n'.join([catalog, learn_html])

    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{gname} · 组索引 · {title}</title>
<style>
{extra_css}
.treenav{{display:block;}}
</style>
</head>
<body>
<header>
  {crumb}
  <h1>{gname}</h1>
  <div class="badges">{badges}</div>
</header>
<main>
  {treenav}
  {navseq}
  {intro}
  {body}
</main>
<footer>{title} · 组页由 07-checkpoint/gen-groups.py 生成 · 数据源 01-dag-data/opencodereview-dag.json</footer>
</body>
</html>
""".format(gname=esc(group['name']), title=esc(TITLE), extra_css=BASE_CSS,
           crumb=crumb, badges=badges, treenav=treenav, navseq=navseq,
           intro=intro, body=body)
    return html


def src_badge_inline(src):
    if src == 'app':
        return '<span class="badge src" style="color:#9cc2ff;background:#16273f;border-color:#4f8cff">App</span>'
    if src == 'agent':
        return '<span class="badge src" style="color:#ff8a97;background:#3a1520;border-color:#e05563">Agent</span>'
    return '<span class="badge src" style="color:#6fd3ae;background:#0f2b1f;border-color:#2fb98a">桥接</span>'


def build_treenav(group_by_id):
    items = []
    for g in group_by_id.values():
        items.append('<a href="%s.html">%s</a>' % (esc(g['id']), esc(g['name'])))
    return '<div class="treenav"><span class="label">组目录:</span>%s</div>' % ''.join(items)


def index_html(dag, group_by_id, by_id):
    total_nodes = len(dag['nodes'])
    total_groups = len(dag['groups'])
    total_edges = len(dag['edges'])
    stats = ('<div class="stat"><b>%d</b><span>节点</span></div>'
             '<div class="stat"><b>%d</b><span>组</span></div>'
             '<div class="stat"><b>%d</b><span>关系边</span></div>'
             '<div class="stat"><b>3</b><span>学习阶段</span></div>'
             '<div class="stat"><b>2</b><span>来源体系</span></div>'
             % (total_nodes, total_groups, total_edges))

    cards = []
    for kind in KIND_ORDER:
        ks = KIND_STYLE[kind]
        cards.append('<div class="section-title"><h2>%s</h2><span>%s</span></div>' % (ks['label'], ''))
        items = []
        for g in dag['groups']:
            if g['kind'] != kind:
                continue
            members = set(g['node_ids'])
            stages = sorted(set(by_id[n]['stage'] for n in g['node_ids']),
                            key=lambda s: ('basic', 'intermediate', 'advanced').index(s))
            stage_str = ' → '.join(
                '<span class="badge st" style="color:%s;background:%s;border-color:%s">%s</span>'
                % (STAGE_STYLE[s]['fg'], STAGE_STYLE[s]['bg'], STAGE_STYLE[s]['brd'], STAGE_STYLE[s]['label'])
                for s in stages)
            items.append(
                '<div class="card" style="border-left:4px solid %s"><a href="%s.html">'
                '<h3>%s · %s</h3>'
                '<div class="meta">%s ｜ %d 个节点</div>'
                '<div class="meta">%s</div>'
                '</a></div>'
                % (ks['brd'], esc(g['id']), esc(g['id']), esc(g['name']),
                   esc(g['domain']), len(g['node_ids']), stage_str))
        if items:
            cards.append('<div class="cards">%s</div>' % ''.join(items))

    crumb = '<div class="crumb"><a href="../index.html">%s</a> / <span>分组目录</span></div>' % esc(TITLE)

    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>分组目录 · {title}</title>
<style>
{extra_css}
.cards{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px;margin:12px 0;}}
.card{{background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:16px 18px;}}
.card:hover{{border-color:var(--accent);}}
.card h3{{font-size:15px;color:var(--accent);margin-bottom:6px;}}
.card .meta{{font-size:12px;color:var(--dim);margin-bottom:6px;}}
.stat{{display:inline-block;background:#1d2a3f;border:1px solid #2b3d5f;border-radius:8px;padding:10px 16px;margin:4px;text-align:center;}}
.stat b{{display:block;font-size:22px;color:#fff;}}
.stat span{{font-size:12px;color:var(--dim);}}
.section-title{{display:flex;align-items:baseline;gap:10px;margin:24px 0 10px;}}
.section-title h2{{margin:0;border:none;padding:0;}}
</style>
</head>
<body>
<header>
  {crumb}
  <h1>分组目录</h1>
  <p>{subtitle}</p>
</header>
<main>
  <div class="navseq">
    <a class="nav-index" href="../index.html"><span class="dir">&#8592; 上一页</span><span class="v">根入口</span></a>
    <a class="nav-index" href="../04-interactive/index.html"><span class="dir">全局</span><span class="v">交互总览</span></a>
    <a class="nav-index" href="../05-views/04-architecture.html"><span class="dir">下一站</span><span class="v">跨体系对照</span></a>
  </div>
  <h2>核心统计</h2>
  <div>{stats}</div>
  <h2>全部组</h2>
  {cards}
</main>
<footer>{title} · 组索引由 07-checkpoint/gen-groups.py 生成 · 数据源 01-dag-data/opencodereview-dag.json</footer>
</body>
</html>
""".format(title=esc(TITLE), subtitle=esc(SUBTITLE), extra_css=BASE_CSS,
           crumb=crumb, stats=stats, cards=''.join(cards))
    return html


def main():
    os.makedirs(GROUPS_DIR, exist_ok=True)
    dag, content, by_id, c_by_id, group_by_id = build_indexes_helper()
    for group in dag['groups']:
        html = group_html(group['id'], group, dag, by_id, c_by_id, group_by_id)
        with open(os.path.join(GROUPS_DIR, group['id'] + '.html'), 'w', encoding='utf-8') as f:
            f.write(html)
    idx = index_html(dag, group_by_id, by_id)
    with open(os.path.join(GROUPS_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(idx)
    print('group pages written:', len(dag['groups']))


def build_indexes_helper():
    from gen_common import load_all
    dag, content, by_id, c_by_id, group_by_id = load_all()
    return dag, content, by_id, c_by_id, group_by_id


if __name__ == '__main__':
    main()
