#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 05-views/ 下的视图页（OpenCodeReview 图谱版）：
  index.html            视图入口（统计卡 + 导航）
  02-scenarios.html     工具使用场景索引（场景 → 命令速查 → 关联节点，兼作工具库索引）
  03-learning-path.html 学习路径（三档阶段 + 全拓扑序）
  04-architecture.html  分层架构视图（7 组按层次浏览）
"""
import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_common import (ROOT, TITLE, SUBTITLE, load_all, esc, build_indexes,
                        topo_sort, stage_badge, src_badge, type_badge,
                        group_badge, BASE_CSS, STAGE_STYLE, SRC_STYLE,
                        EDGE_STYLE, KIND_STYLE)

VIEWS_DIR = os.path.join(ROOT, '05-views')


def views_header(title, subtitle):
    return ('<header><h1>%s</h1><p>%s</p></header>'
            '<main><div class="back"><a href="index.html">&larr; 返回视图入口</a></div>'
            % (esc(title), esc(subtitle)))


def views_footer():
    return ('</main><footer>%s · 由 07-checkpoint/gen-views.py 生成 · '
            '数据源 01-dag-data/opencodereview-dag.json + node-content.json</footer>'
            % esc(TITLE))


def wrap(title, body, header_html, extra_css=''):
    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} · {site}</title>
<style>
{base_css}
.back a{{color:var(--accent);text-decoration:none;font-size:14px;}}
{extra_css}
</style>
</head>
<body>
{header}
{body}
</body>
</html>""".format(title=esc(title), site=esc(TITLE), base_css=BASE_CSS,
                 extra_css=extra_css, header=header_html, body=body)


# ---------------------------------------------------------------- 视图入口
def view_index_html(dag, by_id):
    stats = ('<div class="stat"><b>%d</b><span>节点</span></div>'
             '<div class="stat"><b>%d</b><span>分组</span></div>'
             '<div class="stat"><b>%d</b><span>关系边</span></div>'
             '<div class="stat"><b>3</b><span>学习阶段</span></div>'
             '<div class="stat"><b>6</b><span>使用场景</span></div>'
             % (len(dag['nodes']), len(dag['groups']), len(dag['edges'])))
    cards = (
        '<div class="card"><h3>使用场景索引</h3><p>按任务找工具：审 PR / 扫代码库 / 免 Key 委托 / CI 接入 / 配置规则 / 扩展能力，含命令速查。</p>'
        '<a class="go" href="02-scenarios.html">打开场景索引</a></div>'
        '<div class="card"><h3>学习路径</h3><p>基础 → 进阶 → 高级三档推进 + 全图谱拓扑序，从安装到精通。</p>'
        '<a class="go" href="03-learning-path.html">查看学习路径</a></div>'
        '<div class="card"><h3>分层架构视图</h3><p>核心架构 → 审查引擎 → 命令行 → 配置模型 → 集成生态 → 工程保障，按层浏览。</p>'
        '<a class="go" href="04-architecture.html">按层浏览</a></div>'
        '<div class="card"><h3>交互 DAG 总览</h3><p>组级视图 + 点击下钻 + 关系边高亮，cytoscape 渲染。</p>'
        '<a class="go" href="../04-interactive/index.html">打开交互总览</a></div>'
        '<div class="card"><h3>12 原则对照审查</h3><p>用 12 Factor App/Agent 原则审视 OCR 设计：24 条原则 × 对应机制 × 审查结论。</p>'
        '<a class="go" href="05-principles.html">查看对照审查</a></div>')
    body = ('<h2>核心统计</h2><div>%s</div>'
            '<h2>视图入口</h2><div class="cards">%s</div>'
            '<h2>快速开始</h2><ul class="steps">'
            '<li><b>想直接用</b>：打开使用场景索引，按你的任务找命令。</li>'
            '<li><b>想系统学</b>：走学习路径或分层架构视图，从核心架构读起。</li>'
            '<li><b>想理解全貌</b>：打开交互 DAG 总览，看 7 组 %d 节点的依赖拓扑。</li>'
            '<li><b>想方法论定位</b>：打开 12 原则对照审查，看 OCR 在 12 Factor App/Agent 坐标系中的合规度。</li>'
            '</ul>' % (stats, cards, len(dag['nodes'])))
    return wrap('视图入口', body, views_header('视图入口', SUBTITLE),
                extra_css="""
.stat{display:inline-block;background:#1d2a3f;border:1px solid #2b3d5f;border-radius:8px;padding:10px 16px;margin:4px;text-align:center;}
.stat b{display:block;font-size:22px;color:#fff;}
.stat span{font-size:12px;color:var(--dim);}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:14px;margin:12px 0;}
.card{background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:18px;}
.card h3{font-size:16px;color:var(--accent);margin:0 0 8px;}
.card p{font-size:13px;color:var(--dim);margin-bottom:12px;}
.card .go{display:inline-block;background:#1d2a3f;border:1px solid #2b3d5f;border-radius:8px;padding:6px 14px;color:#fff;font-size:13px;}
.card .go:hover{border-color:var(--accent);}
.steps li{margin:6px 0;font-size:14px;color:#cfd6e4;}
""")


# ---------------------------------------------------------------- 场景索引
def scenario_html(dag, content, by_id, c_by_id, group_by_id):
    """工具使用场景索引：G-S 场景节点卡片 + 命令速查 + 关联工具节点。"""
    scen_nodes = [n for n in dag['nodes'] if n['src'] == 'scenario']
    scen_nodes.sort(key=lambda n: n['id'])
    edges = dag['edges']
    node_by_id = {n['id']: n for n in dag['nodes']}

    # 速查总表：场景 → 核心命令（从 how 中提取含 ocr 的行）
    def cmd_lines(nid):
        c = c_by_id.get(nid, {})
        cmds = []
        for it in (c.get('how') or []):
            if 'ocr ' in it or 'ocr.' in it:
                cmds.append(it)
        return cmds[:4]

    rows = []
    for n in scen_nodes:
        cmds = cmd_lines(n['id'])
        first_cmd = cmds[0] if cmds else '—'
        rows.append('<tr><td class="scen"><a href="#%s">%s</a></td><td class="cmd">%s</td></tr>'
                    % (esc(n['id']), esc(n['name']), esc(first_cmd)))
    table = ('<h2>场景速查总表</h2><div class="tblwrap"><table>'
             '<thead><tr><th>场景</th><th>核心命令</th></tr></thead><tbody>%s</tbody></table></div>'
             % ''.join(rows))

    # 场景卡片
    cards = []
    for n in scen_nodes:
        c = c_by_id.get(n['id'], {})
        cmds = cmd_lines(n['id'])
        rel = [e for e in edges if e['from'] == n['id'] or e['to'] == n['id']]
        rel_links = []
        for e in rel:
            other = e['to'] if e['from'] == n['id'] else e['from']
            on = node_by_id.get(other, {})
            arrow = '&#8594;' if e['from'] == n['id'] else '&#8592;'
            st = EDGE_STYLE.get(e['type'], EDGE_STYLE['dependency'])
            rel_links.append('<a class="chip e-%s" href="../02-node-pages/%s.html">%s%s%s<span class="etype">%s</span></a>'
                             % (e['type'], esc(other), esc(on.get('name', other)), arrow,
                                esc(e.get('label', '')), st['label']))
        cmd_html = ''
        if cmds:
            cmd_html = ('<div class="cmdbox"><div class="cmdlabel">命令速查</div>%s</div>'
                        % ''.join('<code>%s</code>' % esc(x) for x in cmds))
        what = (c.get('what') or [])[:3]
        why = (c.get('why') or [])[:2]
        what_html = ''.join('<div class="bullet">%s</div>' % esc(x) for x in what)
        why_html = ''.join('<div class="bullet">%s</div>' % esc(x) for x in why)
        anti = (c.get('anti_patterns') or [])[:2]
        anti_html = ''.join('<li>%s</li>' % esc(x) for x in anti) if anti else ''
        cards.append("""
<div class="scen-card" id="{sid}">
  <div class="scen-head">
    <h3>{name}</h3>
    {src_badge}{type_badge}
    <div class="brief">{defn}</div>
  </div>
  {cmd_html}
  <div class="scen-grid">
    <div class="scen-col"><h4>适用情况</h4>{what_html}</div>
    <div class="scen-col"><h4>为什么用</h4>{why_html}</div>
  </div>
  {anti}
  <div class="rel"><span class="rellabel">关联节点</span>{rel_links}</div>
</div>""".format(
            sid=esc(n['id']), name=esc(n['name']),
            src_badge=src_badge(n['src']), type_badge=type_badge(n),
            defn=esc(n['definition']), cmd_html=cmd_html,
            what_html=what_html, why_html=why_html,
            anti=('<h4 class="antih">常见坑</h4><ul class="pit">%s</ul>' % anti_html) if anti_html else '',
            rel_links=''.join(rel_links) if rel_links else '<span class="dim">（无）</span>'))
    body = (table + '<h2>场景详解</h2>' + ''.join(cards))
    return wrap('使用场景索引', body, views_header('使用场景索引 · 工具库索引', SUBTITLE),
                extra_css="""
.scen-card{background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:18px;margin:14px 0;}
.scen-head h3{font-size:17px;color:var(--accent);display:inline-block;margin-right:10px;}
.brief{font-size:13.5px;color:#cfe8dd;background:#0d1a14;border:1px solid #2f5a4a;border-left:4px solid var(--ok);border-radius:6px;padding:8px 12px;margin:8px 0;}
.cmdbox{background:#0d1424;border:1px solid #24406e;border-radius:8px;padding:10px 14px;margin:8px 0;}
.cmdlabel{font-size:11px;color:var(--dim);margin-bottom:6px;letter-spacing:1px;}
.cmdbox code{display:block;font-family:Consolas,monospace;font-size:12.5px;color:#9cc2ff;background:#16273f;border-radius:5px;padding:6px 10px;margin:4px 0;white-space:pre-wrap;word-break:break-all;}
.scen-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:8px 0;}
@media (max-width:720px){.scen-grid{grid-template-columns:1fr;}}
.scen-col h4{font-size:13px;color:var(--dim);margin:8px 0 6px;}
.bullet{background:#10151f;border:1px solid var(--border);border-radius:6px;padding:7px 12px;margin:5px 0;font-size:13px;color:#d3d9e4;}
.antih{font-size:13px;color:var(--warn);margin:10px 0 4px;}
.pit li{margin:4px 0;font-size:13px;}
.pit li::marker{color:var(--warn);}
.rel{margin-top:10px;border-top:1px dashed var(--border);padding-top:8px;}
.rellabel{font-size:11px;color:var(--dim);margin-right:8px;}
.tblwrap table th{background:var(--panel);}
td.scen{white-space:nowrap;}
td.scen a{color:#ff8a97;font-weight:600;}
td.cmd{font-family:Consolas,monospace;font-size:12px;color:#9cc2ff;}
""")


# ---------------------------------------------------------------- 学习路径
def learning_html(dag, by_id, group_by_id):
    stages = ['basic', 'intermediate', 'advanced']
    nav = '<div class="layer-nav">' + ''.join(
        '<a href="#layer-%d">%s（%d）</a>' % (i, STAGE_STYLE[s]['label'],
                                              sum(1 for n in dag['nodes'] if n['stage'] == s))
        for i, s in enumerate(stages)) + '</div>'
    secs = []
    for i, s in enumerate(stages):
        st = STAGE_STYLE[s]
        nodes = sorted([n for n in dag['nodes'] if n['stage'] == s],
                       key=lambda n: (n['group'], n['id']))
        rows = []
        for n in nodes:
            gname = group_by_id[n['group']]['name']
            rows.append(
                '<div class="row"><span class="nm"><a href="../02-node-pages/%s.html">%s</a></span>'
                '%s<span class="badge b-grp">%s · %s</span>'
                '<span class="brief">%s</span></div>'
                % (esc(n['id']), esc(n['name']), src_badge(n['src']),
                   esc(n['group']), esc(gname), esc(n['definition'])))
        secs.append('<div class="sec-head" id="layer-%d"><h2>Layer %d · %s</h2><span>%d 个节点</span></div>'
                    '<div class="sec-card">%s</div>' % (i, i, st['label'], len(nodes), ''.join(rows)))

    # 全图谱拓扑路径
    order = topo_sort([n['id'] for n in dag['nodes']], dag['edges'])
    path_items = []
    for i, nid in enumerate(order, 1):
        n = dag['nodes'][dag['nodes'].index(by_id[nid])]
        path_items.append('<a href="../02-node-pages/%s.html">%d. %s</a>' % (esc(nid), i, esc(n['name'])))
    path_html = ('<div class="pathbox"><div class="path-label">全图谱拓扑学习路径（prerequisite 边驱动，%d 步）</div>'
                 '<div class="path-seq">%s</div></div>' % (len(order), ''.join(path_items)))

    body = ('<h2>学习阶段</h2>' + nav + ''.join(secs) + '<h2>拓扑学习路径</h2>' + path_html)
    return wrap('学习路径', body, views_header('学习路径', SUBTITLE),
                extra_css="""
.layer-nav{display:flex;gap:8px;margin:8px 0 16px;flex-wrap:wrap;}
.layer-nav a{background:var(--panel);border:1px solid var(--border);border-radius:20px;padding:4px 14px;font-size:13px;color:var(--dim);}
.layer-nav a:hover{color:var(--accent);border-color:var(--accent);}
.sec-head{display:flex;align-items:baseline;gap:10px;margin:20px 0 8px;border-bottom:1px solid var(--border);padding-bottom:6px;}
.sec-head h2{font-size:17px;color:#cfd6e4;border:none;margin:0;padding:0;}
.sec-head span{font-size:12px;color:var(--dim);}
.sec-card{background:var(--panel);border:1px solid var(--border);border-radius:10px;padding:8px 14px;}
.row{display:flex;align-items:baseline;gap:10px;padding:8px 4px;border-bottom:1px solid var(--border);flex-wrap:wrap;}
.row:last-child{border-bottom:none;}
.row .nm a{font-weight:600;font-size:14px;color:var(--text);}
.row .nm a:hover{color:var(--accent);}
.row .brief{font-size:12px;color:var(--dim);flex:1;min-width:220px;}
.badge.b-grp{background:#1d2a3f;color:#7fb0ff;border-color:#2b3d5f;font-size:11px;padding:1px 8px;border-radius:20px;border:1px solid;}
.pathbox{background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:12px 16px;margin:10px 0;}
.path-label{font-size:12px;color:var(--dim);margin-bottom:8px;}
.path-seq{display:flex;flex-wrap:wrap;gap:4px 0;font-size:13px;}
.path-seq a{display:inline-block;background:#16273f;border:1px solid #2b3d5f;border-radius:6px;padding:2px 8px;color:#7fb0ff;text-decoration:none;margin:2px;}
.path-seq a:hover{background:#2b3d5f;}
""")


# ---------------------------------------------------------------- 架构分层
def architecture_html(dag, by_id):
    kind_order = ['source', 'tool', 'crosscut', 'scenario']
    kind_label = {'source': '架构与机制', 'tool': '工具', 'crosscut': '保障', 'scenario': '场景索引'}
    secs = []
    for kind in kind_order:
        groups = [g for g in dag['groups'] if g['kind'] == kind]
        if not groups:
            continue
        k = KIND_STYLE.get(kind, KIND_STYLE['source'])
        rows_all = []
        for g in groups:
            rows = []
            for nid in g['node_ids']:
                n = by_id[nid]
                rows.append('<div class="row"><span class="nm"><a href="../02-node-pages/%s.html">%s</a></span>'
                            '%s<span class="brief">%s</span></div>'
                            % (esc(nid), esc(n['name']), src_badge(n['src']), esc(n['definition'])))
            rows_all.append('<div class="grp-block"><div class="grp-head">%s · %s <span class="dim">（%s）</span> · %d 节点</div>%s</div>'
                            % (esc(g['id']), esc(g['name']), esc(g['domain']), len(g['node_ids']), ''.join(rows)))
        secs.append('<div class="layer-sec"><h2 style="color:%s;border-color:%s">%s 层</h2>%s</div>'
                    % (k['fg'], k['brd'], kind_label[kind], ''.join(rows_all)))
    body = ('<p class="dim">按图谱分组类别分层：先架构理念与引擎机制，再命令行工具与配置，随后集成生态，工程保障横切支撑，最后是使用场景索引。</p>'
            + ''.join(secs))
    return wrap('分层架构视图', body, views_header('分层架构视图', SUBTITLE),
                extra_css="""
.layer-sec{margin:18px 0;}
.layer-sec>h2{font-size:17px;padding-bottom:6px;border-bottom:2px solid;}
.grp-block{background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:10px 14px;margin:10px 0;}
.grp-head{font-size:14px;font-weight:600;color:#b8c2d4;margin-bottom:6px;}
.row{display:flex;align-items:baseline;gap:10px;padding:6px 4px;border-bottom:1px solid var(--border);flex-wrap:wrap;}
.row:last-child{border-bottom:none;}
.row .nm a{font-weight:600;font-size:13.5px;}
.row .brief{font-size:12px;color:var(--dim);flex:1;min-width:200px;}
""")


def principles_html(dag, by_id):
    """12 原则对照审查：App 12 条 + Agent 12 条 × OCR 机制 × 审查结论"""
    PRIN = os.path.join(ROOT, '01-dag-data', 'principles-mapping.json')
    if not os.path.exists(PRIN):
        return wrap('12 原则对照审查', '<p class="dim">principles-mapping.json 缺失</p>',
                    views_header('12 原则对照审查', SUBTITLE))
    data = json.load(open(PRIN, encoding='utf-8'))
    verdict_color = {'合规': '#2fb98a', '部分合规': '#e8933b', '有张力': '#e05563'}

    def table(items, sys_name, sys_color):
        rows = []
        for it in items:
            vc = verdict_color.get(it['verdict'], '#e8933b')
            rows.append('<tr><td class="pid">%s</td><td class="pname">%s</td>'
                        '<td class="pclaim">%s</td><td class="pmech">%s</td>'
                        '<td class="pverdict" style="color:%s">%s</td></tr>'
                        % (esc(it['id']), esc(it['name']), esc(it['claim']),
                           esc(it['ocr_mechanism']), vc, esc(it['verdict'])))
        return ('<h2 style="border-color:%s;color:%s">%s · 12 条</h2>'
                '<div class="tblwrap"><table class="principle-table">'
                '<thead><tr><th>原则</th><th>主张</th><th>OCR 对应机制</th><th>审查结论</th></tr></thead>'
                '<tbody>%s</tbody></table></div>' % (sys_color, sys_color, sys_name, ''.join(rows)))

    summary = []
    all_items = data['app_principles'] + data['agent_principles']
    from collections import Counter
    cnt = Counter(it['verdict'] for it in all_items)
    summary.append('<div class="sumcard"><b>%d</b><span>合规</span></div>'
                   '<div class="sumcard"><b>%d</b><span>部分合规</span></div>'
                   '<div class="sumcard"><b>%d</b><span>有张力</span></div>'
                   % (cnt.get('合规', 0), cnt.get('部分合规', 0), cnt.get('有张力', 0)))

    body = ('<div class="brieflead">审查标尺：12 Factor App（传统软件工程）与 12 Factor Agent（LLM Agent 工程）'
            '合并图谱的 24 条原则（来源：0823-12factor-methodology）。逐条对照 open-code-review 的设计机制，'
            '给出合规/部分合规/有张力结论。审查目的：验证 OCR 是否落在 12 原则坐标系上，'
            '并暴露设计中的张力点供取舍参考。</div>'
            '<h2>审查总览</h2><div>%s</div>'
            % ''.join(summary))
    body += table(data['app_principles'], '12 Factor App 原则', '#4f8cff')
    body += table(data['agent_principles'], '12 Factor Agent 原则', '#e05563')
    body += ('<h2>审查小结</h2><div class="whybox">'
             '<p>OCR 的核心架构（确定性流水线 + 规则引导分派 + 文件级子 Agent + 独立反思）与 <b>12 Factor Agent</b> '
             '高度同构：控制流由代码决定（ag-control）、上下文工程化（ag-context）、小 Agent 组合（ag-small）、'
             '无状态可重放（ag-reducer）均是完全合规。与 <b>12 Factor App</b> 的对照同样出色：'
             '配置外置（app-config）、后端服务可替换（app-backing）、日志事件流（app-logs）、'
             '可处置性（app-disposability）全部落在原则坐标系上。</p>'
             '<p>两处张力/部分合规：①<em>开发/线上等价</em>——CI 与本地环境差异由配置优先级弥合而非环境等价；'
             '②<em>人类接入</em>——审查工具面向人类审查员但无主动 seek-approval 流程，'
             '属审查场景的合理取舍（审查非执行类任务）。</p></div>')
    return wrap('12 原则对照审查', body, views_header('12 原则对照审查 · 方法论定位', SUBTITLE),
                extra_css="""
.brieflead{background:#0d1a14;border:1px solid #2f5a4a;border-left:4px solid var(--ok);border-radius:8px;padding:12px 16px;font-size:14px;color:#cfe8dd;margin:12px 0;}
.sumcard{display:inline-block;background:#1d2a3f;border:1px solid #2b3d5f;border-radius:8px;padding:10px 16px;margin:4px;text-align:center;}
.sumcard b{display:block;font-size:22px;color:#fff;}
.sumcard span{font-size:12px;color:var(--dim);}
.principle-table th{background:var(--panel);}
.principle-table td{font-size:12.5px;}
td.pid{white-space:nowrap;font-family:Consolas,monospace;font-size:11.5px;color:#8fb5ff;}
td.pname{font-weight:600;white-space:nowrap;}
td.pclaim{color:#b6c0d0;max-width:260px;}
td.pmech{color:#d3d9e4;max-width:380px;}
td.pverdict{font-weight:700;white-space:nowrap;}
.whybox{background:var(--panel);border:1px solid var(--border);border-left-width:4px;border-radius:8px;padding:14px 18px;margin:10px 0;font-size:14px;color:#d3d9e4;}
.whybox p{margin:8px 0;}
""")


def main():
    dag, content, by_id, c_by_id, group_by_id = load_all()
    os.makedirs(VIEWS_DIR, exist_ok=True)
    files = {
        'index.html': view_index_html(dag, by_id),
        '02-scenarios.html': scenario_html(dag, content, by_id, c_by_id, group_by_id),
        '03-learning-path.html': learning_html(dag, by_id, group_by_id),
        '04-architecture.html': architecture_html(dag, by_id),
        '05-principles.html': principles_html(dag, by_id),
    }
    for name, html in files.items():
        with open(os.path.join(VIEWS_DIR, name), 'w', encoding='utf-8') as f:
            f.write(html)
        print('views:', name, len(html), 'bytes')


if __name__ == '__main__':
    main()