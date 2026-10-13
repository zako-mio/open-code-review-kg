#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gate_responsive.py — open-code-review-kg 的**站点侧响应式门控**（批 H · 标准档新增）。

★★ 本件是**静态判据**，⛔ 不是渲染实测 —— 这是本批最重要的一条如实声明：
    本机 **无浏览器**（`agent-browser` 不在 PATH），方案 §7 判据 5（交互页 @375 图谱可视宽
    ≥300px）**无法**用渲染几何验证。⇒ 本件按 SH3 §4.2 的口径，从 `@media` 断点与
    `#side` / `#graph` 的固定宽度规则**算出「未遮挡宽」的静态下界**。
    ⛔ 该数字**不得**被读作「已实测渲染几何」；渲染几何未实测这一事实已写进
    `gate-manifest.json` 的 `not_enforced_here` 与 `not_covered`。

★ 执行强度：**report-only**（`hard_blocking` 枚举不含 responsive）。

判据（4 条）：
  R1 [blind]  空集守卫：扫描面 0 页 / 交互页样式表读不到 / 断点解析出 0 条 ⇒ FAIL
  R2 [report] 断点存在性：每页须有 ≥1 个 `@media`（零断点页＝在窄视口与桌面同版式）
  R3 [report] 宽内容兜底：`.tblwrap` 一类宽内容容器须有 `overflow-x:auto|scroll`
              （Q8-A 回登的 C3-N7 正面样板：它让 `th{white-space:nowrap}` 的撑破后果局部化）
  R4 [report] ★ 判据 5 的静态下界：交互页在 375px 下「图谱未被侧栏遮挡的宽度」的静态下界
              ≥ 300px（算法见 `static_graph_width()`；⛔ 不是渲染实测）

退出码：0 全过（report 类 FAIL 不阻断）/ 1 blind 类 FAIL / 2 输入错误 / 3 护栏拒读
"""
import argparse
import glob
import json
import os
import re
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import gate_common as GC  # noqa: E402  ★ 共用薄工具（含 css_text：从生成器源码切 CSS 文本区）
GateError = GC.GateError
load_json = GC.load_json

MEDIA_RE = re.compile(r"@media\s*([^{]+)\{", re.I)
MAXW_RE = re.compile(r"max-width\s*:\s*(\d+(?:\.\d+)?)px", re.I)
MINW_RE = re.compile(r"min-width\s*:\s*(\d+(?:\.\d+)?)px", re.I)
RULE_RE = re.compile(r"([^{}]+)\{([^{}]*)\}", re.S)
WIDTH_RE = re.compile(r"(?<![-\w])width\s*:\s*([^;{}]+)")
OVERFLOW_RE = re.compile(r"overflow-x\s*:\s*([^;{}]+)")
NARROW_PROBE = 375.0
THRESHOLD = 300.0

BLIND, REPORT = "blind", "report"


def media_blocks(text):
    """切出 (条件串, 块体) 列表（用花括号配平，⛔ 不用非贪婪正则——那会在嵌套 @media 上截断）。"""
    out = []
    for m in MEDIA_RE.finditer(text):
        i = m.end() - 1
        depth, j = 0, i
        while j < len(text):
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        out.append((m.group(1).strip(), text[i + 1:j]))
    return out


def active_widths(text, viewport):
    """算出「在 viewport 宽度下生效的 width 规则」→ {(选择器, 属性): 值}。

    ★ 简化但**保守**的口径：只认 `max-width` 条件（本站全部断点都是 max-width），
      条件里含 `min-width` 且 viewport 小于它 ⇒ 该块不生效。
    """
    order = [("", text)]           # 基础层：条件为空
    for cond, body in media_blocks(text):
        order.append((cond, body))
    eff = {}
    for cond, body in order:
        if cond:
            mw = MAXW_RE.search(cond)
            if mw and viewport > float(mw.group(1)):
                continue           # 该断点在此视口不生效
            mn = MINW_RE.search(cond)
            if mn and viewport < float(mn.group(1)):
                continue
        for rm in RULE_RE.finditer(body):
            sel = re.sub(r"\s+", " ", rm.group(1)).strip()
            if sel.startswith("@") or not sel:
                continue
            wm = WIDTH_RE.search(rm.group(2))
            if wm:
                eff[(sel, "width")] = wm.group(1).strip()
            om = OVERFLOW_RE.search(rm.group(2))
            if om:
                eff[(sel, "overflow-x")] = om.group(1).strip()
    return eff


def resolve_width(eff, selector):
    """取某选择器的 width：优先 `body.side-open #side` 之外的精确匹配，再退 `#side`。"""
    for key in ((selector, "width"),):
        if key in eff:
            return eff[key]
    return None


SIDE_SEL_RE = re.compile(r"^#side\b")
OPEN_SEL_RE = re.compile(r"^body\.side-open\s+#side\b")


def _side_rule(sel):
    """选择器是否直接作用于侧栏本体（`#side` 或 `body.side-open #side`）。

    ★ 必须排除 `#side .legend` 一类**后代**选择器：它们的 `width` 不是侧栏占宽。
    """
    if SIDE_SEL_RE.match(sel):
        return "default"
    if OPEN_SEL_RE.match(sel):
        return "open"
    return None


def _media_applies(cond, viewport):
    mw = MAXW_RE.search(cond)
    if mw and viewport > float(mw.group(1)):
        return False
    mn = MINW_RE.search(cond)
    if mn and viewport < float(mn.group(1)):
        return False
    return True


def static_graph_width(text, viewport=NARROW_PROBE):
    """★ 判据 5 的静态下界：在 viewport 宽度下「图谱未被侧栏遮挡的宽度」。

    算法（全部只读样式表文本，⛔ 不渲染）：
      1. 按层叠顺序遍历「基础层 → 各生效 @media 层」里的 `#side` / `body.side-open #side` 规则，
         取其最终 `display` 与 `width`；
      2. 默认态：`display:none` ⇒ 侧栏占宽 0；否则占宽 = width（px；无声明时取 300px 保守值）；
      3. 图谱可视宽 = viewport − 侧栏占宽（`#graph` 是 `position:fixed;left:0;right:0`，
         侧栏 `position:fixed` 覆盖其上）。
    ★ ⛔ 这是**静态推算**，不是渲染实测；渲染几何未实测这一事实已写进 gate-manifest.json。
    """
    base_rules, media_rules = [], []
    # ★ 先剥 CSS 注释：注释里常写「原断点只改宽度」一类说明，其中的 `{` 会把「选择器」切错
    #   （实测踩到：媒体块里的注释含 `#side{width:220px}` ⇒ 选择器串被截成乱码，折叠判据假阴性）。
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    # 基础层：去掉所有 @media 块后的剩余文本
    stripped = text
    for cond, body in media_blocks(text):
        stripped = stripped.replace(body, "")
        for rm in RULE_RE.finditer(body):
            media_rules.append((cond, re.sub(r"\s+", " ", rm.group(1)).strip(), rm.group(2)))
    for rm in RULE_RE.finditer(stripped):
        base_rules.append((re.sub(r"\s+", " ", rm.group(1)).strip(), rm.group(2)))

    def apply(rules):
        display, width = None, None
        for sel, body in rules:
            if _side_rule(sel) != "default":
                continue
            dm = re.search(r"display\s*:\s*([^;{}]+)", body, re.I)
            if dm:
                display = dm.group(1).strip().lower()
            wm = WIDTH_RE.search(body)
            if wm:
                width = wm.group(1).strip()
        return display, width

    default_display, default_width = apply(base_rules)
    open_display, open_width = None, None
    for cond, sel, body in media_rules:
        if not _media_applies(cond, viewport):
            continue
        kind = _side_rule(sel)
        if kind == "default":
            dm = re.search(r"display\s*:\s*([^;{}]+)", body, re.I)
            if dm:
                default_display = dm.group(1).strip().lower()
            wm = WIDTH_RE.search(body)
            if wm:
                default_width = wm.group(1).strip()
        elif kind == "open":
            dm = re.search(r"display\s*:\s*([^;{}]+)", body, re.I)
            if dm:
                open_display = dm.group(1).strip().lower()
            wm = WIDTH_RE.search(body)
            if wm:
                open_width = wm.group(1).strip()

    def px(w, fallback=300.0):
        if not w:
            return fallback
        m = re.match(r"(\d+(?:\.\d+)?)px$", w.strip())
        if m:
            return float(m.group(1))
        if w.strip() in ("0", "0px"):
            return 0.0
        return fallback

    if default_display == "none":
        side_w = 0.0
        collapsed = True
    else:
        side_w = px(default_width)
        collapsed = False
    return max(0.0, viewport - side_w), side_w, collapsed


def collect(site_root, profile, contract):
    pages = GC.read_pages(site_root, profile)
    css_sources = GC.css_sources(site_root, contract)
    return pages, css_sources


def judge(ctx):
    R = []
    pages, css_sources = ctx["pages"], ctx["css"]
    inter = ctx.get("interactive_page")
    inter_css = ctx.get("interactive_css") or ""

    def add(cid, name, ok, detail, klass):
        R.append((cid, name, bool(ok), detail, klass))

    total_media = sum(len(MEDIA_RE.findall(t)) for t in pages.values())
    # ---- R1 空集守卫
    reasons = []
    if not pages:
        reasons.append("扫描面 0 页（page_families glob 未命中任何文件）")
    if total_media == 0:
        reasons.append("全站 @media 命中 0 处（断点解析面为空）")
    if not inter or not inter_css:
        reasons.append("交互页或其样式表来源读不到（%s）" % (inter or "未声明 interactive_page"))
    add("R1", "空集守卫（页/断点/交互页样式表均非空）", not reasons,
        "；".join(reasons) if reasons else
        "扫描 %d 页 · @media 共 %d 处 · 交互页 %s · 样式表来源 %d 个文件"
        % (len(pages), total_media, inter, len(css_sources)), BLIND)

    # ---- R2 断点存在性
    zero = sorted(rel for rel, t in pages.items() if not MEDIA_RE.search(t))
    add("R2", "断点存在性（每页 ≥1 个 @media）", not zero,
        "零断点页 %d 个：%s" % (len(zero), zero[:6]) if zero else
        "全部 %d 页都有 ≥1 个 @media" % len(pages), REPORT)

    # ---- R3 宽内容兜底（判样式表文本区）
    all_css = "\n".join(GC.css_text(t) for t in css_sources.values())
    bad3 = []
    if ".tblwrap" not in all_css:
        bad3.append("样式表里没有 .tblwrap（宽表兜底容器缺失）")
    else:
        m = re.search(r"\.tblwrap\s*\{([^{}]*)\}", all_css, re.S)
        if not m or not re.search(r"overflow-x\s*:\s*(auto|scroll)", m.group(1), re.I):
            bad3.append(".tblwrap 未声明 overflow-x:auto|scroll")
    add("R3", "宽内容兜底（.tblwrap 的 overflow-x 局部滚动；Q8-A 回登的 C3-N7 样板）", not bad3,
        "；".join(bad3) if bad3 else
        "`.tblwrap{overflow-x:auto}` 在位 ⇒ `th{white-space:nowrap}` 的撑破后果被局部化（页面级溢出 0）",
        REPORT)

    # ---- R4 判据 5 的静态下界
    vis, side_w, collapsed = static_graph_width(inter_css, NARROW_PROBE)
    graph_hidden = False
    for rm in RULE_RE.finditer(inter_css):
        sel = re.sub(r"\s+", " ", rm.group(1)).strip()
        if re.match(r"^#graph\b", sel) and re.search(r"display\s*:\s*none", rm.group(2), re.I):
            graph_hidden = True
    bad4 = []
    if graph_hidden:
        bad4.append("图谱容器 #graph 被 display:none（可视宽 = 0）")
    if vis < THRESHOLD:
        bad4.append("静态下界 %.0fpx < %.0fpx（侧栏占宽 %.0fpx，折叠=%s）"
                    % (vis, THRESHOLD, side_w, collapsed))
    if not collapsed:
        bad4.append("窄视口未折叠侧栏（@media 里没有 #side{display:none}）")
    add("R4", "★ 判据 5 的**静态下界**：@%dpx 图谱可视宽 ≥%.0fpx（⛔ 非渲染实测）"
        % (int(NARROW_PROBE), THRESHOLD), not bad4,
        "；".join(bad4) if bad4 else
        "静态下界 %.0fpx（侧栏占宽 %.0fpx / 折叠=%s）≥ %.0fpx ⇒ 判据 5 在**静态口径**下成立"
        % (vis, side_w, collapsed, THRESHOLD), REPORT)
    return R


def run(site_root, profile_path):
    profile = load_json(profile_path, "profile")
    contract = load_json(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      "vendor/pipeline/values/open-code-review-kg.json"), "值件")
    pages, css = collect(site_root, profile, contract)
    inter = None
    for rel in pages:
        if rel.startswith("04-interactive/"):
            inter = rel
            break
    inter_css = ""
    if inter:
        inter_css = pages[inter]
    # ★ 判据作用域：R4 判的是「交互页本族的样式表」——⛔ 不把别族的 CSS 混进来判它。
    inter_fam = None
    for rule in profile.get("page_families") or []:
        if rule["glob"].startswith("04-interactive/"):
            inter_fam = rule["family"]
            break
    inter_src_css = "\n".join(GC.css_text(t) for t in css
                              if inter_fam and inter_fam in _fams_of(contract, t))
    if not inter_src_css:
        inter_src_css = inter_css
    return judge({"pages": pages, "css": css, "interactive_page": inter,
                  "interactive_css": inter_src_css, "interactive_family": inter_fam})


def _fams_of(contract, target_path):
    """某个生成器源码属于哪些族。"""
    out = set()
    for fam, spec in (contract.get("families") or {}).items():
        if target_path in (spec.get("targets") or []):
            out.add(fam)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--site-root", default=".")
    ap.add_argument("--profile", default=None)
    ap.add_argument("--manifest", default="gate-manifest.json")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    site_root = os.path.abspath(a.site_root)
    profile_path = a.profile or os.path.join(site_root, "build/profile.json")
    if a.manifest and not os.path.isfile(os.path.join(site_root, a.manifest)):
        print("GUARD-REJECT: 清单不存在：%s" % a.manifest)
        return 3
    try:
        R = run(site_root, profile_path)
    except GateError as exc:
        print("GUARD-REJECT: %s" % exc)
        return 3
    for cid, name, ok, detail, klass in R:
        print("[%s] %s %s（%s）— %s" % ("PASS" if ok else "FAIL", cid, name, klass, detail))
    blind = [r for r in R if r[4] == BLIND and not r[2]]
    print("\n=== 响应式门控（report-only；★ 静态判据，渲染几何未实测）：%d 项判据，%d FAIL（blind %d）==="
          % (len(R), sum(1 for r in R if not r[2]), len(blind)))
    return 1 if blind else 0


# --------------------------------------------------------------------------- selftest
GOOD_GEN = '''
BASE_CSS = """
:root{--bg:#0f1117;}
.tblwrap{overflow-x:auto;margin:8px 0;}
th{white-space:nowrap;}
@media (max-width:720px){ main{padding:14px;} }
"""
'''
GOOD_INTER = '''<!DOCTYPE html><html><head><style>
  #side { position:fixed; right:0; top:52px; bottom:0; width:300px; }
  #graph { position:fixed; top:52px; left:0; right:0; bottom:0; }
  @media (max-width:768px){
    #side { display:none; }
    body.side-open #side { display:block; }
  }
</style></head><body><div id="side"></div><div id="graph"></div></body></html>
'''
FIX_PROFILE = {"page_families": [{"glob": "pages/*.html", "family": "default"},
                                 {"glob": "04-interactive/*.html", "family": "04-interactive"}]}
FIX_CONTRACT = {"families": {"default": {"targets": ["gen.py"], "overrides": {}},
                             "04-interactive": {"targets": ["gen-interactive.py"], "overrides": {}}}}


def _tree(tmp, gen=GOOD_GEN, inter=GOOD_INTER):
    os.makedirs(os.path.join(tmp, "pages"), exist_ok=True)
    os.makedirs(os.path.join(tmp, "04-interactive"), exist_ok=True)
    open(os.path.join(tmp, "pages/p.html"), "w", encoding="utf-8").write(
        '<!DOCTYPE html><html><head><style>@media (max-width:720px){main{padding:1px}}</style></head>'
        '<body>hi</body></html>\n')
    open(os.path.join(tmp, "04-interactive/index.html"), "w", encoding="utf-8").write(inter)
    open(os.path.join(tmp, "gen.py"), "w", encoding="utf-8").write(gen)
    open(os.path.join(tmp, "gen-interactive.py"), "w", encoding="utf-8").write("CSS = '''x'''\n")
    open(os.path.join(tmp, "profile.json"), "w", encoding="utf-8").write(json.dumps(FIX_PROFILE))
    return tmp


def _judge(tmp):
    profile = load_json(os.path.join(tmp, "profile.json"), "p")
    pages, css = collect(tmp, profile, FIX_CONTRACT)
    inter = None
    for rel in pages:
        if rel.startswith("04-interactive/"):
            inter = rel
            break
    return judge({"pages": pages, "css": css, "interactive_page": inter,
                  "interactive_css": pages.get(inter, "") if inter else "",
                  "interactive_family": "04-interactive"})


def selftest():
    import shutil
    cases = []

    def case(name, cid, build, expect_fail=True, expect_pass=False):
        tmp = tempfile.mkdtemp(prefix="resp-")
        try:
            build(tmp)
            R = _judge(tmp)
            got = {r[0]: r[2] for r in R}
            ok = all(r[2] for r in R) if expect_pass else ((got.get(cid) is False) if expect_fail else bool(got.get(cid)))
            note = ""
        except Exception as exc:  # noqa: BLE001
            ok, note = False, "异常：%s" % exc
        cases.append((name, ok, note))
        shutil.rmtree(tmp, ignore_errors=True)

    case("正向夹具应 0 FAIL", None, lambda t: _tree(t), expect_pass=True)
    case("R1 负例：扫描面 0 页", "R1",
         lambda t: (_tree(t), open(os.path.join(t, "profile.json"), "w").write(
             json.dumps({"page_families": [{"glob": "nope/*.html", "family": "default"}]}))))
    case("R1 负例：全站 @media 命中 0 处（含交互页）", "R1",
         lambda t: (_tree(t, gen='BASE_CSS = """\n.tblwrap{overflow-x:auto;}\n"""\n',
                          inter='<!DOCTYPE html><html><head><style>#side{width:300px}</style></head>'
                                '<body><div id="side"></div></body></html>\n'),
                    open(os.path.join(t, "pages/p.html"), "w").write(
                        "<!DOCTYPE html><html><head><style>body{x:1}</style></head><body>hi</body></html>\n")))
    case("R2 负例：某页零断点", "R2",
         lambda t: (_tree(t, gen='BASE_CSS = """\n.tblwrap{overflow-x:auto;}\n"""\n'),
                    open(os.path.join(t, "pages/p.html"), "w").write(
                        "<!DOCTYPE html><html><head><style>body{x:1}</style></head><body>hi</body></html>\n")))
    case("R3 负例：.tblwrap 缺 overflow-x", "R3",
         lambda t: _tree(t, gen='BASE_CSS = """\n.tblwrap{margin:8px 0;}\n@media (max-width:720px){main{padding:1px}}\n"""\n'))
    case("R4 负例：窄视口不折叠侧栏（回到 155px 的旧形态）", "R4",
         lambda t: _tree(t, inter='<!DOCTYPE html><html><head><style>\n'
                                  '  #side { position:fixed; right:0; width:300px; }\n'
                                  '  @media (max-width:768px){ #side { width:220px; } }\n'
                                  '</style></head><body><div id="side"></div></body></html>\n'))
    case("★ 假阳样本：侧栏折叠了但 #graph 也被藏起来（可视宽 0）不得算通过", "R4",
         lambda t: _tree(t, inter='<!DOCTYPE html><html><head><style>\n'
                                  '  #side { width:400px; }\n'
                                  '  #graph { position:fixed; }\n'
                                  '  @media (max-width:768px){ #side { display:none; } #graph { display:none; } }\n'
                                  '</style></head><body>x</body></html>\n'))
    case("★ 假阳样本：.tblwrap 只有 overflow-x:hidden 不得算通过", "R3",
         lambda t: _tree(t, gen='BASE_CSS = """\n.tblwrap{overflow-x:hidden;}\n@media (max-width:720px){main{padding:1px}}\n"""\n'))

    ok = all(v for _, v, _ in cases)
    for name, res, note in cases:
        print("  [%s] %s%s" % ("PASS" if res else "FAIL", name, ("  ← " + note) if note else ""))
    print("\n=== gate_responsive.py 自检：%d 项，%d FAIL ===" % (len(cases), sum(1 for _, v, _ in cases if not v)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
