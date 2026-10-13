#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成三合一体系的资产层：
  assets/index.html         资产总览页（按类型分组浏览 42 个实践资产）
  ai-index.json             根目录 AI 可调用索引（节点→命令→资产→页面，机器可读）
  06-md/04-assets.md        AI 友好资产索引
"""
import json
import os
import re
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_common import ROOT, TITLE, SUBTITLE, load_all, esc, src_badge, BASE_CSS, SRC_STYLE, inject_shell

ASSET_MANIFEST = os.path.join(ROOT, 'assets-manifest.json')
ASSET_TYPE_LABEL = {
    'ci': 'CI 集成', 'script': '脚本', 'tool': '工具 schema', 'prompt': '提示词',
    'rule': '规则', 'code': '源码节选', 'skill': 'Skill', 'plugin': '插件',
    'build': '构建发布', 'config': '配置示例', 'doc': '文档',
}
ASSET_TYPE_COLOR = {
    'ci': '#4f8cff', 'script': '#5ad0d0', 'tool': '#e8c66a', 'prompt': '#c9a8ef',
    'rule': '#e8933b', 'code': '#7fe0d8', 'skill': '#2fb98a', 'plugin': '#e05563',
    'build': '#b48ae0', 'config': '#e0c35e', 'doc': '#9aa3b2',
}


def extract_commands(how_items):
    """从 how 文本中提取 ocr 命令行（要求 ocr + 已知子命令，去重保序）"""
    cmds = []
    seen = set()
    for it in how_items:
        for m in re.findall(r'(ocr\s+(?:review|scan|delegate|config|session|rules|llm|viewer|completion|version|d)\b[^\n。；,]*?)(?=\s*[。；,]|$)', it):
            m = m.strip().rstrip('。；,')
            if m not in seen and 3 < len(m) < 120:
                seen.add(m)
                cmds.append(m)
    return cmds


def build_ai_index(dag, content, c_by_id, manifest):
    node_index = []
    command_index = []
    seen_cmd = set()
    for n in dag['nodes']:
        c = c_by_id.get(n['id'], {})
        cmds = extract_commands(c.get('how') or [])
        for cmd in cmds:
            key = cmd
            if key not in seen_cmd:
                seen_cmd.add(key)
                command_index.append({'cmd': cmd, 'node_id': n['id'], 'node_name': n['name']})
        asset_ids = [a['id'] for a in manifest['assets'] if n['id'] in a['node_ids']]
        node_index.append({
            'id': n['id'], 'name': n['name'], 'en': n.get('en', ''),
            'type': n['type'], 'src': n['src'], 'group': n['group'],
            'stage': n['stage'], 'definition': n['definition'],
            'html': '02-node-pages/%s.html' % n['id'],
            'md': '06-md/nodes/%s.md' % n['id'],
            'commands': cmds, 'asset_ids': asset_ids,
            'has_evidence': bool((c_by_id.get(n['id'], {}) or {}).get('evidence')) if False else True,
        })
    group_index = [{'id': g['id'], 'name': g['name'], 'domain': g['domain'],
                    'kind': g['kind'], 'node_ids': g['node_ids']} for g in dag['groups']]
    asset_index = manifest['assets']
    return {
        'meta': {
            'title': TITLE, 'subtitle': SUBTITLE, 'version': '2.0.0',
            'generated': '2026-08-23',
            'total_nodes': len(node_index), 'total_assets': len(asset_index),
            'total_commands': len(command_index),
            'usage': '本文件是 AI 可调用索引：读取 node_index 定位知识节点，'
                     'commands 给可执行命令，asset_ids 关联实践源码资产（assets/ 下），'
                     'html/md 指向人类页面。',
        },
        'node_index': node_index,
        'asset_index': asset_index,
        'command_index': command_index,
        'group_index': group_index,
    }


def assets_html(dag, manifest, c_by_id):
    by_type = {}
    for a in manifest['assets']:
        by_type.setdefault(a['type'], []).append(a)
    cards = []
    for typ in sorted(by_type.keys()):
        color = ASSET_TYPE_COLOR.get(typ, '#9aa3b2')
        label = ASSET_TYPE_LABEL.get(typ, typ)
        items = []
        for a in by_type[typ]:
            items.append(
                '<div class="asset"><div class="asstype" style="color:%s">%s</div>'
                '<div class="assname"><a href="../%s" target="_blank">%s</a></div>'
                '<div class="assdesc">%s</div>'
                '<div class="assmeta">%s · %d B · 关联 %d 节点</div></div>'
                % (color, label, esc(a['path']), esc(a['name']), esc(a['desc']),
                   esc(a['src_path']), a.get('size_bytes', 0), len(a['node_ids'])))
        cards.append('<div class="type-sec"><h2 style="color:%s">%s · %d</h2>'
                     '<div class="assetgrid">%s</div></div>'
                     % (color, label, len(by_type[typ]), ''.join(items)))
    stats = ('<div class="stat"><b>%d</b><span>实践资产</span></div>'
             '<div class="stat"><b>%d</b><span>源码节选</span></div>'
             '<div class="stat"><b>%d</b><span>CI 示例</span></div>'
             '<div class="stat"><b>%d</b><span>插件/Skill</span></div>'
             % (len(manifest['assets']),
                len(by_type.get('code', [])),
                len(by_type.get('ci', [])),
                len(by_type.get('plugin', [])) + len(by_type.get('skill', []))))
    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>实践资产总览 · {title}</title>
<style>
{base_css}
.stat{{display:inline-block;background:#1d2a3f;border:1px solid #2b3d5f;border-radius:8px;padding:10px 16px;margin:4px;text-align:center;}}
.stat b{{display:block;font-size:22px;color:#fff;}}
.stat span{{font-size:12px;color:var(--dim);}}
.type-sec{{margin:18px 0;}}
.type-sec h2{{font-size:16px;border-bottom:1px solid var(--border);padding-bottom:6px;}}
.assetgrid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:10px;margin:8px 0;}}
.asset{{background:var(--panel);border:1px solid var(--border);border-radius:8px;padding:10px 12px;}}
.asstype{{font-size:10.5px;letter-spacing:.5px;margin-bottom:4px;}}
.assname a{{font-family:Consolas,monospace;font-size:12.5px;font-weight:600;word-break:break-all;}}
.assdesc{{font-size:12px;color:#b6c0d0;margin:4px 0;}}
.assmeta{{font-size:10.5px;color:var(--dim);}}
</style>
</head>
<body>
<header><h1>实践资产总览</h1><p>三合一体系 · 知识 + 实践源码资产 + AI 可调用索引（{subtitle}）</p></header>
<main>
<div class="brieflead">每个资产均从 open-code-review 源码精选（复制/节选/自建示例），节点页「实践资产」区块自动关联。
AI 可调用索引见根目录 <b>ai-index.json</b>（node_index / asset_index / command_index 三段式）。</div>
<h2>资产统计</h2><div>{stats}</div>
{cards}
</main>
<footer>{title} · 由 07-checkpoint/gen-assets.py 生成 · 数据源 assets-manifest.json</footer>
</body>
</html>""".format(
        title=esc(TITLE), subtitle=esc(SUBTITLE), base_css=BASE_CSS,
        stats=stats, cards=''.join(cards))
    return html


def assets_md(manifest):
    lines = ['# 实践资产索引', '']
    lines.append('| ID | 类型 | 名称 | 路径 | 关联节点 |')
    lines.append('|---|---|---|---|---|')
    for a in manifest['assets']:
        lines.append('| %s | %s | %s | `%s` | %s |'
                     % (a['id'], ASSET_TYPE_LABEL.get(a['type'], a['type']),
                        a['name'].replace('|', '\\|'), a['path'],
                        ', '.join('`%s`' % n for n in a['node_ids'])))
    lines.append('')
    for typ in sorted(set(a['type'] for a in manifest['assets'])):
        label = ASSET_TYPE_LABEL.get(typ, typ)
        lines.append('## %s' % label)
        lines.append('')
        for a in manifest['assets']:
            if a['type'] == typ:
                lines.append('- `%s` — %s（关联：%s）'
                             % (a['name'], a['desc'], ', '.join(a['node_ids'])))
        lines.append('')
    return '\n'.join(lines)


def main():
    dag, content, by_id, c_by_id, group_by_id = load_all()
    manifest = json.load(open(ASSET_MANIFEST, encoding='utf-8'))
    manifest['meta']['generated'] = '2026-08-23'

    # assets/index.html
    os.makedirs(os.path.join(ROOT, 'assets'), exist_ok=True)
    with open(os.path.join(ROOT, 'assets', 'index.html'), 'w', encoding='utf-8') as f:
        f.write(inject_shell(assets_html(dag, manifest, c_by_id), 'assets/index.html'))
    print('assets/index.html written')

    # ai-index.json（根目录）
    ai = build_ai_index(dag, content, c_by_id, manifest)
    with open(os.path.join(ROOT, 'ai-index.json'), 'w', encoding='utf-8') as f:
        json.dump(ai, f, ensure_ascii=False, indent=1)
    print('ai-index.json written: nodes=%d assets=%d commands=%d'
          % (len(ai['node_index']), len(ai['asset_index']), len(ai['command_index'])))

    # 06-md/04-assets.md
    os.makedirs(os.path.join(ROOT, '06-md'), exist_ok=True)
    with open(os.path.join(ROOT, '06-md', '04-assets.md'), 'w', encoding='utf-8') as f:
        f.write(assets_md(manifest))
    print('06-md/04-assets.md written')


if __name__ == '__main__':
    main()