import json, sys, os
sys.stdout.reconfigure(encoding='utf-8')
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)

dag = json.load(open('01-dag-data/opencodereview-dag.json', encoding='utf-8'))
content = json.load(open('01-dag-data/node-content.json', encoding='utf-8'))
nodes = {n['id']: n for n in dag['nodes']}
groups = dag['groups']
edges = dag['edges']
content_by_id = {n['id']: n for n in content['nodes']}

os.makedirs('06-md/nodes', exist_ok=True)

STAGE_LABEL = {'basic': '基础 basic', 'intermediate': '进阶 intermediate', 'advanced': '高级 advanced'}
TYPE_LABEL = {'principle': '方法机制', 'tool': '工具', 'crosscut': '工程保障', 'scenario': '场景索引'}
SRC_LABEL = {'core': '核心架构', 'engine': '审查引擎', 'cli': '命令行', 'config': '配置模型', 'integration': '集成生态', 'quality': '工程保障', 'scenario': '使用场景'}
EDGE_LABEL = {'prerequisite': '前置依赖', 'variant': '变体', 'combination': '组合', 'cooccurrence': '共现', 'dependency': '依赖关联'}
group_by_id = {g['id']: g for g in groups}
node_group = {n['id']: n['group'] for n in dag['nodes']}

def esc(t):
    return t.replace('|', '\\|').replace('\n', ' ')

# ---------- nodes/*.md ----------
for nid, node in nodes.items():
    c = content_by_id.get(nid, {})
    gid = node['group']
    gname = group_by_id.get(gid, {}).get('name', gid)
    lines = []
    lines.append(f"# {node['name']} ({node['en']})")
    lines.append('')
    lines.append(f"- ID: `{nid}`")
    lines.append(f"- 类型: {TYPE_LABEL.get(node['type'], node['type'])}")
    lines.append(f"- 来源: {SRC_LABEL.get(node['src'], node['src'])}")
    lines.append(f"- 分组: {gid} · {gname}")
    lines.append(f"- 阶段: {STAGE_LABEL.get(node['stage'], node['stage'])}")
    lines.append('')
    lines.append(f"> {node['definition']}")
    lines.append('')
    def sec(title, items):
        lines.append(f"## {title}")
        lines.append('')
        for it in items:
            lines.append(f"- {esc(it)}")
        lines.append('')
    if c.get('what'): sec('核心主张 (what)', c['what'])
    if c.get('why'): sec('为什么 (why)', c['why'])
    if c.get('how'): sec('如何实践 (how)', c['how'])
    if c.get('cases'): sec('案例 (cases)', c['cases'])
    if c.get('anti_patterns'): sec('反模式/易错点', c['anti_patterns'])
    if node['type'] == 'bridge' and c.get('app_side'):
        lines.append("## 三栏对比")
        lines.append('')
        lines.append("| App 侧做法 | Agent 侧做法 | 差异根源 |")
        lines.append("|---|---|---|")
        a, b, df = c.get('app_side', []), c.get('agent_side', []), c.get('difference', [])
        for i in range(max(len(a), len(b), len(df))):
            aa = a[i] if i < len(a) else ''
            bb = b[i] if i < len(b) else ''
            dd = df[i] if i < len(df) else ''
            lines.append(f"| {esc(aa)} | {esc(bb)} | {esc(dd)} |")
        lines.append('')
    # 相关边
    rel = [e for e in edges if e['from'] == nid or e['to'] == nid]
    if rel:
        lines.append("## 相关关系")
        lines.append('')
        lines.append("| 方向 | 类型 | 关系 |")
        lines.append("|---|---|---|")
        for e in rel:
            direction = f"{e['from']} → {e['to']}"
            lines.append(f"| {direction} | {EDGE_LABEL.get(e['type'], e['type'])} | {esc(e.get('label', ''))} |")
        lines.append('')
    with open(f'06-md/nodes/{nid}.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

# ---------- 00-index.md ----------
lines = ['# Open Code Review 项目解析知识图谱 · AI 友好索引', '']
lines.append(f"版本 {dag['meta']['version']} | {dag['meta']['total_nodes']} 节点 | {dag['meta']['total_edges']} 边 | {dag['meta']['total_groups']} 组")
lines.append('')
lines.append('## 节点总表')
lines.append('')
lines.append('| ID | 名称 | 类型 | 来源 | 阶段 | 分组 | 定义 |')
lines.append('|---|---|---|---|---|---|---|')
for n in dag['nodes']:
    gid = n['group']
    gname = group_by_id.get(gid, {}).get('name', gid)
    lines.append(f"| {n['id']} | {esc(n['name'])} | {TYPE_LABEL.get(n['type'], n['type'])} | {SRC_LABEL.get(n['src'], n['src'])} | {STAGE_LABEL.get(n['stage'], n['stage'])} | {gid} | {esc(n['definition'])} |")
lines.append('')
with open('06-md/00-index.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

# ---------- 01-groups.md ----------
lines = ['# 分组索引', '']
lines.append('| 分组 ID | 名称 | 类别 | 域 | 节点数 |')
lines.append('|---|---|---|---|---|')
for g in groups:
    kind_label = {'source': '架构/机制组', 'tool': '工具组', 'crosscut': '保障组', 'scenario': '场景索引组'}.get(g['kind'], g['kind'])
    lines.append(f"| {g['id']} | {esc(g['name'])} | {kind_label} | {esc(g['domain'])} | {len(g['node_ids'])} |")
lines.append('')
for g in groups:
    lines.append(f"## {g['id']} {g['name']}")
    lines.append('')
    for nid in g['node_ids']:
        n = nodes.get(nid)
        if n:
            lines.append(f"- [{nid}] {n['name']} — {n['definition']}")
    lines.append('')
with open('06-md/01-groups.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

# ---------- 02-stage.md ----------
lines = ['# 阶段视图', '']
for stage in ['basic', 'intermediate', 'advanced']:
    lines.append(f"## {STAGE_LABEL[stage]}")
    lines.append('')
    for n in dag['nodes']:
        if n['stage'] == stage:
            lines.append(f"- [{n['id']}] {n['name']} ({TYPE_LABEL.get(n['type'], n['type'])})")
    lines.append('')
with open('06-md/02-stage.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

# ---------- 03-learning-path.md ----------
def topo(nodes, edges):
    # 排序稳定版拓扑排序：入度 0 节点与邻接表均按字典序，保证跨环境可复现
    from collections import defaultdict, deque
    ids = {n['id'] for n in nodes}
    indeg = defaultdict(int); adj = defaultdict(list)
    for e in edges:
        if e['type'] != 'prerequisite': continue
        if e['from'] in ids and e['to'] in ids:
            adj[e['from']].append(e['to']); indeg[e['to']] += 1
    for u in adj:
        adj[u].sort()
    q = deque(sorted(n for n in ids if indeg[n] == 0)); order = []
    while q:
        u = q.popleft(); order.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return order

cli_nodes = [n for n in dag['nodes'] if n['src'] == 'cli']
order_cli = topo(cli_nodes, edges)
order_all = topo(dag['nodes'], edges)

lines = ['# 学习路径（自动生成，基于 prerequisite 拓扑序）', '']
lines.append('## 路径 A：命令行上手（CLI 工具）')
lines.append('')
for i, nid in enumerate(order_cli, 1):
    n = nodes[nid]
    lines.append(f"{i}. [{nid}] {n['name']}")
lines.append('')
lines.append('## 路径 B：从入门到精通（全图谱拓扑序）')
lines.append('')
for i, nid in enumerate(order_all, 1):
    n = nodes[nid]
    lines.append(f"{i}. [{nid}] {n['name']} ({TYPE_LABEL.get(n['type'], n['type'])})")
lines.append('')
with open('06-md/03-learning-path.md', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))


# ---------- 05-principles.md ----------
try:
    import json as _json
    _p = _json.load(open('01-dag-data/principles-mapping.json', encoding='utf-8'))
    _lines = ['# 12 Factor 原则 × Open Code Review 对照审查', '']
    _lines.append('> 审查标尺：12 Factor App + 12 Factor Agent 合并图谱的 24 条原则（来源：0823-12factor-methodology）。')
    _lines.append('')
    for _sysname, _items in (('## 12 Factor App 原则', _p['app_principles']), ('## 12 Factor Agent 原则', _p['agent_principles'])):
        _lines.append(_sysname)
        _lines.append('')
        _lines.append('| 原则 | 主张 | OCR 对应机制 | 结论 |')
        _lines.append('|---|---|---|---|')
        for _it in _items:
            _lines.append('| %s | %s | %s | **%s** |' % (_it['id'], _it['claim'].replace('|', '\|'), _it['ocr_mechanism'].replace('|', '\|'), _it['verdict']))
        _lines.append('')
    with open('06-md/05-principles.md', 'w', encoding='utf-8') as _f:
        _f.write('\n'.join(_lines))
    print('06-md/05-principles.md written')
except Exception as e:
    print('principles md skipped:', e)

print('06-md generated: nodes=%d index/groups/stage/learning-path done' % len(nodes))
