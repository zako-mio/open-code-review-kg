#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gate_dead_css.py — open-code-review-kg 的**站点侧死 CSS 门控**（批 H · 标准档新增）。

判据对象与断言对象（SH5 §4.0 第 1 条）：
    判据对象 ＝ 站内 `.html` 产物里真实出现的 **class 名集合**（含 `class="…"` 属性与
               JS 里 `className='…'` / `classList.toggle('…')` 一类字符串字面量）；
    断言对象 ＝ 样式表里 `.xxx` 形式的选择器类名集合。
    ⛔ 二者必须一致才是同一对象——本门控只比 **class 名**，不把标签选择器（`table`/`th`）
      或 id 选择器（`#side`）混进来判「死」（那会造出成批假阳）。

★ 为什么本判据是 report-only：`site-profile.schema.json` 的 `hard_blocking` 枚举只有四项
  （token-consistency / contrast / empty-set-guard / artifact-existence），死 CSS 不在其中
  ⇒ 按 Q 裁定「其余类只能进 report_only」，擅自扩枚举＝改 schema（须走独立决策）。

判据（3 条）：
  H1 [blind] 空集守卫：扫描面 0 页 / 0 个 class 属性 / 0 个选择器类名 ⇒ FAIL（⛔ 不返回「0 命中」）
  H2 [report] 零引用选择器：每个选择器类名必须在产物里**至少命中一次**；
              未命中的选择器必须逐条出现在 `gate-manifest.json` 的 `registered_orphan_selectors`
              里（登记面即本判据的豁免**出口**，⛔ 不是白名单——登记项同样要过 H3 的反向断言）
  H3 [report] 登记不得过期／不得幽灵：登记的选择器必须**真的**零命中（有过期即 FAIL），
              且登记项必须真的存在于样式表（幽灵登记即 FAIL）

★ 本站实测（批 H）：唯一零引用选择器是 `.navseq .spacer`（`gen_common.py` 的
  `.navseq .spacer{flex:1;min-width:60px;}`）。按 **Q8-A 裁定登记保留、⛔ 不删除**——
  它是「审计点名的死 CSS 多数为误报、真死的是另一个」这一教训的**实证样本**。

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
import gate_common as _GC  # noqa: E402  ★ 共用薄工具（取页面 / 取样式表来源 / 切 CSS 区）
SKIP_DIRS = {".git", "__pycache__", "vendor", "node_modules", "07-checkpoint", "08-source", "05-source"}

# class 来源：① 静态 class 属性；② JS 里的字符串字面量赋值（className / classList / dataset 等）
CLASS_ATTR_RE = re.compile(r"""class\s*=\s*["']([^"']*)["']""", re.I)
CLASS_JS_RE = re.compile(r"""(?:className|classList\.(?:add|remove|toggle|contains))\s*[=(]\s*["']([^"']+)["']""")
CLASS_JS_MULTI_RE = re.compile(r"""className\s*=\s*["']([^"']+)["']""")
# 样式表里的类选择器：`.name`（允许转义与连字符）
SEL_CLASS_RE = re.compile(r"\.(-?[A-Za-z_][A-Za-z0-9_-]*)")
# 规则块：`selector{...}`（足够用：本站样式表无嵌套 @ 规则里的选择器）
RULE_RE = re.compile(r"([^{}]+)\{", re.S)
# ★ 选择器字面量守卫（SH5 §4.0 第 1、2 条）：候选串必须**整段**只由选择器合法字符组成，
#   且必须含 `.` 或 `#`（本门控的判据对象**只有类选择器**）。
#   ★ 为什么需要它：样式表来源是 **Python 源码**（生成器里的 CSS 常量），其中还夹着大量 JS 代码。
#     不加守卫时，`RULE_RE` 会把 JS 里 `{` 之前的那段文本当成选择器 —— 实测踩到：
#     `$('backbtn').addEventListener('click'` / `'advanced').index(s)) groups.append(` /
#     `BASE_CSS = ''' .a` 三类假选择器被抽出，进而把 `backbtn` 一类**JS 里的 id**误当 class 判死。
SELECTOR_OK_RE = re.compile(r"^[A-Za-z0-9_.#:\[\]()=~^|$*,'\"\s>+-]+$")
# 明显是 JS/Python 代码的痕迹（命中即不是选择器）
CODE_TRACE_RE = re.compile(
    r"[{};]|=>|\(\)|\$\("          # 花括号/分号/箭头函数/立即调用
    r"|\.\s*[A-Za-z_][A-Za-z0-9_]*\s*\("   # `cy.animate(` / `edges.push(` 一类**方法调用**
    r"|push\(|getElementById|querySelector|addEventListener"   # JS API
    r"|:\s*[a-z_]+\(|^[a-z_]+:"    # 对象字面量的 key: value
)
IDENT_RE = re.compile(r"^-?[A-Za-z_][A-Za-z0-9_-]*$")


def _is_selector(part):
    """候选串是否像 CSS 类选择器。

    条件：① 不含换行（CSS 选择器不跨行；跨行说明它是「赋值语句 + 首个选择器」一类拼接，
    实测踩到：`BASE_CSS = \"\"\"` 与 `.d{color:blue}` 被 RULE_RE 拼成候选）；
    ② 括号只能出现在**伪类**里（`…:not(.x)` / `…:nth-child(n)`）——
       ⛔ 排除 `cy.animate(` / `edges.push(` 一类 JS 调用（实测踩到）；
    ③ 字符集合法；④ 不含 `=`（排除赋值）；⑤ 不含 JS/Python 代码痕迹；
    ⑥ 含 `.` 或 `#`（⛔ 不把元素选择器当成本门控的对象——那会造出成批假阳）。
    """
    if not part or "\n" in part or "=" in part:
        return False
    if re.search(r"(?<!:)\(", part):
        return False
    if not SELECTOR_OK_RE.match(part):
        return False
    if CODE_TRACE_RE.search(part):
        return False
    return bool(re.search(r"[.#]", part))

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


def pages_of(site_root, profile):
    out = []
    for rule in profile.get("page_families") or []:
        for absp in sorted(glob.glob(os.path.join(site_root, rule["glob"]), recursive=True)):
            if os.path.isfile(absp):
                out.append((os.path.relpath(absp, site_root).replace(os.sep, "/"), rule["family"]))
    return out


def classes_in(text):
    """一页里出现的全部 class 名（静态属性 + JS 字面量）——**并集**（用于 H1 的非空守卫）。"""
    out = set()
    for group in class_groups_in(text):
        out |= group
    return out


def class_groups_in(text):
    """一页里的 class 名**按来源分组**：每个 class 属性一份、每个 JS 字面量一份。

    ★ 为什么必须分组而不是取并集：组合选择器 `.b .c` 的判据是「b 与 c 是否**同属一个元素**」，
      若取并集，则 `<div class="a b">` + `<div class="c">` 会被误判为命中 ⇒ **假阳**
      （实测踩到：本判据的自检假阳样本正是这一条）。
    """
    groups = []
    for m in CLASS_ATTR_RE.finditer(text):
        groups.append(set(m.group(1).split()))
    for m in CLASS_JS_RE.finditer(text):
        groups.append(set(m.group(1).split()))
    return [g for g in groups if g]


def selectors_of(text):
    """样式表里出现的「类选择器组合」→ {归一化选择器原文: frozenset(类名)}。

    ★ 归一化：折叠空白（含换行）⇒ 选择器名可稳定用于登记与对账。
    """
    out = {}
    for m in RULE_RE.finditer(text):
        sel = m.group(1).strip()
        if sel.startswith("@") or not sel:
            continue
        for part in sel.split(","):
            part = re.sub(r"\s+", " ", part).strip()
            if not part or not _is_selector(part):
                continue
            names = frozenset(n for n in SEL_CLASS_RE.findall(part) if IDENT_RE.match(n))
            if names:
                out.setdefault(part, names)
    return out


def css_regions(src):
    """从样式表来源文件里切出**CSS 文本区**（⛔ 不把 JS/Python 代码当样式表）。

    ★ 为什么要切：样式表来源是 **Python 源码**（生成器里的 CSS 常量），其中夹着大量 JS。
      若整文件扫 `selector{`，JS 里 `{` 之前的代码会被当成选择器（实测踩到：`$('backbtn')`
      一类被抽出，把 JS 里的 id 误当 class 判死）。
    ★ 实现已收拢到共用薄工具 `gate_common.css_regions`（⛔ 不造第二套实现）。
    """
    return _GC.css_regions(src)


def selectors_in_source(src):
    """一个来源文件里的全部类选择器（跨其全部 CSS 区取并集）。"""
    out = {}
    for region in css_regions(src):
        for sel, names in selectors_of(region).items():
            out.setdefault(sel, names)
    return out


def collect(site_root, profile, contract):
    pages = pages_of(site_root, profile)
    per_page_classes = {}
    for rel, _fam in pages:
        txt = open(os.path.join(site_root, rel), encoding="utf-8", errors="replace").read()
        per_page_classes[rel] = class_groups_in(txt)
    fams = {}
    for fam, spec in (contract.get("families") or {}).items():
        fams[fam] = spec
    # 样式表来源：各族的生成器源码（= 产物内联样式的字面来源），**带所属族**。
    # ★ 判据作用域（SH5 §4.0 第 1 条「判据对象必须与断言对象一致」）：某族的样式表只服务该族
    #   的页面 ⇒ 「零引用」必须**在该族自己的页面上**判，⛔ 不拿别族的页面判它。
    #   实测踩到：`gen-interactive.py` 的 `.btn.on` / `.badge.cnt` 等在本族页面上确实未用（真孤儿），
    #   但若拿全站 69 页当参照，会把它与「别族未用」混在一起，登记面变成一本糊涂账。
    css_sources = {}
    fam_of_source = {}
    for fam, spec in sorted(fams.items()):
        for t in (spec.get("targets") or []):
            if not t.endswith(".py"):
                continue
            fp = os.path.join(site_root, t)
            if os.path.isfile(fp):
                css_sources[t] = open(fp, encoding="utf-8", errors="replace").read()
                fam_of_source.setdefault(t, set()).add(fam)
    return pages, per_page_classes, css_sources, fam_of_source


def judge(ctx):
    R = []
    site_root = ctx["site_root"]
    profile = ctx["profile"]
    manifest = ctx["manifest"]
    pages, per_page_classes, css_sources = ctx["pages"], ctx["per_page"], ctx["css"]
    fam_of_source = ctx.get("fam_of_source") or {}
    page_fam = dict(pages)

    def add(cid, name, ok, detail, klass):
        R.append((cid, name, bool(ok), detail, klass))

    n_classes = sum(len(g) for groups in per_page_classes.values() for g in groups)
    all_class_names = {c for groups in per_page_classes.values() for g in groups for c in g}
    sels = {}
    for src, text in sorted(css_sources.items()):
        for sel, names in selectors_in_source(text).items():
            sels.setdefault(sel, {"names": names, "src": src,
                                  "fams": fam_of_source.get(src)})

    def hits(sel_meta):
        """★ 判据作用域：只在该选择器**所属族**的页面上判命中（⛔ 不拿别族的页面判它）。"""
        fams = sel_meta.get("fams")
        for rel, groups in per_page_classes.items():
            if fams and page_fam.get(rel) not in fams:
                continue
            for g in groups:
                if sel_meta["names"] <= g:
                    return True
        return False

    # ---- H1 空集守卫
    reasons = []
    if not pages:
        reasons.append("扫描面 0 页（page_families glob 未命中任何文件）")
    if n_classes == 0:
        reasons.append("产物里 0 个 class 名（class 属性与 JS 字面量都没抽到）")
    if not sels:
        reasons.append("样式表里 0 个类选择器（css 来源：%s）" % (sorted(css_sources) or "无"))
    add("H1", "空集守卫（页/class/选择器三者均非空）", not reasons,
        "；".join(reasons) if reasons else
        "页 %d 个 · class 名 %d 个（去重 %d）· 类选择器 %d 个 · css 来源 %d 个文件"
        % (len(pages), n_classes, len(all_class_names), len(sels), len(css_sources)), BLIND)

    # ---- H2 零引用选择器
    registered = list(manifest.get("registered_orphan_selectors") or [])
    reg_sels = {e.get("selector") for e in registered if isinstance(e, dict)}
    orphan, used = [], 0
    for sel, meta in sorted(sels.items()):
        if hits(meta):
            used += 1
        else:
            orphan.append(sel)
    unreg = [s for s in orphan if s not in reg_sels]
    add("H2", "零引用选择器（未命中者必须逐条登记）", not unreg,
        "未登记的零引用选择器 %d 个：%s" % (len(unreg), unreg[:6]) if unreg else
        "类选择器 %d 个（命中 %d / 零引用 %d），零引用者全部已登记：%s"
        % (len(sels), used, len(orphan), orphan or "无"), REPORT)

    # ---- H3 登记不得过期 / 不得幽灵
    bad3 = []
    for e in registered:
        if not isinstance(e, dict) or not e.get("selector"):
            bad3.append("登记项结构非法：%r" % (e,))
            continue
        sel = e["selector"]
        if sel not in sels:
            bad3.append("幽灵登记（样式表里没有这个选择器）：%s" % sel)
            continue
        if hits(sels[sel]):
            bad3.append("登记过期（该选择器其实被真实产物命中）：%s" % sel)
    add("H3", "登记不得过期／不得幽灵（登记项必须真的零命中且在样式表内）", not bad3,
        "；".join(bad3[:4]) if bad3 else "登记 %d 项全部为真零引用且存在于样式表" % len(registered), REPORT)

    return R


def run(site_root, profile_path, manifest_path):
    profile = load_json(profile_path, "profile")
    manifest = load_json(manifest_path, "门控清单")
    contract = load_json(os.path.join(HERE, "vendor/pipeline/values/open-code-review-kg.json"), "值件")
    pages, per_page, css, fam_of_source = collect(site_root, profile, contract)
    return judge({"site_root": site_root, "profile": profile, "manifest": manifest,
                  "pages": pages, "per_page": per_page, "css": css,
                  "fam_of_source": fam_of_source})


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
    nf = sum(1 for r in R if not r[2])
    blind = [r for r in R if r[4] == BLIND and not r[2]]
    print("\n=== 死 CSS 门控：%d 项判据，%d FAIL（blind %d）===" % (len(R), nf, len(blind)))
    if blind:
        return 1
    return 0


# --------------------------------------------------------------------------- selftest
FIX_PROFILE = {"page_families": [{"glob": "pages/*.html", "family": "default"}]}
FIX_CONTRACT = {"families": {"default": {"targets": ["gen.py"], "overrides": {}}}}
FIX_GEN = """
BASE_CSS = '''
.a{color:red}
.b .c{display:flex}
.d{color:blue}
'''
"""
PAGE = '<!DOCTYPE html><html><body><div class="a b">x</div><div class="c">y</div>' \
       '<script>var d=document.createElement("div");d.className="row";</script></body></html>\n'


def _tree(tmp, page=PAGE, gen=FIX_GEN, manifest=None):
    os.makedirs(os.path.join(tmp, "pages"), exist_ok=True)
    open(os.path.join(tmp, "pages/p.html"), "w", encoding="utf-8").write(page)
    open(os.path.join(tmp, "gen.py"), "w", encoding="utf-8").write(gen)
    open(os.path.join(tmp, "profile.json"), "w", encoding="utf-8").write(json.dumps(FIX_PROFILE))
    open(os.path.join(tmp, "contract.json"), "w", encoding="utf-8").write(json.dumps(FIX_CONTRACT))
    open(os.path.join(tmp, "manifest.json"), "w", encoding="utf-8").write(
        json.dumps(manifest if manifest is not None else {"registered_orphan_selectors": []}))
    return tmp


def _judge(tmp):
    profile = load_json(os.path.join(tmp, "profile.json"), "p")
    manifest = load_json(os.path.join(tmp, "manifest.json"), "m")
    pages, per_page, css, fam_of_source = collect(tmp, profile, FIX_CONTRACT)
    return judge({"site_root": tmp, "profile": profile, "manifest": manifest,
                  "pages": pages, "per_page": per_page, "css": css,
                  "fam_of_source": fam_of_source})


def selftest():
    import shutil
    cases = []

    def case(name, cid, build, expect_fail=True, expect_pass=False):
        tmp = tempfile.mkdtemp(prefix="dcss-")
        try:
            build(tmp)
            R = _judge(tmp)
            got = {r[0]: r[2] for r in R}
            if expect_pass:
                ok = all(r[2] for r in R)
            else:
                ok = (got.get(cid) is False) if expect_fail else bool(got.get(cid))
            note = ""
        except Exception as exc:  # noqa: BLE001
            ok, note = False, "异常：%s" % exc
        cases.append((name, ok, note))
        shutil.rmtree(tmp, ignore_errors=True)

    def base(tmp, page=PAGE, gen=FIX_GEN, manifest=None, profile=None):
        _tree(tmp, page=page, gen=gen, manifest=manifest)
        if profile is not None:
            open(os.path.join(tmp, "profile.json"), "w", encoding="utf-8").write(json.dumps(profile))

    case("正向夹具应 0 FAIL（.d 已登记）",
         None, lambda t: base(t, manifest={"registered_orphan_selectors": [
             {"selector": ".d", "reason": "夹具：孤儿选择器，登记保留"},
             {"selector": ".b .c", "reason": "夹具：组合选择器，登记保留"}]}), expect_pass=True)
    case("H1 负例：扫描面 0 页",
         "H1", lambda t: base(t, profile={"page_families": [{"glob": "nope/*.html", "family": "default"}]}))
    case("H1 负例：产物里 0 个 class 名",
         "H1", lambda t: base(t, page="<!DOCTYPE html><html><body>no classes</body></html>\n"))
    case("H1 负例：样式表里 0 个类选择器",
         "H1", lambda t: base(t, gen="BASE_CSS = '''table{border-collapse:collapse}'''\n"))
    case("H2 负例：出现未登记的零引用选择器（.d）",
         "H2", lambda t: base(t))
    case("H3 负例：登记过期（.a 其实被命中）",
         "H3", lambda t: base(t, manifest={"registered_orphan_selectors": [
             {"selector": ".a", "reason": "夹具：过期登记"}]}))
    case("H3 负例：幽灵登记（样式表里没有 .zzz）",
         "H3", lambda t: base(t, manifest={"registered_orphan_selectors": [
             {"selector": ".zzz", "reason": "夹具：幽灵登记"}]}))
    case("★ 假阳样本：JS 里 className=\"row\" 的字面量必须被算作已引用（.row 不得判死）",
         None, lambda t: base(
             t, gen=FIX_GEN + ".row{display:flex}\n",
             manifest={"registered_orphan_selectors": [{"selector": ".d", "reason": "夹具"},
                                                       {"selector": ".b .c", "reason": "夹具"}]}),
         expect_pass=True)
    case("★ 假阳样本：`.b .c` 组合选择器不得因 .b 与 .c 分别出现就判命中（须同属一个 class 属性）",
         None, lambda t: base(
             t, page='<!DOCTYPE html><html><body><div class="a b"></div><div class="c"></div></body></html>\n',
             manifest={"registered_orphan_selectors": [{"selector": ".d", "reason": "夹具"},
                                                       {"selector": ".b .c", "reason": "夹具"}]}),
         expect_pass=True)

    ok = all(v for _, v, _ in cases)
    for name, res, note in cases:
        print("  [%s] %s%s" % ("PASS" if res else "FAIL", name, ("  ← " + note) if note else ""))
    print("\n=== gate_dead_css.py 自检：%d 项，%d FAIL ===" % (len(cases), sum(1 for _, v, _ in cases if not v)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
