#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成交互 DAG：04-interactive/index.html

cytoscape + dagre，两级下钻（组级视图 → 点击组 → 组内 DAG）。
桥接高亮模式：按钮切换，只显示 bridge 主题节点及其连接边。
DATA 用内联 JS 对象注入（nodes 含 id/name/type/group/stage，edges 含 from/to/type/label，
groupColor/stageColor 映射）。vendor 从 0820 复制（cytoscape.min.js + cytoscape-dagre.min.js）。
JS 为完整 IIFE，避免全局污染。
"""
import json
import os
import shutil
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_common import (ROOT, TITLE, SUBTITLE, load_all, esc, topo_sort,
                        EDGE_STYLE, SRC_STYLE)

INTER_DIR = os.path.join(ROOT, '04-interactive')
VENDOR_DIR = os.path.join(INTER_DIR, 'vendor')
SRC_VENDOR = os.path.join(INTER_DIR, 'vendor')
SRC_VENDOR_ABS = os.path.join(INTER_DIR, 'vendor')

GROUP_COLOR_MAP = {
    'G-A': '#4f8cff', 'G-B': '#7fe0d8', 'G-C': '#e8c66a',
    'G-D': '#c9a8ef', 'G-E': '#e05563', 'G-F': '#2fb98a', 'G-S': '#ffb86b',
}
STAGE_COLOR_MAP = {
    'basic': '#4f8cff',
    'intermediate': '#2fb98a',
    'advanced': '#e8933b',
}
EDGE_COLOR_MAP = {k: v['brd'] for k, v in EDGE_STYLE.items()}


def build_data(dag, content):
    """构造内联 DATA 对象（与 0820 结构对齐）。"""
    nodes = []
    for n in dag['nodes']:
        nodes.append({
            'id': n['id'],
            'name': n['name'],
            'type': n['type'],
            'src': n['src'],
            'group': n['group'],
            'stage': n['stage'],
            'brief': n['definition'],
        })
    edges = []
    for e in dag['edges']:
        edges.append({'from': e['from'], 'to': e['to'], 'type': e['type'], 'label': e['label']})

    groupEdges = []
    # 组间 prerequisite 聚合（源组→目标组），保留经由节点对
    seen = set()
    for e in dag['edges']:
        if e['type'] != 'prerequisite':
            continue
        f, t = e['from'], e['to']
        gf = node_group_of(dag, f)
        gt = node_group_of(dag, t)
        if gf == gt or gf is None or gt is None:
            continue
        key = gf + '|' + gt
        if key in seen:
            continue
        seen.add(key)
        groupEdges.append({'source': gf, 'target': gt, 'viaFrom': f, 'viaTo': t, 'type': e['type']})

    groups = []
    for g in dag['groups']:
        stages = sorted(set(n['stage'] for n in dag['nodes'] if n['id'] in g['node_ids']),
                        key=lambda s: ('basic', 'intermediate', 'advanced').index(s))
        groups.append({
            'id': g['id'],
            'name': g['name'],
            'domain': g['domain'],
            'kind': g['kind'],
            'stage_range': stages,
            'node_ids': g['node_ids'],
        })

    return {
        'meta': {
            'title': TITLE,
            'subtitle': SUBTITLE,
            'generated': '2026-08-23',
            'total_groups': len(dag['groups']),
            'total_nodes': len(dag['nodes']),
            'total_edges': len(dag['edges']),
            'stages': dag['meta']['stages'],
            'edge_types': dag['meta']['edge_types'],
            'dag_acyclic': True,
        },
        'groups': groups,
        'nodes': nodes,
        'edges': edges,
        'groupEdges': groupEdges,
        'groupColor': GROUP_COLOR_MAP,
        'stageColor': STAGE_COLOR_MAP,
        'edgeColor': EDGE_COLOR_MAP,
    }


def node_group_of(dag, nid):
    for g in dag['groups']:
        if nid in g['node_ids']:
            return g['id']
    return None


CSS = """
  :root { --bg:#0f1117; --panel:#161a22; --border:#2a2f3a; --text:#e6e8ee; --dim:#9aa3b2; --accent:#4f8cff; --warn:#e0c35e; --danger:#e05563; }
  * { box-sizing:border-box; margin:0; padding:0; }
  body { background:var(--bg); color:var(--text); font-family:'Segoe UI',system-ui,sans-serif; height:100vh; overflow:hidden; }
  header { position:fixed; top:0; left:0; right:0; z-index:10; background:var(--panel); border-bottom:1px solid var(--border); padding:8px 16px; display:flex; align-items:center; gap:12px; flex-wrap:wrap; }
  header h1 { font-size:15px; font-weight:600; white-space:nowrap; }
  header a { color:var(--accent); text-decoration:none; font-size:13px; }
  header a:hover { text-decoration:underline; }
  .badge { background:#20324f; color:#7fb0ff; padding:2px 10px; border-radius:20px; font-size:12px; white-space:nowrap; }
  .hint { color:var(--dim); font-size:11px; }
  .controls { display:flex; align-items:center; gap:6px; flex-wrap:wrap; }
  .seg { display:inline-flex; background:#0b0e14; border:1px solid var(--border); border-radius:8px; overflow:hidden; }
  .seg button { background:transparent; color:var(--dim); border:none; padding:5px 12px; font-size:12px; cursor:pointer; white-space:nowrap; }
  .seg button.active { background:var(--accent); color:#fff; }
  .seg button:hover:not(.active) { color:var(--text); }
  .btn { background:#20324f; color:#7fb0ff; border:1px solid #2a3a55; border-radius:20px; padding:4px 14px; font-size:12px; cursor:pointer; white-space:nowrap; }
  .btn:hover { background:#2a3a55; }
  .btn.primary { background:var(--accent); color:#fff; border-color:var(--accent); }
  .btn.on { background:#0f2b1f; color:#6fd3ae; border-color:#2fb98a; }
  #side { position:fixed; right:0; top:52px; bottom:0; width:300px; background:var(--panel); border-left:1px solid var(--border); padding:14px; overflow:auto; z-index:9; }
  #side h2 { font-size:13px; margin-bottom:8px; color:var(--dim); }
  #side .legend { font-size:12px; color:var(--dim); line-height:1.9; }
  #side .legend b { color:var(--text); }
  #side .legend .sw { display:inline-block; width:12px; height:12px; border-radius:3px; margin-right:6px; vertical-align:-1px; }
  #zoominfo { position:fixed; bottom:14px; left:18px; background:var(--panel); border:1px solid var(--border); border-radius:8px; padding:7px 12px; font-size:12px; color:var(--dim); z-index:9; }
  #zoominfo b { color:var(--text); }
  #crumb { position:fixed; top:52px; left:18px; background:var(--panel); border:1px solid var(--border); border-radius:8px; padding:6px 12px; font-size:12px; color:var(--dim); z-index:9; display:none; align-items:center; gap:8px; }
  #crumb b { color:var(--accent); }
  #crumb a { color:var(--dim); cursor:pointer; text-decoration:underline; }
  #crumb a:hover { color:var(--accent); }
  #graph { position:fixed; top:52px; left:0; right:0; bottom:0; }
  #glegend { margin-top:6px; }
  #glegend .row { display:flex; align-items:center; gap:8px; font-size:12px; color:var(--dim); margin:3px 0; cursor:pointer; }
  #glegend .row:hover { color:var(--text); }
  #glegend .row .sw { width:14px; height:14px; border-radius:3px; flex:0 0 auto; }
  #glegend .row.active { color:var(--text); font-weight:600; }
  #empty { position:fixed; inset:0; top:52px; display:none; align-items:center; justify-content:center; color:var(--dim); font-size:14px; background:var(--bg); z-index:5; }
  @media (max-width:768px){
    #side { width:220px; }
    header { padding:6px 10px; gap:8px; }
    header h1 { font-size:13px; }
    .hint { display:none; }
  }
"""

JS = r"""
(function(){
  'use strict';
  const DATA = __DATA__;

  // ===== 常量 =====
  const EDGE_COLOR = DATA.edgeColor;
  const STAGE_ORDER = ['basic','intermediate','advanced'];
  const STAGE_LABEL = { basic:'基础', intermediate:'进阶', advanced:'高级' };
  const STAGE_COLOR = DATA.stageColor;
  const EDGE_LABEL = { prerequisite:'前置(prerequisite)', variant:'变体(variant)', combination:'组合(combination)', cooccurrence:'共现(cooccurrence)', dependency:'依赖关联(dependency)' };

  const nodeById = {};
  DATA.nodes.forEach(n => nodeById[n.id] = n);
  const groupById = {};
  DATA.groups.forEach(g => groupById[g.id] = g);
  const nodeToGroup = {};
  DATA.groups.forEach(g => g.node_ids.forEach(nid => nodeToGroup[nid] = g.id));
  const groupNodeIndex = {};
  DATA.groups.forEach(g => g.node_ids.forEach((nid,i) => { groupNodeIndex[nid] = i; }));

  // ===== 状态 =====
  let currentGroup = null;   // null = 组级视图
  let bridgeMode = false;    // 桥接高亮模式

  const $ = id => document.getElementById(id);
  const crumb = $('crumb');

  function isBridge(nid){ const n = nodeById[nid]; return n && (n.type === 'bridge' || n.src === 'bridge'); }

  // ===== 组级视图 =====
  function buildGroupNodes(){
    const nodes = DATA.groups.map(g => ({
      data:{
        id:'grp-'+g.id, label: g.name, kind:'group', group:g.id, gname:g.name,
        domain:g.domain, gkind:g.kind,
        coreCount: g.node_ids.length,
        totalCount: g.node_ids.length
      }
    }));
    let edges = [];
    DATA.groupEdges.forEach(ge => {
      edges.push({ data:{ id:'grp-'+ge.source+'->grp-'+ge.target, source:'grp-'+ge.source, target:'grp-'+ge.target, kind:'group', type:ge.type, viaFrom:ge.viaFrom, viaTo:ge.viaTo } });
    });
    const seen = new Set();
    edges = edges.filter(e => {
      const k = e.data.source+'|'+e.data.target;
      if (seen.has(k)) return false;
      seen.add(k); return true;
    });
    return { nodes, edges };
  }

  // ===== 组内视图（含跨组 stub）=====
  function buildGroupDrill(gid){
    const g = groupById[gid];
    const members = g.node_ids;
    const memberSet = new Set(members);
    const relatedIds = new Set(members);
    const edges = [];
    DATA.edges.forEach(e => {
      if (bridgeMode && !(isBridge(e.from) || isBridge(e.to))) return;
      const s = e.from, t = e.to;
      const sIn = memberSet.has(s), tIn = memberSet.has(t);
      if (sIn && tIn){
        edges.push({ data:{ id:s+'->'+t, source:s, target:t, type:e.type, label:e.label } });
      } else if (sIn || tIn){
        const other = sIn ? t : s;
        if (nodeById[other] && !memberSet.has(other)){
          relatedIds.add(other);
          edges.push({ data:{ id:s+'->'+t, source:s, target:t, type:e.type, label:e.label } });
        }
      }
    });
    const nodes = [];
    relatedIds.forEach(id => {
      const n = nodeById[id];
      if (!n) return;
      const isMember = memberSet.has(id);
      nodes.push({
        data:{
          id, label:n.name, kind:'node', group:n.group, gname: groupById[n.group] ? groupById[n.group].name : '',
          stage:n.stage, src:n.src, brief:n.brief || '',
          member:isMember, mode: isMember ? 'member' : 'stub'
        }
      });
    });
    nodes.sort((a,b) => {
      const am = a.data.member ? 0 : 1, bm = b.data.member ? 0 : 1;
      if (am !== bm) return am - bm;
      if (a.data.member) return groupNodeIndex[a.data.id] - groupNodeIndex[b.data.id];
      return a.data.id < b.data.id ? -1 : 1;
    });
    return { nodes, edges };
  }

  // ===== 桥接模式：只看 bridge 主题及其连接边 =====
  function buildBridgeView(){
    const bridgeIds = DATA.nodes.filter(n => isBridge(n.id)).map(n => n.id);
    const idSet = new Set(bridgeIds);
    const nodes = bridgeIds.map(id => {
      const n = nodeById[id];
      return { data:{ id, label:n.name, kind:'node', group:n.group, gname: groupById[n.group]?groupById[n.group].name:'', stage:n.stage, src:n.src, brief:n.brief||'', member:true, mode:'member' } };
    });
    const edges = [];
    DATA.edges.forEach(e => {
      if (idSet.has(e.from) && idSet.has(e.to)){
        edges.push({ data:{ id:e.from+'->'+e.to, source:e.from, target:e.to, type:e.type, label:e.label } });
      }
    });
    return { nodes, edges };
  }

  // ===== 渲染 =====
  function render(doFit=true){
    let els, mode;
    if (bridgeMode){
      els = buildBridgeView();
      mode = '桥接主题';
    } else if (currentGroup === null){
      els = buildGroupNodes();
      mode = '组级';
    } else {
      els = buildGroupDrill(currentGroup);
      mode = currentGroup + ' · ' + (groupById[currentGroup] ? groupById[currentGroup].name : '');
    }
    cy.elements().remove();
    cy.add(els.nodes);
    cy.add(els.edges);
    applyViewStyles();
    $('zcount').textContent = cy.nodes().length;
    $('zmode').textContent = mode;
    cy.layout({ name:'dagre', rankDir:'LR', nodeSep:40, rankSep:70, padding:40 }).run();
    if (doFit) cy.fit(undefined, 50);
    updateCrumb();
  }

  function applyViewStyles(){
    cy.nodes().forEach(n => {
      const d = n.data();
      let bw = 1, bc = 'rgba(255,255,255,0.35)', op = 1;
      if (d.kind === 'group') bw = 3;
      if (bridgeMode){
        if (d.kind === 'node' && !isBridge(d.id)) op = 0.08;
        if (d.kind === 'group') op = 0.15;
      }
      n.style('border-width', bw);
      n.style('border-color', bc);
      n.style('opacity', op);
    });
  }

  // ===== 视图切换 =====
  function toggleBridge(){
    bridgeMode = !bridgeMode;
    currentGroup = null;
    $('bridgebtn').classList.toggle('on', bridgeMode);
    render();
  }
  $('bridgebtn').addEventListener('click', toggleBridge);

  function goBack(){
    if (currentGroup !== null){
      currentGroup = null;
      render();
    }
  }
  $('backbtn').addEventListener('click', goBack);

  // ===== cytoscape =====
  const cy = cytoscape({
    container: document.getElementById('graph'),
    elements: [],
    style: [
      { selector:'node', style:{
        label:'data(label)', 'text-valign':'center','text-halign':'center', color:'#fff',
        'font-size':9, 'text-wrap':'wrap', 'text-max-width':90
      }},
      { selector:'node[kind="group"]', style:{
        'background-color': function(ele){ return DATA.groupColor[ele.data('group')] || '#243040'; },
        'border-width':3,'border-color':'rgba(255,255,255,0.5)','width':130,'height':46,'font-size':12,
        'text-wrap':'wrap','text-max-width':116
      }},
      { selector:'node[kind="node"]', style:{
        'background-color': function(ele){ return DATA.groupColor[ele.data('group')] || '#2b3550'; },
        'border-width':1,'border-color':'rgba(255,255,255,0.35)','width':58,'height':30, shape:'round-rectangle'
      }},
      { selector:'node[kind="node"][mode="stub"]', style:{
        'background-color':'#2a2e38','border-width':1,'border-color':'#555a66',
        'width':52,'height':26, opacity:0.55, 'font-size':8
      }},
      { selector:'edge', style:{
        'curve-style':'bezier','target-arrow-shape':'triangle','arrow-scale':0.7,
        'line-color': function(ele){ return EDGE_COLOR[ele.data('type')] || '#4a5265'; },
        'target-arrow-color': function(ele){ return EDGE_COLOR[ele.data('type')] || '#4a5265'; },
        'width':1.3
      }},
      { selector:'edge[type="prerequisite"]', style:{ 'width':2.0 } },
      { selector:'edge[type="variant"]', style:{ 'line-style':'dashed' } },
      { selector:'edge[type="cooccurrence"]', style:{ 'line-style':'dotted' } }
    ],
    layout: { name:'dagre', rankDir:'LR', nodeSep:40, rankSep:70, padding:40 },
    wheelSensitivity: 0.3,
    minZoom: 0.05,
    maxZoom: 5,
  });
  window.__cy = cy;

  // ===== 交互 =====
  cy.on('tap', 'node', (evt) => {
    const d = evt.target.data();
    if (currentGroup === null){
      if (d.kind === 'group'){
        currentGroup = d.group;
        render();
      }
    } else {
      if (d.kind === 'node'){
        window.location.href = '../02-node-pages/' + d.id + '.html';
      }
    }
  });

  // ===== hash 路由 =====
  function handleHash(){
    const h = location.hash.replace(/^#/,'');
    if (!h) return;
    if (groupById[h]){
      currentGroup = h;
      bridgeMode = false;
      $('bridgebtn').classList.remove('on');
      render();
    } else if (nodeById[h]){
      const g = nodeToGroup[h];
      if (g){
        currentGroup = g;
        bridgeMode = false;
        $('bridgebtn').classList.remove('on');
        render();
        const el = cy.$('#'+CSS.escape(h));
        if (el.length){
          cy.animate({ fit:{ eles: el, padding: 120 }, duration: 500 });
          el.style('border-width', 4); el.style('border-color', '#ffd700');
        }
      }
    }
  }
  window.addEventListener('hashchange', handleHash);

  // ===== crumb 更新 =====
  function updateCrumb(){
    if (currentGroup !== null && !bridgeMode){
      const g = groupById[currentGroup];
      crumb.style.display = 'inline-flex';
      $('backbtn').style.display = 'inline-block';
      crumb.innerHTML = '<b>'+currentGroup+'</b> '+escapeHtml(g ? g.name : '')+' <span style="color:var(--dim)">· '+ (g ? g.node_ids.length : 0) +' 节点</span>';
    } else {
      crumb.style.display = 'none';
      $('backbtn').style.display = 'none';
    }
  }
  function escapeHtml(s){ return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }

  // ===== 图例 =====
  function buildLegend(){
    const lg = $('legend');
    let html = '<b>组节点</b>（'+DATA.groups.length+' 组，彩色，点击下钻）<br>';
    html += '<b>知识节点</b>（'+DATA.nodes.length+' 个，点击跳转节点页）<br>';
    html += '<b>边类型</b>：<br>';
    Object.keys(EDGE_COLOR).forEach(t => {
      html += '<span class="sw" style="background:'+EDGE_COLOR[t]+'"></span>'+EDGE_LABEL[t]+'<br>';
    });
    html += '<b>阶段</b>：';
    STAGE_ORDER.forEach(s => { html += '<span class="sw" style="background:'+STAGE_COLOR[s]+'"></span>'+STAGE_LABEL[s]+' '; });
    html += '<br><b>桥接模式</b>：仅显示 10 个桥接主题及其连接边';
    lg.innerHTML = html;
  }

  // ===== 组配色图例 =====
  const gl = $('glegend');
  DATA.groups.forEach(g => {
    const d = document.createElement('div');
    d.className = 'row';
    d.dataset.gid = g.id;
    const sw = document.createElement('span');
    sw.className = 'sw';
    sw.style.background = DATA.groupColor[g.id];
    const txt = document.createElement('span');
    txt.textContent = g.name + ' (' + g.id + ')';
    d.appendChild(sw);
    d.appendChild(txt);
    d.addEventListener('click', () => {
      currentGroup = g.id;
      bridgeMode = false;
      $('bridgebtn').classList.remove('on');
      render();
    });
    gl.appendChild(d);
  });

  // ===== 初始渲染 =====
  buildLegend();
  render();
  handleHash();
})();
"""


def ensure_vendor():
    os.makedirs(VENDOR_DIR, exist_ok=True)
    local1 = os.path.join(VENDOR_DIR, 'cytoscape.min.js')
    local2 = os.path.join(VENDOR_DIR, 'cytoscape-dagre.min.js')
    if os.path.exists(local1) and os.path.exists(local2):
        # 库内已自带 vendor 资产（自包含优先，符合依赖显式化）
        return
    # 回退：从 0820 参考库复制（仅首次搭建时使用）
    src = os.path.join(SRC_VENDOR_ABS, 'cytoscape.min.js')
    src2 = os.path.join(SRC_VENDOR_ABS, 'cytoscape-dagre.min.js')
    if not os.path.exists(src) or not os.path.exists(src2):
        raise FileNotFoundError('vendor 文件缺失，且参考库也不存在: %s' % SRC_VENDOR_ABS)
    shutil.copy2(src, local1)
    shutil.copy2(src2, local2)


def main():
    os.makedirs(INTER_DIR, exist_ok=True)
    ensure_vendor()
    dag, content, by_id, c_by_id, group_by_id = load_all()
    data = build_data(dag, content)
    data_json = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    js = JS.replace('__DATA__', data_json)
    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Open Code Review 图谱 · 交互式 DAG 总览</title>
<style>
{css}
</style>
</head>
<body>
<header>
  <h1>Open Code Review 图谱 <span class="badge">交互 DAG</span></h1>
  <a href="../index.html">← 根入口</a>
  <a href="../03-groups/index.html">组目录</a>
  <span id="crumb"></span>
  <button id="backbtn" class="btn" style="display:none;">← 返回组级</button>
  <div class="controls">
    <button id="bridgebtn" class="btn">桥接高亮</button>
  </div>
</header>
<div id="empty"></div>
<div id="graph"></div>
<div id="crumb"></div>
<div id="side">
  <h2>图例</h2>
  <div class="legend" id="legend"></div>
  <h2 style="margin-top:12px;">组配色</h2>
  <div id="glegend"></div>
</div>
<div id="zoominfo">模式 <b id="zmode">组级</b> · 节点 <b id="zcount">0</b></div>

<script src="vendor/cytoscape.min.js"></script>
<script src="vendor/cytoscape-dagre.min.js"></script>
<script>
{js}
</script>
</body>
</html>
""".format(css=CSS, js=js)
    with open(os.path.join(INTER_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html)
    print('interactive written, DATA nodes=%d edges=%d groups=%d'
          % (len(data['nodes']), len(data['edges']), len(data['groups'])))


if __name__ == '__main__':
    main()
