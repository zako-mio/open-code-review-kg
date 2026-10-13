#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gate_common.py — open-code-review-kg 五道站点门控的**共用薄工具**（批 H · 标准档新增）。

★ 只放「取页面 / 取样式表来源 / 从生成器源码里切 CSS 文本区」三件**无判据**的读取工具。
  ⛔ 不放任何判据、阈值或例外名单 —— 判据留在各门控里，使每道门控的判据对象可独立审阅
     （SH5 §4.0 第 1 条：判据对象必须与断言对象一致）。

★ 为什么需要 `css_regions()`：本站的样式表来源是**生成器源码**（Python 文件里的 CSS 常量），
  文件里同时夹着大量 JS。若整文件扫 `selector{`，JS 里 `{` 之前的代码会被当成选择器
  （实测踩到：`$('backbtn')` 一类被抽出）。本函数把「CSS 文本区」切出来，供各门控共用。
"""
import glob
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

SKIP_DIRS = {".git", "__pycache__", "vendor", "node_modules", "07-checkpoint",
             "08-source", "05-source"}
HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONTRACT = os.path.join(HERE, "vendor", "pipeline", "values", "open-code-review-kg.json")


class GateError(Exception):
    """护栏拒读（exit 3）——输入缺失/非法，⛔ 不静默降级为「跳过」。"""


def load_json(path, label):
    if not path or not os.path.isfile(path):
        raise GateError("%s 不存在：%s" % (label, path))
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception as exc:  # noqa: BLE001
        raise GateError("%s 非法 JSON：%s" % (label, exc))


def repo_html(site_root):
    """仓内 HTML 全集（口径与 evidence/h/tools/measure_station_baseline.py 一致）。"""
    out = []
    for dp, dn, fn in os.walk(site_root):
        dn[:] = sorted(d for d in dn if d not in SKIP_DIRS)
        for f in sorted(fn):
            if f.endswith(".html"):
                out.append(os.path.relpath(os.path.join(dp, f), site_root).replace(os.sep, "/"))
    return sorted(out)


def pages_of(site_root, profile):
    """按 profile.page_families 的 glob 采集页面 → [(rel, family)]。"""
    out = []
    for rule in profile.get("page_families") or []:
        for absp in sorted(glob.glob(os.path.join(site_root, rule["glob"]), recursive=True)):
            if os.path.isfile(absp):
                out.append((os.path.relpath(absp, site_root).replace(os.sep, "/"), rule["family"]))
    return out


def read_pages(site_root, profile):
    """→ {rel: 文本}。"""
    return {rel: open(os.path.join(site_root, rel), encoding="utf-8", errors="replace").read()
            for rel, _fam in pages_of(site_root, profile)}


def css_sources(site_root, contract, contract_path=DEFAULT_CONTRACT):
    """样式表来源 = 各族 profile.targets 里的 `.py` 生成器源码 → {rel: 文本}。

    ★ 为什么是生成器源码而不是产物：产物是内联样式（每页一份），源码是**唯一字面来源**；
      判「样式表里有没有 X」应当判来源，⛔ 不判 69 份副本（那是重复计量）。
    """
    prof_path = os.path.join(site_root, "build/profile.json")
    prof = load_json(prof_path, "profile") if os.path.isfile(prof_path) else None
    srcs = {}
    if prof:
        for t in prof.get("targets") or []:
            if str(t.get("path", "")).endswith(".py"):
                fp = os.path.join(site_root, t["path"])
                if os.path.isfile(fp):
                    srcs[t["path"]] = open(fp, encoding="utf-8", errors="replace").read()
    if not srcs:
        for _fam, spec in sorted((contract.get("families") or {}).items()):
            for t in (spec.get("targets") or []):
                if str(t).endswith(".py"):
                    fp = os.path.join(site_root, t)
                    if os.path.isfile(fp):
                        srcs[t] = open(fp, encoding="utf-8", errors="replace").read()
    return srcs


def css_regions(src):
    """从生成器源码里切出**CSS 文本区**（⛔ 不把 JS/Python 代码当样式表）。

    口径：① 优先取三引号字符串字面量里同时含 `{` 与 `:` 的段（= CSS 常量体）；
          ② 若一个都没有，退化为取 `<style>…</style>` 段；③ 再没有则返回空。
    """
    out = []
    for pat in (r'"""((?:[^"\\]|\\.|"(?!""))*)"""', r"'''((?:[^'\\]|\\.|'(?!''))*)'''"):
        for m in re.finditer(pat, src, re.S):
            body = m.group(1)
            if "{" in body and ":" in body:
                out.append(body)
    if not out:
        out = [m.group(1) for m in re.finditer(r"<style\b[^>]*>(.*?)</style>", src, re.I | re.S)]
    return out


def css_text(src):
    """一个来源文件的全部 CSS 文本（跨区拼接；用于「样式表里有没有 X」这类存在性判据）。"""
    return "\n".join(css_regions(src))
