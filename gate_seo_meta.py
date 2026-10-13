#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gate_seo_meta.py — open-code-review-kg 的**站点侧元数据门控**（批 H · 标准档新增）。

★ 执行强度：**report-only**（`hard_blocking` 枚举不含 metadata；擅自扩枚举＝改 schema）。
★ 判据定义来源：`solutions/_shared/SH4-seo-meta.md` §4.2。

★ 本步的实测事实（必须如实登记，⛔ 不得读作「没问题」）：
    本站 69 页**全部**缺 `meta description` / `og:*` / `canonical` / favicon。
    本门控因此会**如实报 FAIL**（report-only，不阻断生成），把这批缺口变成**可见的基线数字**；
    ⛔ 本批不修它们（属 SH4 的后续步，且改 `<head>` 会动全部 10 个生成器）。

判据（5 条）：
  S1 [blind]  空集守卫：扫描面 0 页 ⇒ FAIL
  S2 [report] `<title>` 非空且页页有
  S3 [report] `meta[name=description]` 非空
  S4 [report] `link[rel=canonical]` 存在且为绝对 URL
  S5 [report] favicon：`link[rel~=icon]` 存在
  （另附：`og:*` 与 `lang` 属性的计数进 detail，不单列判据——避免把「一条事实」拆成多条判据
    以虚增判据数，见 SH5 §4.0 第 8 条「判据蕴含关系要声明」）

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

TITLE_RE = re.compile(r"<title\b[^>]*>(.*?)</title>", re.I | re.S)
DESC_RE = re.compile(r"""<meta\b[^>]*\bname\s*=\s*["']description["'][^>]*>""", re.I)
DESC_CONTENT_RE = re.compile(r"""\bcontent\s*=\s*["']([^"']*)["']""", re.I)
CANON_RE = re.compile(r"""<link\b[^>]*\brel\s*=\s*["']?canonical["']?[^>]*>""", re.I)
HREF_RE = re.compile(r"""\bhref\s*=\s*["']([^"']*)["']""", re.I)
ICON_RE = re.compile(r"""<link\b[^>]*\brel\s*=\s*["']?[^"'>]*\bicon\b[^"'>]*["']?[^>]*>""", re.I)
OG_RE = re.compile(r"""<meta\b[^>]*\bproperty\s*=\s*["']og:""", re.I)
LANG_RE = re.compile(r"""<html\b[^>]*\blang\s*=\s*["']([^"']+)["']""", re.I)

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


def collect(site_root, profile):
    pages = {}
    for rule in profile.get("page_families") or []:
        for absp in sorted(glob.glob(os.path.join(site_root, rule["glob"]), recursive=True)):
            if os.path.isfile(absp):
                rel = os.path.relpath(absp, site_root).replace(os.sep, "/")
                pages[rel] = open(absp, encoding="utf-8", errors="replace").read()
    return pages


def judge(ctx):
    R = []
    pages = ctx["pages"]

    def add(cid, name, ok, detail, klass):
        R.append((cid, name, bool(ok), detail, klass))

    add("S1", "空集守卫（扫描面非空）", bool(pages),
        "扫描面 0 页（page_families glob 未命中任何文件）" if not pages else
        "扫描 %d 页" % len(pages), BLIND)

    # S2 title
    bad2 = []
    for rel, t in sorted(pages.items()):
        m = TITLE_RE.search(t)
        if not m or not m.group(1).strip():
            bad2.append(rel)
    add("S2", "`<title>` 非空且页页有", not bad2,
        "缺/空 title 的页 %d 个：%s" % (len(bad2), bad2[:6]) if bad2 else
        "全部 %d 页都有非空 <title>" % len(pages), REPORT)

    # S3 description
    bad3 = []
    for rel, t in sorted(pages.items()):
        m = DESC_RE.search(t)
        if not m:
            bad3.append(rel)
            continue
        c = DESC_CONTENT_RE.search(m.group(0))
        if not c or not c.group(1).strip():
            bad3.append(rel)
    add("S3", "`meta[name=description]` 非空", not bad3,
        "缺/空 description 的页 %d 个：%s" % (len(bad3), bad3[:6]) if bad3 else
        "全部 %d 页都有非空 description" % len(pages), REPORT)

    # S4 canonical
    bad4 = []
    for rel, t in sorted(pages.items()):
        m = CANON_RE.search(t)
        if not m:
            bad4.append(rel)
            continue
        h = HREF_RE.search(m.group(0))
        if not h or not h.group(1).startswith(("http://", "https://")):
            bad4.append(rel)
    add("S4", "`link[rel=canonical]` 存在且为绝对 URL", not bad4,
        "缺/非绝对 canonical 的页 %d 个：%s" % (len(bad4), bad4[:6]) if bad4 else
        "全部 %d 页都有绝对 canonical" % len(pages), REPORT)

    # S5 favicon
    bad5 = sorted(rel for rel, t in pages.items() if not ICON_RE.search(t))
    add("S5", "favicon（`link[rel~=icon]`）", not bad5,
        "缺 favicon 的页 %d 个：%s" % (len(bad5), bad5[:6]) if bad5 else
        "全部 %d 页都声明了 favicon" % len(pages), REPORT)

    og = sum(1 for t in pages.values() if OG_RE.search(t))
    lang = sum(1 for t in pages.values() if LANG_RE.search(t))
    R.append(("S-extra", "（不单列判据）og:* 页数 / lang 属性页数", True,
              "og:* 命中 %d/%d 页 · lang 属性命中 %d/%d 页（本批不修，只记基线）"
              % (og, len(pages), lang, len(pages)), REPORT))
    return R


def run(site_root, profile_path):
    profile = load_json(profile_path, "profile")
    return judge({"pages": collect(site_root, profile)})


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
    print("\n=== 元数据门控（report-only）：%d 项判据，%d FAIL（blind %d）==="
          % (len(R), sum(1 for r in R if not r[2]), len(blind)))
    return 1 if blind else 0


# --------------------------------------------------------------------------- selftest
GOOD = ('<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">'
        '<title>页标题</title>'
        '<meta name="description" content="一段描述">'
        '<link rel="canonical" href="https://example.org/p.html">'
        '<link rel="icon" href="/favicon.ico">'
        '<meta property="og:title" content="t">'
        '</head><body>hi</body></html>\n')
FIX_PROFILE = {"page_families": [{"glob": "pages/*.html", "family": "default"}]}


def _tree(tmp, page=GOOD):
    os.makedirs(os.path.join(tmp, "pages"), exist_ok=True)
    open(os.path.join(tmp, "pages/p.html"), "w", encoding="utf-8").write(page)
    open(os.path.join(tmp, "profile.json"), "w", encoding="utf-8").write(json.dumps(FIX_PROFILE))
    return tmp


def _judge(tmp):
    return judge({"pages": collect(tmp, load_json(os.path.join(tmp, "profile.json"), "p"))})


def selftest():
    import shutil
    cases = []

    def case(name, cid, build, expect_fail=True, expect_pass=False):
        tmp = tempfile.mkdtemp(prefix="seo-")
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
    case("S1 负例：扫描面 0 页", "S1",
         lambda t: (_tree(t), open(os.path.join(t, "profile.json"), "w").write(
             json.dumps({"page_families": [{"glob": "nope/*.html", "family": "default"}]}))))
    case("S2 负例：缺 title", "S2", lambda t: _tree(t, page=GOOD.replace("<title>页标题</title>", "")))
    case("S2 负例：空 title", "S2", lambda t: _tree(t, page=GOOD.replace("<title>页标题</title>", "<title>  </title>")))
    case("S3 负例：缺 description", "S3",
         lambda t: _tree(t, page=GOOD.replace('<meta name="description" content="一段描述">', "")))
    case("S3 负例：description 内容为空", "S3",
         lambda t: _tree(t, page=GOOD.replace('content="一段描述"', 'content=""')))
    case("S4 负例：缺 canonical", "S4",
         lambda t: _tree(t, page=GOOD.replace('<link rel="canonical" href="https://example.org/p.html">', "")))
    case("★ 假阳样本：相对 URL 的 canonical 不得算通过", "S4",
         lambda t: _tree(t, page=GOOD.replace('href="https://example.org/p.html"', 'href="p.html"')))
    case("S5 负例：缺 favicon", "S5",
         lambda t: _tree(t, page=GOOD.replace('<link rel="icon" href="/favicon.ico">', "")))

    ok = all(v for _, v, _ in cases)
    for name, res, note in cases:
        print("  [%s] %s%s" % ("PASS" if res else "FAIL", name, ("  ← " + note) if note else ""))
    print("\n=== gate_seo_meta.py 自检：%d 项，%d FAIL ===" % (len(cases), sum(1 for _, v, _ in cases if not v)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
