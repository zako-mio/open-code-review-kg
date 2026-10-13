#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gate_a11y.py — open-code-review-kg 的**站点侧无障碍门控**（批 H · 标准档新增）。

★ 执行强度：**report-only**。`site-profile.schema.json` 的 `hard_blocking` 枚举只有四项
  （token-consistency / contrast / empty-set-guard / artifact-existence），无障碍不在其中
  ⇒ 按 Q 裁定只能进 `report_only`（擅自扩枚举＝改 schema，须走独立决策）。
★ 判据定义来源：`solutions/_shared/SH2-a11y-baseline.md` §4.2（本件只实现，⛔ 不新造阈值）。

判据（5 条）：
  A1 [blind]  空集守卫：扫描面 0 页 / 未声明 main_landmark_exceptions ⇒ FAIL（⛔ 不返回「0 命中」）
  A2 [report] `<main>` 地标：每页须有恰 1 个 `<main`；无 main 的页必须逐页登记在
              `gate-manifest.json` 的 `main_landmark_exceptions`（登记面即出口，⛔ 非白名单）
  A3 [report] 登记不得过期／不得幽灵：登记的页必须真的无 main 且在扫描面内
  A4 [report] skip link：每页须有 `<a ... href="#id">` 形式的跳转链接，且 `#id` 在**同页**内存在
  A5 [report] 焦点可见与动效熔断：样式表须有 `:focus-visible` 与 `prefers-reduced-motion`
              （判**样式表来源**＝生成器源码；⛔ 不判「某页是否用到该规则」——那是 CSS 覆盖面，
              不是无障碍可达性的判据对象，混在一起会造假 FAIL）

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

MAIN_RE = re.compile(r"<main\b", re.I)
# ★ skip link 的判据对象必须与断言对象一致（SH5 §4.0 第 1 条）：
#   站内大量 `<a href="#use-ci">场景：…</a>` 一类**页内目录锚**不是 skip link —— 若只判
#   「有没有 `<a href="#id">`」，会把它们误判为已具备 skip link（实测踩到：本判据在
#   05-views/02-scenarios.html 与 03-learning-path.html 上产生**假绿**）。
#   ⇒ 判据收紧为：① 锚文本含「跳到 / 跳至 / skip」；② 该锚出现在 `<body>` 之后的前 1500 字符内
#      （skip link 的定义位置就是「内容之前」）；③ `#id` 在同页内存在。
SKIP_RE = re.compile(r"""<a\b[^>]*href\s*=\s*["']#([A-Za-z0-9_:.-]+)["'][^>]*>(.*?)</a>""",
                     re.I | re.S)
SKIP_TEXT_RE = re.compile(r"跳到|跳至|skip", re.I)
BODY_RE = re.compile(r"<body\b[^>]*>", re.I)
SKIP_WINDOW = 1500
ID_RE = re.compile(r"""\bid\s*=\s*["']([A-Za-z0-9_:.-]+)["']""", re.I)

BLIND, REPORT = "blind", "report"


class GateError(Exception):
    """护栏拒读（exit 3）。"""


def load_json(path, label):
    if not os.path.isfile(path):
        raise GateError("%s 不存在：%s" % (label, path))
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception as exc:  # noqa: BLE001
        raise GateError("%s 非法 JSON：%s" % (label, exc))


def collect(site_root, profile, contract):
    pages = GC.read_pages(site_root, profile)
    css_sources = GC.css_sources(site_root, contract)
    return pages, css_sources


def judge(ctx):
    R = []
    pages, css_sources = ctx["pages"], ctx["css"]
    manifest = ctx["manifest"]

    def add(cid, name, ok, detail, klass):
        R.append((cid, name, bool(ok), detail, klass))

    # ---- A1 空集守卫
    reasons = []
    if not pages:
        reasons.append("扫描面 0 页（page_families glob 未命中任何文件）")
    if not css_sources:
        reasons.append("样式表来源 0 个文件（无法判 A5）")
    if "main_landmark_exceptions" not in manifest:
        reasons.append("清单未声明 main_landmark_exceptions（⛔ 不静默跳过）")
    add("A1", "空集守卫（扫描面/样式表来源/登记面均非空）", not reasons,
        "；".join(reasons) if reasons else
        "页 %d 个 · 样式表来源 %d 个文件" % (len(pages), len(css_sources)), BLIND)

    no_main = sorted(rel for rel, t in pages.items() if not MAIN_RE.search(t))
    ex = manifest.get("main_landmark_exceptions") or []
    ex_pages = {e.get("page") for e in ex if isinstance(e, dict)}

    # ---- A2 `<main>` 地标
    unreg = [r for r in no_main if r not in ex_pages]
    add("A2", "`<main>` 地标（无 main 的页必须逐页登记）", not unreg,
        "无 main 且未登记的页 %d 个：%s" % (len(unreg), unreg[:6]) if unreg else
        "有 main 的页 %d / 无 main 的页 %d（全部已登记：%s）"
        % (len(pages) - len(no_main), len(no_main), sorted(ex_pages) or "无"), REPORT)

    # ---- A3 登记不得过期／不得幽灵
    bad3 = []
    for p in sorted(ex_pages):
        if p not in pages:
            bad3.append("幽灵登记（扫描面里没有这一页）：%s" % p)
        elif p not in no_main:
            bad3.append("登记过期（该页其实有 <main>）：%s" % p)
    add("A3", "登记不得过期／不得幽灵", not bad3,
        "；".join(bad3[:4]) if bad3 else "登记 %d 项全部为真「无 main」且在扫描面内" % len(ex_pages), REPORT)

    # ---- A4 skip link
    bad4 = []
    for rel, t in sorted(pages.items()):
        ids = set(ID_RE.findall(t))
        bm = BODY_RE.search(t)
        head = t[bm.end():bm.end() + SKIP_WINDOW] if bm else t[:SKIP_WINDOW]
        ok_skip = False
        for m in SKIP_RE.finditer(head):
            if m.group(1) in ids and SKIP_TEXT_RE.search(m.group(2) or ""):
                ok_skip = True
                break
        if not ok_skip:
            bad4.append(rel)
    add("A4", "skip link（锚文本含「跳到/skip」＋ 位于 <body> 后 %d 字符内 ＋ #id 在同页存在）"
        % SKIP_WINDOW, not bad4,
        "缺 skip link 的页 %d 个：%s" % (len(bad4), bad4[:6]) if bad4 else
        "全部 %d 页都有合格的 skip link" % len(pages), REPORT)

    # ---- A5 焦点可见与动效熔断（判**样式表文本区**，⛔ 不判整份生成器源码——那会把 JS 里的字样当样式）
    all_css = "\n".join(GC.css_text(t) for t in css_sources.values())
    bad5 = []
    if ":focus-visible" not in all_css and ":focus" not in all_css:
        bad5.append("样式表里没有 :focus-visible / :focus 规则（键盘焦点不可见）")
    if "prefers-reduced-motion" not in all_css:
        bad5.append("样式表里没有 prefers-reduced-motion 熔断")
    add("A5", "焦点可见与动效熔断（判样式表来源）", not bad5,
        "；".join(bad5) if bad5 else "样式表含 :focus-visible 与 prefers-reduced-motion", REPORT)

    return R


def run(site_root, profile_path, manifest_path):
    profile = load_json(profile_path, "profile")
    manifest = load_json(manifest_path, "门控清单")
    contract = load_json(os.path.join(HERE, "vendor/pipeline/values/open-code-review-kg.json"), "值件")
    pages, css = collect(site_root, profile, contract)
    return judge({"pages": pages, "css": css, "manifest": manifest})


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
    manifest_path = a.manifest if os.path.isabs(a.manifest or "") else os.path.join(site_root, a.manifest)
    try:
        R = run(site_root, profile_path, manifest_path)
    except GateError as exc:
        print("GUARD-REJECT: %s" % exc)
        return 3
    for cid, name, ok, detail, klass in R:
        print("[%s] %s %s（%s）— %s" % ("PASS" if ok else "FAIL", cid, name, klass, detail))
    blind = [r for r in R if r[4] == BLIND and not r[2]]
    print("\n=== 无障碍门控：%d 项判据，%d FAIL（blind %d）==="
          % (len(R), sum(1 for r in R if not r[2]), len(blind)))
    return 1 if blind else 0


# --------------------------------------------------------------------------- selftest
GOOD_PAGE = ('<!DOCTYPE html><html lang="zh-CN"><head><title>t</title></head><body>'
             '<a class="skip" href="#main">跳到主要内容</a>'
             '<main id="main">hi</main></body></html>\n')
GOOD_CSS = "BASE_CSS = '''\n:focus-visible{outline:2px solid #4f8cff;}\n" \
           "@media (prefers-reduced-motion:reduce){*{animation:none}}\n'''\n"
FIX_PROFILE = {"page_families": [{"glob": "pages/*.html", "family": "default"}]}
FIX_CONTRACT = {"families": {"default": {"targets": ["gen.py"], "overrides": {}}}}


def _tree(tmp, page=GOOD_PAGE, css=GOOD_CSS, manifest=None):
    os.makedirs(os.path.join(tmp, "pages"), exist_ok=True)
    open(os.path.join(tmp, "pages/p.html"), "w", encoding="utf-8").write(page)
    open(os.path.join(tmp, "gen.py"), "w", encoding="utf-8").write(css)
    open(os.path.join(tmp, "profile.json"), "w", encoding="utf-8").write(json.dumps(FIX_PROFILE))
    open(os.path.join(tmp, "manifest.json"), "w", encoding="utf-8").write(
        json.dumps(manifest if manifest is not None else {"main_landmark_exceptions": []}))
    return tmp


def _judge(tmp):
    profile = load_json(os.path.join(tmp, "profile.json"), "p")
    manifest = load_json(os.path.join(tmp, "manifest.json"), "m")
    pages, css = collect(tmp, profile, FIX_CONTRACT)
    return judge({"pages": pages, "css": css, "manifest": manifest})


def selftest():
    import shutil
    cases = []

    def case(name, cid, build, expect_fail=True, expect_pass=False):
        tmp = tempfile.mkdtemp(prefix="a11y-")
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
    case("A1 负例：扫描面 0 页", "A1",
         lambda t: (_tree(t), open(os.path.join(t, "profile.json"), "w").write(
             json.dumps({"page_families": [{"glob": "nope/*.html", "family": "default"}]}))))
    case("A1 负例：清单未声明 main_landmark_exceptions", "A1",
         lambda t: _tree(t, manifest={}))
    case("A2 负例：某页无 <main> 且未登记", "A2",
         lambda t: _tree(t, page=GOOD_PAGE.replace("<main id=\"main\">hi</main>", "<div>hi</div>")))
    case("A2 正向：无 main 但已登记 ⇒ 0 FAIL", None,
         lambda t: _tree(t, page=GOOD_PAGE.replace('<main id="main">hi</main>', '<div id="main">hi</div>'),
                         manifest={"main_landmark_exceptions": [{"page": "pages/p.html", "reason": "夹具"}]}),
         expect_pass=True)
    case("A3 负例：登记过期（该页其实有 main）", "A3",
         lambda t: _tree(t, manifest={"main_landmark_exceptions": [{"page": "pages/p.html", "reason": "夹具"}]}))
    case("A3 负例：幽灵登记", "A3",
         lambda t: _tree(t, manifest={"main_landmark_exceptions": [{"page": "ghost.html", "reason": "夹具"}]}))
    case("A4 负例：缺 skip link", "A4",
         lambda t: _tree(t, page=GOOD_PAGE.replace('<a class="skip" href="#main">跳到主要内容</a>', "")))
    case("★ 假阳样本：skip link 指向**不存在**的 id 不得算通过", "A4",
         lambda t: _tree(t, page=GOOD_PAGE.replace('href="#main"', 'href="#nope"')))
    case("★ 假阳样本：页内目录锚（href=\"#id\" 但锚文本不是「跳到/skip」）不得算 skip link", "A4",
         lambda t: _tree(t, page=GOOD_PAGE.replace(
             '<a class="skip" href="#main">跳到主要内容</a>',
             '<a href="#main">场景：接入 CI 流水线</a>')))
    case("A5 负例：样式表无 :focus-visible", "A5",
         lambda t: _tree(t, css="BASE_CSS = '''\nbody{color:#000}\n@media (prefers-reduced-motion:reduce){*{animation:none}}\n'''\n"))
    case("A5 负例：样式表无 prefers-reduced-motion", "A5",
         lambda t: _tree(t, css="BASE_CSS = '''\n:focus-visible{outline:2px solid #4f8cff;}\n'''\n"))

    ok = all(v for _, v, _ in cases)
    for name, res, note in cases:
        print("  [%s] %s%s" % ("PASS" if res else "FAIL", name, ("  ← " + note) if note else ""))
    print("\n=== gate_a11y.py 自检：%d 项，%d FAIL ===" % (len(cases), sum(1 for _, v, _ in cases if not v)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
