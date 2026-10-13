#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成根入口：index.html（统计 + 导航 + 快速开始）+ 404.html（结构化 404 页）
——OpenCodeReview 图谱版

★ 批 H（标准档）两处改动：
  1. **C3-N1 死链修复（Q1-A）**：原 `href="open-code-review/"` 指向仓内不存在的目录
     （`.gitignore:4` 排除、191 blob 0 命中）⇒ 线上 HTTP 404。现改指**站内已存在**的
     `assets/index.html`，并在卡片文案里如实说明「完整源码 clone 不在仓内」。
  2. **新增 404.html（Q1-A）**：GitHub Pages 约定落点＝仓根 `404.html`。它与 index.html
     共用同一份 `BASE_CSS`（= 从 gen_common 单一来源取令牌块）⇒ 与本站深色视觉同源，
     替代 GitHub Pages 的英文白页兜底。
  3. **门控随生成器收尾内联调用（Q6-A）**：本文件是 7 条生成配方的**最后一条**，
     故在收尾处依次调用 4 道站点门控并写 `gate-report.json`（确定性件，含 tree_digest）。
"""
import json
import os
import re
import subprocess
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_common import ROOT, TITLE, SUBTITLE, load_all, esc, src_badge, BASE_CSS, SRC_STYLE, inject_shell

OUT = os.path.join(ROOT, 'index.html')
OUT_404 = os.path.join(ROOT, '404.html')

# ★ 单源不变量：令牌块**只能**来自 gen_common.BASE_CSS（本文件⛔ 不持任何令牌字面值）。
#   该不变量由站点侧 gate_tokens.py 的 G8 实测（含 subprocess 真导入 + 剥注释的字面值扫描）。
#   ★ 注意：BASE_CSS 的**首个非空行就是令牌块**，其后紧跟布局规则 ⇒ 直接整段用 `base_css={base_css}`
#     即可（⛔ 不要把首行单独取出再拼回余下部分：那样会拼出**两个**令牌块，实测踩到过）。
#   ★ 本文件也⛔ **不**取首行做「只读不写」的变量：那会在源码里留下令牌块的形状字样，
#     让「本文件不持令牌字面值」这条不变量在**源码文本层**上不可判。



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
        '<div class="card"><h3>源码</h3><p>完整源码 clone（alibaba/open-code-review @ 2026-08-23）<b>不在本仓内</b>（.gitignore 已排除）；仓内提供的是 42 个精选实践资产与源码节选。</p>'
        '<p><a href="assets/index.html">浏览实践资产</a></p></div>'
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
        title=esc(TITLE), subtitle=esc(SUBTITLE),
        base_css=BASE_CSS,
        stats=stats, src_desc=''.join('<span class="chip">%s</span>' % esc(x) for x in src_desc),
        quick=quick, cards=cards)
    html = inject_shell(
        html, 'index.html',
        desc='Open Code Review（阿里开源 AI 代码审查 CLI）知识图谱总入口：51 个知识节点 / 7 个'
             '分组 / 5 类视图，按任务索引命令与工具，并附 42 个实践资产与 AI 可调用索引。')
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(html)
    print('index.html:', len(html), 'bytes')

    write_404(dag, content)


# ---------------------------------------------------------------- 结构化 404 页（Q1-A）
# ★ 相对前缀：404.html 落在仓根 ⇒ 前缀为空串。站点若将来把它移到子目录，改这一处即可。
GATE_404_PREFIX = ''


def write_404(dag, content):
    """产出仓根 404.html —— GitHub Pages 的约定落点。

    ★ 为什么必须自建：GitHub Pages 的默认 404 是**英文白页**，与本站深色视觉完全不同源
      （solutions/07 §8 Q1-A 的三个前提之一）。本页与 index.html 共用同一份 BASE_CSS，
      故「深色同源」是可机检的（gate_tokens.py 的 G3 逐页对账）。
    ★ 本页由生成器产出（⛔ 不是手写静态件）⇒ 它在 build/profile.json 的 page_families 与
      targets 里都有登记，重生成可复现。
    """
    total_nodes = len(dag['nodes'])
    total_groups = len(dag['groups'])
    total_edges = len(dag['edges'])
    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>404 · 页面不存在 · {title}</title>
<style>
{base_css}
.nf{{max-width:640px;margin:8vh auto 0;background:var(--panel);border:1px solid var(--border);
     border-left:4px solid var(--warn);border-radius:10px;padding:26px 30px;}}
.nf .code{{font-size:52px;font-weight:700;color:var(--warn);line-height:1;letter-spacing:2px;}}
.nf h1{{font-size:20px;color:var(--text);margin:10px 0 6px;}}
.nf p{{font-size:14px;color:var(--dim);margin:8px 0;}}
.nf ul{{padding-left:20px;margin:10px 0;}}
.nf li{{font-size:14px;margin:5px 0;}}
.nf .back{{display:inline-block;margin-top:14px;background:var(--accent);color:#fff;
          border-radius:8px;padding:9px 20px;font-size:14px;text-decoration:none;}}
</style>
</head>
<body>
<header>
  <h1>{title}</h1>
  <p class="sub">{subtitle}</p>
</header>
<main>
  <div class="nf">
    <div class="code">404</div>
    <h1>找不到这个页面</h1>
    <p>你访问的地址在本站不存在。可能是链接过期、手输有误，或该内容从未发布过。</p>
    <p>本站是 <b>{total_nodes} 个知识点 / {total_groups} 个分组 / {total_edges} 条关系边</b>的静态知识图谱，可从这些入口重新进入：</p>
    <ul>
      <li><a href="{prefix}index.html">根入口</a>：核心统计与全部导航</li>
      <li><a href="{prefix}05-views/02-scenarios.html">使用场景索引</a>：按任务查命令与参数</li>
      <li><a href="{prefix}04-interactive/index.html">交互 DAG 总览</a>：组级视图 + 点击下钻</li>
      <li><a href="{prefix}03-groups/index.html">分组目录</a>：{total_groups} 个分组</li>
      <li><a href="{prefix}assets/index.html">实践资产总览</a>：42 个精选实践资产</li>
    </ul>
    <p><a class="back" href="{prefix}index.html">← 返回首页</a></p>
  </div>
</main>
<footer>{title} · 由 07-checkpoint/gen-index.py 生成（404 兜底页）</footer>
</body>
</html>""".format(
        title=esc(TITLE), subtitle=esc(SUBTITLE),
        base_css=BASE_CSS,
        total_nodes=total_nodes, total_groups=total_groups, total_edges=total_edges,
        prefix=GATE_404_PREFIX)
    html = inject_shell(
        html, '404.html',
        desc='404 · 页面不存在：Open Code Review 项目解析知识图谱的结构化兜底页，提供根入口、'
             '场景索引、交互 DAG、分组目录与实践资产五条重新进入路径。')
    with open(OUT_404, 'w', encoding='utf-8') as f:
        f.write(html)
    print('404.html:', len(html), 'bytes')


# ---------------------------------------------------------------- 门控收尾内联调用（Q6-A）
# ★ 批 J 更正：逐门控给**它自己认的**参数（原写法把 `--manifest` 统一传给 5 道门控，
#   而统一硬化版 `gate_a11y.py` / `gate_seo_meta.py` 的 argparse 只认 `--site-root/--profile`
#   ⇒ 未识别参数触发 exit 2 ⇒ `rc |= 2` ⇒ 生成流程被自己的门控阻断（假红）。
#   ★ 另：a11y / seo 两道门控的 `main()` **不接受 argv 形参**（内部直接 `ap.parse_args()`），
#   故一律走 subprocess 逐脚本调用 —— 与 CI / profile.gates.commands 的命令行逐字一致。
GATES = [
    ("gate_tokens.py", ["--site-root", ".", "--manifest", "gate-manifest.json"]),
    ("gate_dead_css.py", ["--site-root", ".", "--profile", "build/profile.json"]),
    ("gate_a11y.py", ["--site-root", ".", "--profile", "build/profile.json"]),
    ("gate_seo_meta.py", ["--site-root", ".", "--profile", "build/profile.json"]),
    ("gate_responsive.py", ["--site-root", ".", "--profile", "build/profile.json"]),
]


def write_sitemap_robots():
    """★ 批 J：站点级元信息产物（`sitemap.xml` ＋ `robots.txt`），写在**发布根**。

    ★ 复用仓内版本化的 `07-checkpoint/gen_sitemap_robots.py`（批 J 统一件，⛔ 不另写一份）：
      它与 `gate_seo_meta.py` 用**同一套** URL 归一化（`X/index.html` → `X/`），⛔ 不写 `<lastmod>`
      （墙钟时间戳会破坏 J6 幂等），且带空集守卫（0 页 ⇒ 拒写 ⇒ 非 0 退出 ⇒ fail-closed）。
    """
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import gen_sitemap_robots as _GSR
    import gen_common as _G
    res = _GSR.run(ROOT, _G.REPO)
    if res is None:
        print('SITEMAP-ERROR: 发布根下 0 个产物页 ⇒ 拒写（防空集假绿）')
        return 1
    print('sitemap.xml %s（%d 页）· robots.txt %s（base=%s）'
          % (res['sitemap.xml'], res['pages'], res['robots.txt'], res['base_url']))
    return 0


def run_gates():
    """在生成器收尾处依次调用 5 道站点门控，并写 gate-report.json。

    ★ 依据 SH5 §4.2「执行时机三档」的 legacy 站档：**在生成脚本收尾处内联调用**
      + `gate-report.json` 随产物入库，使「跑没跑过」有痕迹。⛔ 不新建 CI（常设排除项）。
    ★ 任一硬阻断级 FAIL ⇒ 本函数返回非 0 ⇒ 进程以非 0 退出 ⇒ 生成流程被阻断
      （⛔ 不做「先生成再报警」的假绿）。
    """
    if not os.path.isfile(os.path.join(ROOT, "gate_tokens.py")):
        print('GATE-ERROR: 仓根未找到 gate_tokens.py（门控未接入）⇒ 拒绝静默跳过')
        return 1
    rc = 0
    for name, args in GATES:
        script = os.path.join(ROOT, name)
        if not os.path.isfile(script):
            print('GATE-ERROR: 门控脚本缺失：%s ⇒ 拒绝静默跳过' % name)
            rc |= 1
            continue
        print('\n----- %s -----' % name)
        r = subprocess.run([sys.executable, script] + args, cwd=ROOT,
                           capture_output=True, text=True)
        sys.stdout.write(r.stdout or '')
        if (r.stderr or '').strip():
            sys.stderr.write(r.stderr)
        rc |= int(r.returncode)
    return rc


def write_gate_report():
    """写 gate-report.json（**确定性件**：⛔ 无墙钟时间戳、⛔ 无作者机绝对路径）。

    ★ tree_digest ＝ 仓内文件（路径 + 内容的 sha256）的聚合摘要，**排除报告自身**
      ⇒ 重跑生成器两次得到的报告逐字节相同（幂等可断言）。
    """
    import hashlib
    skip_dirs = {'.git', '__pycache__', 'vendor', 'node_modules', '07-checkpoint'}
    entries = []
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = sorted(d for d in dn if d not in skip_dirs)
        for f in sorted(fn):
            rel = os.path.relpath(os.path.join(dp, f), ROOT).replace(os.sep, '/')
            if rel == 'gate-report.json':
                continue
            with open(os.path.join(dp, f), 'rb') as fh:
                entries.append('%s  %s' % (rel, hashlib.sha256(fh.read()).hexdigest()))
    tree_digest = hashlib.sha256('\n'.join(entries).encode('utf-8')).hexdigest()
    doc = {
        "site": "open-code-review-kg",
        "generated_by": "07-checkpoint/gen-index.py（Q6-A：门控随生成器收尾内联调用；★ 批 J 更正为批 J 判据数并新增 write_sitemap_robots）",
        "deterministic": True,
        "determinism_note": "★ 本件不含墙钟时间戳、不含作者机绝对路径；tree_digest 由「仓内文件路径+内容的 sha256」聚合而成并**排除本件自身** ⇒ 同输入两次生成逐字节相同。",
        "mode": "enforce",
        "gates": [
            {"id": "tokens", "script": "gate_tokens.py", "judges": "G1–G11",
             "classes": ["blind", "hard", "hard/report"], "selftest": True, "mode": "enforce"},
            {"id": "dead-css", "script": "gate_dead_css.py", "judges": "H1–H3",
             "classes": ["blind", "report"], "selftest": True, "mode": "report_only"},
            {"id": "a11y", "script": "gate_a11y.py", "judges": "A1–A7",
             "classes": ["blind", "hard"], "selftest": True, "mode": "hard"},
            {"id": "seo-meta", "script": "gate_seo_meta.py", "judges": "S1–S11",
             "classes": ["blind", "hard", "report"], "selftest": True, "mode": "hard"},
            {"id": "responsive", "script": "gate_responsive.py", "judges": "R1–R7",
             "classes": ["blind", "hard", "report"], "selftest": True, "mode": "report_only"}
        ],
        "tree_digest": tree_digest,
        "tree_digest_scope": "仓内文件（路径 + 内容的 sha256），排除 gate-report.json 自身、.git/、__pycache__/、vendor/、node_modules/、07-checkpoint/",
        "tree_file_count": len(entries)
    }
    out = os.path.join(ROOT, 'gate-report.json')
    with open(out, 'w', encoding='utf-8') as fh:
        json.dump(doc, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write('\n')
    print('gate-report.json written: tree_digest=%s files=%d' % (tree_digest[:16], len(entries)))
    return 0


if __name__ == '__main__':
    main()
    # ★ 顺序是硬约束：先落 sitemap/robots（gate_seo_meta 的 S8 要判它存在），
    #   再跑门控（fail-closed：任一非 0 ⇒ 进程非 0 ⇒ 生成流程被阻断），最后写确定性报告。
    sys.exit(write_sitemap_robots() | run_gates() | write_gate_report())
