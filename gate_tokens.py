#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gate_tokens.py — open-code-review-kg 的**站点侧令牌门控**（批 H · 标准档新增）。

范式与纪律来源：`solutions/_shared/SH5-gating.md` §4.0 十条；形状照批 E 在 `12-factor-methodology-kg`
立的先例（仓根 `gate_tokens.py`，⛔ 不散落在 `07-checkpoint/`，见值件 meta.decisions.B6_gate_location）。

用法：
    python3 gate_tokens.py --site-root . --manifest gate-manifest.json
    python3 gate_tokens.py --site-root . --manifest gate-manifest.json --mode report
    python3 gate_tokens.py --site-root . --manifest gate-manifest.json --mode enforce
    python3 gate_tokens.py --site-root . --manifest gate-manifest.json --json
    python3 gate_tokens.py --selftest

执行强度：
    `--mode enforce`（本站默认，见 build/profile.json 的 gates.mode_now）——任一 hard 类判据 FAIL 即 exit 1。
    `--mode report` —— 判据全跑、逐条打印，除 blind 类外不阻断。
    ★ blind 类（G1 空集守卫）**不随报告模式放宽**：它守的是「门控自己是否致盲」，不是站点缺陷；
      致盲时报告模式也 exit 1 —— 否则「报告模式全绿」会是假绿。

判据（11 条，逐条声明判据对象；⛔ 无豁免字段、⛔ 不静默跳过）：
  G1  [blind]  空集守卫：扫描面为 0 页 / 0 族 / 0 令牌 / 未声明 page_families ⇒ FAIL
  G2  [hard]   族内唯一值：同一族内同名令牌必须同值（⛔ **不**判「全站唯一值」——族覆盖是合法的）
  G3  [hard]   派生一致性：每个页面的首个 `:root` 块（归一化后）== 值件对该族的派生结果
  G4  [hard]   跨族差异逐族登记：全站同名令牌出现的**每一个**取值，都必须能被某个族的派生解释
  G5  [hard]   ★ **判据 4（Q2-A 收敛后的状态判）**：`--warn` 全站取值数 = 1 且 `--danger` 命中数 = 0
  G6  [hard]   border 分档极性：强分隔（--border）对比度必须 > 弱分隔（--border-subtle）
  G7  [混合]   成对对比度：每个非 surface 色角色令牌对 surface.page，阈值与门档取自 usage_tiers
  G8  [混合]   零引用令牌登记：站点级零引用（hard）与页级未用（report）都必须逐枚登记，且登记不得过期
  G9  [hard]   生成器单源不变量：gen-index.py 不得再持令牌字面值；gen_common.BASE_CSS 首个非空行必须是 `:root` 块
  G10 [hard]   未声明令牌：盘上出现值件未声明的令牌名 ⇒ FAIL（防「悄悄加令牌」）
  G11 [hard]   ★ 产物存在性与扫描面完备：profile.targets 全在 · no_root_pages 真的无 `:root` ·
               盘上 HTML 全集 ⊆ page_families 覆盖 · 每页恰 1 个 `:root` 与恰 1 个内联 `<style>`

★ 判据蕴含关系声明（SH5 §4.0 第 8 条）：
    G5 ⊂ G4 —— G5 只对**两枚**已被用户裁定收敛的令牌（`--warn` / `--danger`）作状态判；
    G4 覆盖**全部**令牌并要求每一处多值都能被某个族解释。⛔ 两者不可互相替代：
    G5 判「收敛目标是否达成」，G4 判「剩余的差异是否都是**合法的族覆盖且已逐族登记**」。
    ★ 为什么 G5 必须限定在本站两枚令牌上：`pipeline/README.md:36-37` 明禁「全站同名令牌唯一值」
      判据——那会把**合法**的页面族覆盖（如 12-factor 的 `--warn` 两值，Qa-A 裁定逐族保留）
      判成 FAIL。本站之所以能作此状态判，是因为 **Q2-A 已裁定收敛**（见值件 meta.decisions.B5）。

★ 与 AUD 侧契约门控 `check_site_tokens.py` 的分工（⛔ 不重叠、不互相替代）：
    AUD 侧跑 C1–C12，判「值件 ↔ 派生产物 ↔ 改动前令牌集」的**骨架契约**，
    需要 `--orig-root`（改动前克隆）与 `~/opencode/projects/fe-starter-kit` ⇒ 在别的机器上必然 FAIL。
    站点侧（本件）跑 G1–G11，判「仓内盘上事实 ↔ 值件」的**站点契约**，⛔ 不依赖克隆/仓外路径。

退出码：0 全过（或报告模式且有 hard 类 FAIL 但无 blind FAIL）/ 1 有阻断级 FAIL / 2 输入错误 / 3 护栏拒读
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys
import tempfile

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
VENDOR = os.path.join(HERE, "vendor", "pipeline")
if VENDOR not in sys.path:
    sys.path.insert(0, VENDOR)
import derive_site_tokens as D  # noqa: E402  ★ 复用派生器的块定位/归一化/三级覆盖（⛔ 不造第二套实现）
sys.path.insert(0, os.path.join(HERE, "vendor", "tools"))
import contrast as C            # noqa: E402  ★ 复用对比度实现（tools/contrast.py 的唯一实现）

VAR_RE = re.compile(r"var\(\s*(--[A-Za-z0-9_-]+)")
LITERAL_RE = re.compile(r"--[A-Za-z0-9_-]+\s*:\s*#[0-9a-fA-F]{3,8}")
STYLE_RE = re.compile(r"<style\b", re.I)
SKIP_DIRS = {".git", "__pycache__", "vendor", "node_modules", "07-checkpoint", "08-source", "05-source"}

BLIND, HARD, REPORT = "blind", "hard", "report"


def _strip_py_comments(src):
    """剥掉 Python **行注释**（⛔ 不碰字符串字面量）。

    ★ 为什么要剥：G9 判「生成器是否仍持令牌字面值」，若把注释里为了说明不变量而写的
      `:root{…}` 字样当成事实，就会**假阳**（12-factor 站实测踩到过一次）。
    """
    out, q = [], None
    for line in src.split("\n"):
        cut = len(line)
        for i, ch in enumerate(line):
            if q:
                if ch == q:
                    q = None
            elif ch in "\"'":
                q = ch
            elif ch == "#":
                cut = i
                break
        out.append(line[:cut])
    return "\n".join(out)


class GateError(Exception):
    """护栏拒读（exit 3）——输入缺失/非法，⛔ 不静默降级为「跳过」。"""


def load_json(path, label):
    if not os.path.isfile(path):
        raise GateError("%s 不存在：%s" % (label, path))
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception as exc:  # noqa: BLE001
        raise GateError("%s 非法 JSON：%s" % (label, exc))


# --------------------------------------------------------------------------- 采集
def repo_html(site_root):
    """仓内 HTML 全集（口径与 evidence/h/tools/measure_station_baseline.py 一致）。"""
    out = []
    for dp, dn, fn in os.walk(site_root):
        dn[:] = sorted(d for d in dn if d not in SKIP_DIRS)
        for f in sorted(fn):
            if f.endswith(".html"):
                out.append(os.path.relpath(os.path.join(dp, f), site_root).replace(os.sep, "/"))
    return sorted(out)


def collect_pages(site_root, profile):
    """按 profile.page_families 的 glob 规则采集页面 → {rel: {...}}。"""
    out = {}
    for rule in profile.get("page_families") or []:
        pat = os.path.join(site_root, rule["glob"])
        for absp in sorted(glob.glob(pat, recursive=True)):
            if not os.path.isfile(absp):
                continue
            rel = os.path.relpath(absp, site_root).replace(os.sep, "/")
            raw = open(absp, encoding="utf-8", errors="replace").read()
            blk = D.extract_block(raw)
            out[rel] = {"family": rule["family"], "raw": raw, "block": blk,
                        "tokens": D.parse_tokens(blk) if blk else {},
                        "root_count": len(re.findall(r":root\s*\{[^{}]*\}", raw, re.S)),
                        "style_count": len(STYLE_RE.findall(raw))}
    return out


def declared_token_names(contract):
    """值件声明的全部令牌名 = 角色绑定 ∪ 各族 overrides ∪ 透传。"""
    names = set((contract.get("binding") or {}).get("site_token_names", {}).values())
    for spec in (contract.get("families") or {}).values():
        names |= set((spec.get("overrides") or {}).keys())
    for _g, kv in ((contract.get("binding") or {}).get("passthrough_tokens") or {}).items():
        if isinstance(kv, dict):
            names |= {k for k in kv if str(k).startswith("--")}
    return names


def family_expected(contract, profile, fam):
    """复用派生器的三级覆盖（P1–P7 护栏在内）→ 该族的期望令牌表。"""
    _fid, tokens = D.build_tokens(contract, profile, fam)
    return tokens


# --------------------------------------------------------------------------- 判据
def judge(ctx):
    """跑全部判据，返回 [(id, 名称, ok, detail, klass)]。"""
    R = []
    site_root = ctx["site_root"]
    contract = ctx["contract"]
    profile = ctx["profile"]
    pages = ctx["pages"]
    fams = list((contract.get("families") or {}).keys())

    def add(cid, name, ok, detail, klass):
        R.append((cid, name, bool(ok), detail, klass))

    # ---- G1 空集守卫（blind）
    reasons = []
    if not fams:
        reasons.append("值件未声明任何族")
    if not pages:
        reasons.append("扫描面 0 页（page_families glob 未命中任何文件）")
    if not (profile.get("page_families") or []):
        reasons.append("profile 未声明 page_families（扫描面无从谈起）")
    if not any(v["tokens"] for v in pages.values()):
        reasons.append("全部页面的 :root 块都解析出 0 枚令牌")
    if not declared_token_names(contract):
        reasons.append("值件声明的令牌名为空")
    add("G1", "空集守卫（扫描面/族/令牌名均非空）", not reasons,
        "；".join(reasons) if reasons else
        "族 %d 个 · 页 %d 个 · 令牌名 %d 枚 · 有 :root 的页 %d 个"
        % (len(fams), len(pages), len(declared_token_names(contract)),
           sum(1 for v in pages.values() if v["block"])), BLIND)

    # ---- 族期望值缓存：派生失败一律记为错误值（⛔ 不静默跳过、⛔ 不让异常逃出判据）
    exp_cache = {}
    for fam in fams:
        try:
            exp_cache[fam] = family_expected(contract, profile, fam)
        except Exception as exc:  # noqa: BLE001
            exp_cache[fam] = {"__error__": str(exc)}

    # ---- G2 族内唯一值（hard）
    dup_bad = []
    for fam in fams:
        seen = {}
        for rel, v in sorted(pages.items()):
            if v["family"] != fam:
                continue
            for tok, val in v["tokens"].items():
                if tok in seen and seen[tok][1] != val:
                    dup_bad.append("族 %s 的 %s 出现两值：%s(%s) / %s(%s)"
                                   % (fam, tok, seen[tok][1], seen[tok][0], val, rel))
                else:
                    seen.setdefault(tok, (rel, val))
    add("G2", "族内唯一值（同族同名同值；⛔ 不判全站唯一值）", not dup_bad,
        "；".join(dup_bad[:4]) if dup_bad else "各族内同名令牌均为单值", HARD)

    # ---- G3 派生一致性（hard）
    drift = []
    checked = []
    for fam in fams:
        exp = exp_cache[fam]
        if "__error__" in exp:
            drift.append("族 %s 无法派生（%s）" % (fam, exp["__error__"]))
            continue
        want = D.normalize(D.render(exp))
        for rel, v in sorted(pages.items()):
            if v["family"] != fam or not v["block"]:
                continue
            checked.append(rel)
            if D.normalize(v["block"]) != want:
                drift.append("%s（族 %s）与值件派生结果不一致" % (rel, fam))
    # 生成器源目标也要对账（它们同样是 profile.targets 的成员）
    for t in profile.get("targets") or []:
        if not t["path"].endswith(".py"):
            continue
        fp = os.path.join(site_root, t["path"])
        if not os.path.isfile(fp):
            drift.append("源目标不存在：%s" % t["path"])
            continue
        blk = D.extract_block(open(fp, encoding="utf-8", errors="replace").read())
        if not blk:
            drift.append("源目标无 :root 块：%s" % t["path"])
            continue
        checked.append(t["path"])
        exp = exp_cache.get(t["family"], {})
        if "__error__" in exp:
            drift.append("源目标 %s 的族 %s 无法派生（%s）" % (t["path"], t["family"], exp["__error__"]))
        elif D.normalize(blk) != D.normalize(D.render(exp)):
            drift.append("源目标 %s 与族 %s 派生结果不一致" % (t["path"], t["family"]))
    add("G3", "派生一致性（页面与生成器源的首个 :root 块 == 值件派生）", not drift,
        "；".join(drift[:4]) if drift else "核对 %d 个对象的 :root 块，全部与值件派生一致" % len(checked), HARD)

    # ---- G4 跨族差异逐族登记（hard）
    per_token = {}
    for rel, v in sorted(pages.items()):
        for tok, val in v["tokens"].items():
            per_token.setdefault(tok, {}).setdefault(val, []).append(rel)
    unexplained = []
    for tok, byval in per_token.items():
        if len(byval) < 2:
            continue
        for val, rels in byval.items():
            ok_any = False
            for fam in fams:
                if exp_cache.get(fam, {}).get(tok) == val:
                    ok_any = True
                    break
            if not ok_any:
                unexplained.append("%s=%s（%s）不被任何族解释" % (tok, val, rels[0]))
    multi = [t for t, m in per_token.items() if len(m) > 1]
    add("G4", "跨族差异逐族登记（多值的每一处都能被某族派生解释）", not unexplained,
        "；".join(unexplained[:4]) if unexplained else
        "多值令牌 %d 枚（%s），全部逐族登记" % (len(multi), ",".join(sorted(multi)) or "无"), HARD)

    # ---- G5 ★ 判据 4：Q2-A 收敛后的状态判（hard）
    warn_vals = sorted(per_token.get("--warn", {}))
    danger_hits = sorted(per_token.get("--danger", {}))
    g5 = []
    if len(warn_vals) != 1:
        g5.append("--warn 全站取值数 = %d（期望 1）：%s" % (len(warn_vals), warn_vals))
    if warn_vals and warn_vals != ["#e8933b"]:
        g5.append("--warn 取值 = %s（Q2-A 裁定收敛到 #e8933b）" % warn_vals)
    if danger_hits:
        g5.append("--danger 仍有声明（Q 裁定：退役并入 --err）")
    add("G5", "★ 判据 4（Q2-A 收敛后的状态判）：--warn 全站唯一值且 --danger 命中数 = 0", not g5,
        "；".join(g5) if g5 else
        "--warn=%s（全站 %d 页）· --danger 命中 0 处 ⇒ Q2-A 收敛目标达成"
        % (warn_vals[0] if warn_vals else "?", len(per_token.get("--warn", {}).get(warn_vals[0], [])) if warn_vals else 0),
        HARD)

    # ---- G6 border 分档极性（hard）★ 判**盘上真实取值**（族内一致性由 G2 保证）
    names = (contract.get("binding") or {}).get("site_token_names", {})
    strong, weak = names.get("border.line"), names.get("border.subtle")
    surf = names.get("surface.page")
    fam_toks = {}
    for fam in fams:
        for rel in sorted(pages):
            v = pages[rel]
            if v["family"] == fam and v["tokens"]:
                fam_toks[fam] = v["tokens"]
                break
    pol = []
    if not strong or not weak:
        pol.append("值件未绑定 border.line / border.subtle（极性判据无从谈起）")
    elif not fam_toks:
        pol.append("没有任何族在盘上有可判的令牌集（空集守卫）")
    else:
        for fam, toks in sorted(fam_toks.items()):
            a, b, bg = toks.get(strong), toks.get(weak), toks.get(surf)
            if a is None or b is None or bg is None:
                pol.append("族 %s 缺 %s / %s / %s（空集守卫）" % (fam, strong, weak, surf))
                continue
            ra = C.ratio(C.parse_color(str(a)), C.parse_color(str(bg)))
            rb = C.ratio(C.parse_color(str(b)), C.parse_color(str(bg)))
            if ra is None or rb is None or not ra > rb:
                pol.append("族 %s 极性反转：强 %s=%s(%s) 未强于 弱 %s=%s(%s)"
                           % (fam, strong, a, "n/a" if ra is None else "%.2f" % ra,
                              weak, b, "n/a" if rb is None else "%.2f" % rb))
    add("G6", "border 分档极性（强分隔对比度 > 弱分隔，判盘上取值）", not pol,
        "；".join(pol) if pol else
        "；".join("族 %s %s=%s(%.2f) > %s=%s(%.2f)"
                  % (f, strong, fam_toks[f][strong],
                     C.ratio(C.parse_color(fam_toks[f][strong]), C.parse_color(fam_toks[f][surf])),
                     weak, fam_toks[f][weak],
                     C.ratio(C.parse_color(fam_toks[f][weak]), C.parse_color(fam_toks[f][surf])))
                  for f in sorted(fam_toks)), HARD)

    # ---- G7 成对对比度（hard/report 由 usage_tiers.gate 逐档决定）★ 判盘上取值
    tiers = contract.get("usage_tiers") or {}
    roles = contract.get("roles") or {}
    form = (contract.get("scope") or {}).get("declared_forms", ["dark"])[0]
    hardbad, rep = [], []
    for fam, toks in sorted(fam_toks.items()):
        if surf not in toks:
            hardbad.append("族 %s 缺表面令牌 %s（空集守卫）" % (fam, surf))
            continue
        for role, token in sorted(names.items()):
            spec_role = roles.get(role) or {}
            if spec_role.get("kind") == "dimension":
                continue                      # ★ 尺寸类角色不是颜色对象
            if role.startswith("surface."):
                continue
            spec = tiers.get(spec_role.get("tier"))
            if not spec:
                hardbad.append("族 %s 角色 %s 的 tier=%r 未在 usage_tiers 内" % (fam, role, spec_role.get("tier")))
                continue
            need = (spec.get("min_contrast") or {}).get(form)
            if not need:
                continue
            a, b = toks.get(token), toks.get(surf)
            if a is None or b is None:
                hardbad.append("族 %s %s/%s 令牌缺失（空集守卫）" % (fam, role, token))
                continue
            rr = C.ratio(C.parse_color(str(a)), C.parse_color(str(b)))
            if spec.get("gate") == "hard":
                if rr is None or rr < need:
                    hardbad.append("族 %s %s=%s 对 %s=%s 仅 %s < %s"
                                   % (fam, token, a, surf, b, "n/a" if rr is None else "%.2f" % rr, need))
            else:
                rep.append("族 %s %s=%.2f（report-only 档）" % (fam, token, rr if rr is not None else -1))
    add("G7", "成对对比度（按 usage_tiers 的 min_contrast 与 gate 逐档）", not hardbad,
        "；".join(hardbad[:4]) if hardbad else "硬阻断对全部达标；report-only %d 条" % len(rep),
        HARD if hardbad else REPORT)

    # ---- G8 零引用令牌登记（hard: 站点级 / report: 页级）
    uses_site, uses_page = {}, {}
    for rel, v in sorted(pages.items()):
        refs = set(VAR_RE.findall(v["raw"]))
        for tok in v["tokens"]:
            uses_site[tok] = uses_site.get(tok, 0) + (1 if tok in refs else 0)
            uses_page[(tok, rel)] = 1 if tok in refs else 0
    reg = contract.get("dead_tokens") or {}
    reg_site = {e.get("token") for e in (reg.get("site_level_zero_ref") or [])}
    plu = reg.get("page_level_unused") or {}
    plist = plu.get("entries") if isinstance(plu, dict) else plu
    reg_page = {(e.get("token"), e.get("page")) for e in (plist or [])}
    declared_here = {t for t, n in uses_site.items() if n == 0}
    unreg_site = sorted(declared_here - reg_site)
    stale_site = sorted(reg_site - declared_here)
    unreg_page = sorted((t, r) for (t, r), n in uses_page.items()
                        if n == 0 and uses_site.get(t, 0) > 0 and (t, r) not in reg_page)
    stale_page = sorted((t, r) for (t, r) in reg_page if (t, r) in uses_page and uses_page[(t, r)] != 0)
    phantom_page = sorted((t, r) for (t, r) in reg_page if (t, r) not in uses_page)
    bad8 = []
    if unreg_site:
        bad8.append("站点级零引用未登记：%s" % unreg_site)
    if stale_site:
        bad8.append("登记了但实际有引用（登记过期）：%s" % stale_site)
    if stale_page:
        bad8.append("页级登记过期：%s" % stale_page[:6])
    if phantom_page:
        bad8.append("页级登记指向不存在的令牌/页（幽灵登记）：%s" % phantom_page[:6])
    rep8 = ["页级未用未登记 %d 条：%s" % (len(unreg_page), unreg_page[:6])] if unreg_page else []
    add("G8", "零引用令牌登记（站点级 hard / 页级 report；登记不得过期）", not bad8,
        "；".join(bad8 + rep8) if (bad8 or rep8) else
        "站点级零引用 %d 枚（%s）全部登记；页级未用 %d 条全部登记"
        % (len(declared_here), ",".join(sorted(declared_here)) or "无", len(reg_page)),
        HARD if bad8 else REPORT)

    # ---- G9 生成器单源不变量（hard）
    inv = profile.get("single_source_invariants")
    g9 = []
    if not inv:
        g9.append("profile 未声明 single_source_invariants（⛔ 不静默跳过）")
    else:
        mod = inv.get("base_css_module")
        attr = inv.get("base_css_attr", "BASE_CSS")
        fp = os.path.join(site_root, mod or "")
        if not mod or not os.path.isfile(fp):
            g9.append("BASE_CSS 模块不存在：%s" % mod)
        else:
            code = ("import json,sys; sys.path.insert(0, %r); import %s as m; "
                    "print(json.dumps((getattr(m,%r).strip().split('\\n',1)[0]), ensure_ascii=False))"
                    % (os.path.dirname(mod), os.path.basename(mod)[:-3], attr))
            r = subprocess.run([sys.executable, "-c", code], cwd=site_root,
                               capture_output=True, text=True)
            if r.returncode != 0:
                g9.append("导入 %s 失败：%s" % (mod, (r.stderr or "").strip()[-120:]))
            else:
                try:
                    first = json.loads(r.stdout.strip().splitlines()[-1])
                except Exception:  # noqa: BLE001
                    g9.append("无法解析 %s.%s 的首行" % (mod, attr))
                    first = None
                if first is not None and not D.extract_block(first):
                    g9.append("%s.%s 的首个非空行不是 `:root{...}` 块（单源不变量被破坏）"
                              % (mod, attr))
        for rel in (inv.get("literal_free_generators") or []):
            fp2 = os.path.join(site_root, rel)
            if not os.path.isfile(fp2):
                g9.append("声明的无字面值生成器不存在：%s" % rel)
                continue
            src = _strip_py_comments(open(fp2, encoding="utf-8", errors="replace").read())
            if D.extract_block(src):
                g9.append("%s 仍持有 :root 令牌块字面值（未从单源取）" % rel)
            m = LITERAL_RE.search(src)
            if m:
                g9.append("%s 仍持有令牌赋值字面值：%s" % (rel, m.group(0)))
            if attr not in src:
                g9.append("%s 未引用单源 %s" % (rel, attr))
    add("G9", "生成器单源不变量（无字面值块 ＋ BASE_CSS 首行即 :root 块）", not g9,
        "；".join(g9[:4]) if g9 else "单源不变量成立", HARD)

    # ---- G10 未声明令牌（hard）
    declared = declared_token_names(contract)
    unknown = []
    for rel, v in sorted(pages.items()):
        extra = sorted(set(v["tokens"]) - declared)
        if extra:
            unknown.append("%s 出现未声明令牌 %s" % (rel, extra))
    add("G10", "未声明令牌（盘上令牌名 ⊆ 值件声明面）", not unknown,
        "；".join(unknown[:4]) if unknown else "值件声明 %d 枚，盘上无未声明令牌" % len(declared), HARD)

    # ---- G11 产物存在性与扫描面完备（hard）★ 本步新增（方案 §7 判据 7 的仓内口径）
    miss = []
    for t in profile.get("targets") or []:
        if not os.path.isfile(os.path.join(site_root, t["path"])):
            miss.append("目标不存在：%s" % t["path"])
    for rel in (profile.get("no_root_pages") or []):
        fp = os.path.join(site_root, rel)
        if not os.path.isfile(fp):
            miss.append("no_root_pages 声明项不存在：%s" % rel)
        elif D.extract_block(open(fp, encoding="utf-8", errors="replace").read()):
            miss.append("no_root_pages 声明项 %s 竟然有 :root 块（声明与事实不一致）" % rel)
    on_disk = set(repo_html(site_root))
    covered = set(pages)
    # ★ no_root_pages 是**显式声明**的例外面（照 12-factor 先例：该表成员不进 page_families）⇒
    #   它不算「未被覆盖」，但 G11 的反向判据会断言它们**真的**没有 :root（见上）。
    declared_no_root = set(profile.get("no_root_pages") or [])
    uncovered = sorted(on_disk - covered - declared_no_root)
    if uncovered:
        miss.append("盘上 HTML 未被任何 page_families glob 覆盖（会「默认通过」）：%s" % uncovered)
    extra_covered = sorted(covered - on_disk)
    if extra_covered:
        miss.append("page_families 命中了非仓内 HTML：%s" % extra_covered)
    for rel, v in sorted(pages.items()):
        if v["root_count"] != 1:
            miss.append("%s 的 :root 块数 = %d（期望恰 1）" % (rel, v["root_count"]))
        if v["style_count"] != 1:
            miss.append("%s 的内联 <style> 块数 = %d（期望恰 1）" % (rel, v["style_count"]))
    add("G11", "产物存在性与扫描面完备（targets 全在 ＋ 盘上 HTML ⊆ 扫描面 ＋ 每页恰 1 个 :root/<style>）",
        not miss,
        "；".join(miss[:4]) if miss else
        "目标 %d 个全部存在；盘上 %d 个 HTML 全部被扫描面覆盖；每页恰 1 个 :root 与 1 个内联 <style>"
        % (len(profile.get("targets") or []), len(on_disk)), HARD)

    return R


# --------------------------------------------------------------------------- 主流程
def run(site_root, contract_path, profile_path, mode=None):
    contract = load_json(contract_path, "值件")
    profile = load_json(profile_path, "profile")
    pages = collect_pages(site_root, profile)
    ctx = {"site_root": site_root, "contract": contract, "profile": profile, "pages": pages}
    R = judge(ctx)
    m = mode or profile.get("gates", {}).get("mode_now") or "report"
    return R, m, pages


def summarize(R, mode, pages):
    blind_fail = [r for r in R if r[4] == BLIND and not r[2]]
    hard_fail = [r for r in R if r[4] == HARD and not r[2]]
    rep_fail = [r for r in R if r[4] == REPORT and not r[2]]
    counts = {"pages": len(pages), "with_root": sum(1 for v in pages.values() if v["block"]),
              "judges": len(R), "fail_total": sum(1 for r in R if not r[2]),
              "blind_fail": len(blind_fail), "hard_fail": len(hard_fail), "report_fail": len(rep_fail)}
    return counts, blind_fail, hard_fail, rep_fail


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--site-root", default=".")
    ap.add_argument("--contract", default=None)
    ap.add_argument("--profile", default=None)
    ap.add_argument("--manifest", default=None)
    ap.add_argument("--mode", choices=["report", "enforce"], default=None)
    ap.add_argument("--baseline-out", default=None)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()

    site_root = os.path.abspath(a.site_root)
    contract_path = a.contract or os.path.join(
        HERE, "vendor/pipeline/values/open-code-review-kg.json")
    profile_path = a.profile or os.path.join(site_root, "build/profile.json")
    if a.manifest and not os.path.isfile(os.path.join(site_root, a.manifest)):
        print("GUARD-REJECT: 清单不存在：%s" % a.manifest)
        return 3
    try:
        R, mode, pages = run(site_root, contract_path, profile_path, a.mode)
    except (GateError, D.GuardError) as exc:
        print("GUARD-REJECT: %s" % exc)
        return 3

    for cid, name, ok, detail, klass in R:
        print("[%s] %s %s（%s）— %s" % ("PASS" if ok else "FAIL", cid, name, klass, detail))
    counts, blind_fail, hard_fail, rep_fail = summarize(R, mode, pages)
    print("\n=== 站点令牌门控（mode=%s）：%d 项判据，%d FAIL（blind %d / hard %d / report %d）；"
          "扫描 %d 页（含 :root %d 页）==="
          % (mode, counts["judges"], counts["fail_total"], counts["blind_fail"],
             counts["hard_fail"], counts["report_fail"], counts["pages"], counts["with_root"]))
    if a.json or a.baseline_out:
        doc = {"site_root": site_root, "mode": mode, "counts": counts, "generated_at": "deterministic",
               "judges": [{"id": c, "name": n, "ok": o, "class": k, "detail": d} for c, n, o, d, k in R]}
        blob = json.dumps(doc, ensure_ascii=False, indent=2)
        if a.json:
            print(blob)
        if a.baseline_out:
            with open(a.baseline_out, "w", encoding="utf-8") as fh:
                fh.write(blob + "\n")
            print("基线已写入：%s" % a.baseline_out)

    if blind_fail:
        print("阻断：blind 类判据 FAIL（门控致盲，报告模式也不宽恕）")
        return 1
    if mode == "enforce" and hard_fail:
        print("阻断：enforce 模式下 hard 类判据 FAIL")
        return 1
    if hard_fail or rep_fail:
        print("报告模式：上述 FAIL 已记基线，不阻断（转硬条件见 build/profile.json 的 gates.mode_now_transition）")
    return 0


# --------------------------------------------------------------------------- selftest
FIX_CONTRACT = {
    "meta": {"id": "t", "contract_version": "0", "frozen_at": "2026-10-13", "title": "t"},
    "scope": {"site": "t", "upstream_repo_head": "0" * 40, "declared_forms": ["dark"]},
    "usage_tiers": {
        "body": {"allowed_use": "x", "min_contrast": {"dark": 4.5}, "gate": "hard"},
        "non-text": {"allowed_use": "x", "min_contrast": {"dark": 3.0}, "gate": "hard"},
        "non-text-decorative": {"allowed_use": "x", "min_contrast": {"dark": 3.0}, "gate": "report-only"},
    },
    "roles": {
        "text.primary": {"tier": "body", "kind": "text", "purpose": "p", "site_source": "s"},
        "border.line": {"tier": "non-text", "kind": "border", "purpose": "p", "site_source": "s"},
        "border.subtle": {"tier": "non-text-decorative", "kind": "border", "purpose": "p", "site_source": "s"},
        "surface.page": {"tier": "non-text", "kind": "surface", "purpose": "p", "site_source": "s"},
        "err": {"tier": "body", "kind": "semantic-text", "purpose": "p", "site_source": "s"},
        "ok": {"tier": "body", "kind": "semantic-text", "purpose": "p", "site_source": "s"},
        "warn": {"tier": "body", "kind": "semantic-text", "purpose": "p", "site_source": "s"},
    },
    "palettes": {"p": {"family": "f", "provenance": "x", "values": {
        "text.primary": {"dark": "#e6e8ee"},
        "border.line": {"dark": "#6b7280"},
        "border.subtle": {"dark": "#2a2f3a"},
        "surface.page": {"dark": "#0f1117"},
        "err": {"dark": "#ff6b6b"},
        "ok": {"dark": "#2fb98a"},
        "warn": {"dark": "#e8933b"},
    }}},
    "binding": {"site_token_names": {"text.primary": "--text", "border.line": "--border",
                                     "border.subtle": "--border-subtle", "surface.page": "--bg",
                                     "err": "--err", "ok": "--ok", "warn": "--warn"},
                "passthrough_tokens": {}},
    "families": {"default": {"targets": ["pages/a.html", "pages/c.html",
                                         "07-checkpoint/gen_common.py"],
                             "overrides": {}},
                 "04-interactive": {"targets": ["04-interactive/index.html"], "overrides": {}},
                 "report": {"targets": ["report.html"],
                            "overrides": {"--panel2": "#1c212c"}}},
    "derivation": {"state": "s", "direction": "d", "generator_ref": "g", "rule": "r"},
    "dead_tokens": {
        "site_level_zero_ref": [{"token": "--err", "reason": "夹具：语义角色，但两种页型都用不到"},
                                {"token": "--panel2", "reason": "夹具：report 族的非角色令牌，零引用"}],
        "page_level_unused": {"entries": [
            {"token": "--ok", "page": "pages/a.html", "reason": "夹具：a 页用不到，c 页用到"},
            {"token": "--warn", "page": "pages/a.html", "reason": "夹具：a 页用不到，c 页用到"},
            {"token": "--err", "page": "pages/a.html", "reason": "夹具：站点级零引用"},
            {"token": "--err", "page": "pages/c.html", "reason": "夹具：站点级零引用"},
            {"token": "--ok", "page": "04-interactive/index.html", "reason": "夹具：交互页用不到"},
            {"token": "--warn", "page": "04-interactive/index.html", "reason": "夹具：交互页用不到"},
            {"token": "--err", "page": "04-interactive/index.html", "reason": "夹具：站点级零引用"},
            {"token": "--ok", "page": "report.html", "reason": "夹具：报告页用不到"},
            {"token": "--warn", "page": "report.html", "reason": "夹具：报告页用不到"},
            {"token": "--err", "page": "report.html", "reason": "夹具：站点级零引用"},
        ]},
    },
}
FIX_PROFILE = {
    "site": "t", "form": "inline-single-source", "publish_dir": ".", "value_file": "v.json",
    "targets": [{"path": "pages/a.html", "mode": "root-block", "family": "default"},
                {"path": "pages/c.html", "mode": "root-block", "family": "default"},
                {"path": "07-checkpoint/gen_common.py", "mode": "root-block", "family": "default"},
                {"path": "04-interactive/index.html", "mode": "root-block", "family": "04-interactive"},
                {"path": "report.html", "mode": "root-block", "family": "report"}],
    "page_families": [{"glob": "pages/*.html", "family": "default"},
                      {"glob": "04-interactive/*.html", "family": "04-interactive"},
                      {"glob": "report.html", "family": "report"}],
    "no_root_pages": ["notes.html"],
    "single_source_invariants": {"base_css_module": "07-checkpoint/gen_common.py",
                                 "base_css_attr": "BASE_CSS",
                                 "literal_free_generators": ["07-checkpoint/gen-index.py"]},
    "gates": {"manifest": "gate-manifest.json", "mode_now": "enforce"},
}
FIX_ROOT_BLOCK = (":root{--text:#e6e8ee;--border:#6b7280;--border-subtle:#2a2f3a;--bg:#0f1117;"
                  "--err:#ff6b6b;--ok:#2fb98a;--warn:#e8933b;}")
FIX_ROOT_BLOCK_I = FIX_ROOT_BLOCK          # 04-interactive 与 default 同值（本站 Q2-A 收敛后的形态）


def _fix_page(extra_css, block=FIX_ROOT_BLOCK):
    return ('<!DOCTYPE html><html><head><style>\n' + block +
            '\nbody{background:var(--bg);color:var(--text);border:1px solid var(--border);}'
            '\n.s{color:var(--border-subtle);}' + extra_css +
            '\n</style></head><body>hi</body></html>\n')


FIX_PAGE = _fix_page("")                                  # a.html：不用 --ok/--warn/--err
FIX_PAGE_C = _fix_page("\n.ok{color:var(--ok);}\n.w{color:var(--warn);}")   # c.html：用 --ok/--warn
FIX_GEN_COMMON = ('#!/usr/bin/env python3\nBASE_CSS = """\n' + FIX_ROOT_BLOCK +
                  '\n*{box-sizing:border-box;}\n"""\n')
FIX_GEN_INDEX = ('#!/usr/bin/env python3\nfrom gen_common import BASE_CSS\n'
                 "ROOT_TOKENS = BASE_CSS.strip().split('\\n', 1)[0]\n"
                 'html = "<style>\\n  {root_tokens}\\n</style>".format(root_tokens=ROOT_TOKENS)\n')


def _fixture_tree(tmp):
    os.makedirs(os.path.join(tmp, "07-checkpoint"), exist_ok=True)
    os.makedirs(os.path.join(tmp, "04-interactive"), exist_ok=True)
    os.makedirs(os.path.join(tmp, "pages"), exist_ok=True)
    with open(os.path.join(tmp, "pages/a.html"), "w", encoding="utf-8") as fh:
        fh.write(FIX_PAGE)
    with open(os.path.join(tmp, "pages/c.html"), "w", encoding="utf-8") as fh:
        fh.write(FIX_PAGE_C)
    with open(os.path.join(tmp, "report.html"), "w", encoding="utf-8") as fh:
        fh.write(_fix_page("", FIX_ROOT_BLOCK[:-1] + "--panel2:#1c212c;}"))
    with open(os.path.join(tmp, "notes.html"), "w", encoding="utf-8") as fh:
        fh.write("<!DOCTYPE html><html><body>no root here</body></html>\n")
    with open(os.path.join(tmp, "04-interactive/index.html"), "w", encoding="utf-8") as fh:
        fh.write(_fix_page("", FIX_ROOT_BLOCK_I))
    with open(os.path.join(tmp, "07-checkpoint/gen_common.py"), "w", encoding="utf-8") as fh:
        fh.write(FIX_GEN_COMMON)
    with open(os.path.join(tmp, "07-checkpoint/gen-index.py"), "w", encoding="utf-8") as fh:
        fh.write(FIX_GEN_INDEX)
    cp = os.path.join(tmp, "contract.json")
    pp = os.path.join(tmp, "profile.json")
    with open(cp, "w", encoding="utf-8") as fh:
        json.dump(FIX_CONTRACT, fh, ensure_ascii=False)
    with open(pp, "w", encoding="utf-8") as fh:
        json.dump(FIX_PROFILE, fh, ensure_ascii=False)
    return cp, pp


def _run_fixture(mutate=None):
    tmp = tempfile.mkdtemp(prefix="gatefix-")
    cp, pp = _fixture_tree(tmp)
    if mutate:
        mutate(tmp, cp, pp)
    c = json.load(open(cp, encoding="utf-8"))
    p = json.load(open(pp, encoding="utf-8"))
    pages = collect_pages(tmp, p)
    R = judge({"site_root": tmp, "contract": c, "profile": p, "pages": pages})
    return R


def selftest():
    cases = []

    def case(name, cid, mutate, expect_fail=True, expect_pass=False):
        try:
            R = _run_fixture(mutate)
        except Exception as exc:  # noqa: BLE001
            cases.append((name, False, "异常：%s" % exc))
            return
        got = {r[0]: r[2] for r in R}
        if expect_pass:
            ok = all(r[2] for r in R)
        else:
            ok = (got.get(cid) is False) if expect_fail else bool(got.get(cid))
        cases.append((name, ok, ""))

    # 正向：夹具应 0 FAIL（证明判据不是恒真）
    case("正向夹具应 0 FAIL", None, None, expect_pass=True)

    def setc(fn):
        def _m(tmp, cp, pp):
            c = json.load(open(cp, encoding="utf-8"))
            fn(c)
            json.dump(c, open(cp, "w", encoding="utf-8"), ensure_ascii=False)
        return _m

    def setp(fn):
        def _m(tmp, cp, pp):
            p = json.load(open(pp, encoding="utf-8"))
            fn(p)
            json.dump(p, open(pp, "w", encoding="utf-8"), ensure_ascii=False)
        return _m

    def edit_page(name, fn):
        def _m(tmp, cp, pp):
            fp = os.path.join(tmp, name)
            s = open(fp, encoding="utf-8").read()
            open(fp, "w", encoding="utf-8").write(fn(s))
        return _m

    def add_page(name, text):
        def _m(tmp, cp, pp):
            fp = os.path.join(tmp, name)
            os.makedirs(os.path.dirname(fp), exist_ok=True)
            open(fp, "w", encoding="utf-8").write(text)
        return _m

    # ---- 逐判据负例（每条判据至少一个，且必须真的触发）
    case("G1 负例：扫描面 glob 未命中任何文件",
         "G1", setp(lambda p: p.__setitem__("page_families", [{"glob": "nope/*.html", "family": "default"}])))
    case("G1 负例：命中的页全部无 :root（令牌解析出 0 枚）",
         "G1", setp(lambda p: p.__setitem__("page_families", [{"glob": "notes.html", "family": "default"}])))
    case("G2 负例：同族内同名令牌两值",
         "G2", add_page("pages/b.html", FIX_PAGE.replace("--text:#e6e8ee", "--text:#123456")))
    case("G3 负例：盘上取值与值件派生不一致",
         "G3", edit_page("pages/a.html", lambda s: s.replace("--text:#e6e8ee", "--text:#123456")))
    case("G3 负例：源目标无 :root 块",
         "G3", edit_page("07-checkpoint/gen_common.py",
                         lambda s: s.replace(FIX_ROOT_BLOCK, "*{box-sizing:border-box;}")))
    case("G4 负例：多值不被任何族解释",
         "G4", edit_page("pages/a.html", lambda s: s.replace("--border-subtle:#2a2f3a", "--border-subtle:#abcdef")))
    case("G5 负例：--warn 出现两值（Q2-A 收敛被破坏）",
         "G5", edit_page("pages/a.html", lambda s: s.replace("--warn:#e8933b", "--warn:#e0c35e")))
    case("G5 负例：--danger 仍有声明（退役未落实）",
         "G5", edit_page("04-interactive/index.html",
                         lambda s: s.replace("--warn:#e8933b", "--warn:#e8933b;--danger:#e05563")))
    case("G6 负例：分档极性反转（强分隔取弱值）",
         "G6", edit_page("pages/a.html", lambda s: s.replace("--border:#6b7280", "--border:#111111")))
    case("G7 负例：正文对比度不达标（--text 压到近背景）",
         "G7", edit_page("pages/a.html", lambda s: s.replace("--text:#e6e8ee", "--text:#101010")))
    case("G7 负例：--err 对 --bg 不达标（旧值 #c0504d 回归）",
         "G7", edit_page("pages/a.html", lambda s: s.replace("--err:#ff6b6b", "--err:#c0504d")))
    case("G8 负例：站点级零引用未登记",
         "G8", setc(lambda c: c["dead_tokens"].__setitem__("site_level_zero_ref", [])))
    case("G8 负例：登记项其实有引用（登记过期）",
         "G8", edit_page("pages/c.html", lambda s: s.replace("var(--ok)", "var(--err)")))
    case("G8 负例：页级登记指向不存在的页（幽灵登记）",
         "G8", setc(lambda c: c["dead_tokens"]["page_level_unused"]["entries"].append(
             {"token": "--ok", "page": "ghost.html", "reason": "幽灵登记"})))
    case("G9 负例：gen-index.py 仍持令牌字面值块",
         "G9", edit_page("07-checkpoint/gen-index.py",
                         lambda s: s + '\nLITERAL = "' + FIX_ROOT_BLOCK + '"\n'))
    case("G9 负例：BASE_CSS 首个非空行不是 :root 块",
         "G9", edit_page("07-checkpoint/gen_common.py",
                         lambda s: s.replace('BASE_CSS = """\n', 'BASE_CSS = """\n/* 注释行在前 */\n')))
    case("G9 负例：profile 未声明单源不变量",
         "G9", setp(lambda p: p.pop("single_source_invariants")))
    case("G10 负例：盘上出现未声明令牌",
         "G10", edit_page("pages/a.html", lambda s: s.replace("--text:#e6e8ee", "--text:#e6e8ee;--ghost:#ffffff")))
    case("G11 负例：声明了不存在的目标",
         "G11", setp(lambda p: p["targets"].append({"path": "ghost.html", "mode": "root-block",
                                                    "family": "default"})))
    case("G11 负例：no_root_pages 声明项其实有 :root",
         "G11", edit_page("notes.html", lambda s: s.replace("<body>", "<style>" + FIX_ROOT_BLOCK + "</style><body>")))
    case("G11 负例：盘上 HTML 未被任何 glob 覆盖（会「默认通过」）",
         "G11", add_page("sub/orphan.html", FIX_PAGE))
    case("G11 负例：某页有 2 个 :root 块",
         "G11", edit_page("pages/a.html", lambda s: s.replace("</style>", "</style><style>" + FIX_ROOT_BLOCK + "</style>")))
    case("G11 负例：某页内联 <style> 块数 = 2",
         "G11", edit_page("pages/a.html", lambda s: s.replace("</style>", "</style><style>body{x:1}</style>")))

    ok = all(v for _, v, _ in cases)
    for name, res, note in cases:
        print("  [%s] %s%s" % ("PASS" if res else "FAIL", name, ("  ← " + note) if note else ""))
    print("\n=== gate_tokens.py 自检：%d 项，%d FAIL ===" % (len(cases), sum(1 for _, v, _ in cases if not v)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
