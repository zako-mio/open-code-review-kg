#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check_reachability.py — open-code-review-kg 的**逐页可达性验收件**（批 H · 标准档新增）。

★ 为什么需要它：方案 §7 **判据 7**（「68 页重生成后逐页 `curl` 断言 HTML 200 且内联 `<style>`
  块数 = 1」）在方案里**没有对应命令**（§7 只给了首页与 404 两条 curl）⇒ 本件是新增实现。

用法：
    # 本地口径（本机可跑；起一个只读静态服务，逐页 GET）
    python3 check_reachability.py --site-root . --out reachability.json
    # 推送后口径（对 GitHub Pages 跑；★ 本步⛔ 未推送，故本轮只留命令与本地留痕）
    python3 check_reachability.py --base-url https://zako-mio.github.io/open-code-review-kg --out reachability-live.json
    python3 check_reachability.py --selftest

判据（2 条，均 fail-closed）：
    V1 每页 HTTP 200（非 200 即 FAIL；空集守卫：扫描面 0 页即 FAIL，⛔ 不返回「0 命中」）
    V2 每页内联 `<style>` 块数恰为 1（形态 2「内联单源」的可机检形态）

★ 前置条件校验（SH5 §4.0 第 3 条）：**非 200 的页不参与 V2 判定**——把 404 页当正常页量
  正是批 B1 的 F3 教训（假证据）。本件对非 200 页只报 V1 FAIL 并注明「测量值不可用」。

退出码：0 全过 / 1 有 FAIL（含空集）/ 2 输入错误
"""
import argparse
import functools
import glob
import http.server
import json
import os
import re
import socketserver
import sys
import tempfile
import threading
import urllib.error
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

SKIP_DIRS = {".git", "__pycache__", "vendor", "node_modules", "07-checkpoint", "08-source", "05-source"}
STYLE_RE = re.compile(r"<style\b", re.I)
NON200_NOTE = "非 200 ⇒ 测量值不可用（⛔ 不得当作正常页量）"


def pages_of(site_root):
    out = []
    for dp, dn, fn in os.walk(site_root):
        dn[:] = sorted(d for d in dn if d not in SKIP_DIRS)
        for f in sorted(fn):
            if f.endswith(".html"):
                out.append(os.path.relpath(os.path.join(dp, f), site_root).replace(os.sep, "/"))
    return sorted(out)


class _Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):  # noqa: D102
        pass


def serve(site_root):
    """起一个只读静态服务（线程版），返回 (base_url, shutdown_fn)。"""
    handler = functools.partial(_Quiet, directory=site_root)

    class S(socketserver.ThreadingTCPServer):
        allow_reuse_address = True
        daemon_threads = True

    srv = S(("127.0.0.1", 0), handler)
    port = srv.server_address[1]
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    return "http://127.0.0.1:%d" % port, srv.shutdown


def fetch(url):
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception:  # noqa: BLE001
        return 0, ""


def check(pages, base_url):
    rows, fail = [], []
    for rel in pages:
        url = "%s/%s" % (base_url.rstrip("/"), rel)
        code, body = fetch(url)
        row = {"page": rel, "url": url, "status": code, "style_blocks": None}
        if code != 200:
            row["note"] = NON200_NOTE
            fail.append("V1 %s → HTTP %s（%s）" % (rel, code, NON200_NOTE))
        else:
            n = len(STYLE_RE.findall(body))
            row["style_blocks"] = n
            if n != 1:
                fail.append("V2 %s → 内联 <style> 块数 = %d（期望恰 1）" % (rel, n))
        rows.append(row)
    return rows, fail


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--site-root", default=".")
    ap.add_argument("--base-url", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()

    shutdown = None
    if a.base_url:
        base_url = a.base_url
        site_root = os.path.abspath(a.site_root)
    else:
        site_root = os.path.abspath(a.site_root)
        if not os.path.isdir(site_root):
            print("输入错误：--site-root 不存在：%s" % site_root)
            return 2
        base_url, shutdown = serve(site_root)

    try:
        pages = pages_of(site_root)
        if not pages:
            print("FAIL 空集守卫：扫描面 0 个 HTML ⇒ ⛔ 不返回「0 命中」")
            return 1
        print("扫描面 %d 页；base_url=%s" % (len(pages), base_url))
        rows, fail = check(pages, base_url)
    finally:
        if shutdown:
            shutdown()

    n200 = sum(1 for r in rows if r["status"] == 200)
    n_style_ok = sum(1 for r in rows if r["style_blocks"] == 1)
    print("  V1 HTTP 200：%d/%d" % (n200, len(rows)))
    print("  V2 内联 <style> 恰 1 块：%d/%d（★ 只在 200 的页上判）" % (n_style_ok, n200))
    for f in fail[:20]:
        print("  FAIL %s" % f)
    if len(fail) > 20:
        print("  … 另有 %d 条 FAIL" % (len(fail) - 20))
    print("\n=== 逐页可达性：%d 页，%d FAIL ===" % (len(rows), len(fail)))

    if a.out:
        doc = {"generated_by": "check_reachability.py（批 H · 方案 §7 判据 7 的新增实现）",
               "base_url_kind": "live" if a.base_url else "local-static-server",
               "page_count": len(rows), "http_200": n200, "style_blocks_ok": n_style_ok,
               "fail_count": len(fail), "fails": fail,
               "note": "★ base_url 里的主机与端口是**临时**的（本地服务每次端口不同）⇒ 本件不作为确定性入库件；"
                       "入库的确定性件是 gate-report.json。",
               "rows": [{"page": r["page"], "status": r["status"], "style_blocks": r["style_blocks"]}
                        for r in rows]}
        with open(a.out, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
        print("已写 %s" % a.out)
    return 0 if not fail else 1


# --------------------------------------------------------------------------- selftest
GOOD = '<!DOCTYPE html><html><head><style>body{x:1}</style></head><body>hi</body></html>\n'


def selftest():
    import shutil
    cases = []

    def case(name, build, expect_fail, pages_fn=None, expect_pages=1):
        tmp = tempfile.mkdtemp(prefix="reach-")
        try:
            build(tmp)
            base, shutdown = serve(tmp)
            try:
                pages = pages_fn(tmp) if pages_fn else pages_of(tmp)
                rows, fail = check(pages, base)
            finally:
                shutdown()
            got_fail = bool(fail)
            ok = (got_fail == expect_fail) and (len(rows) == expect_pages)
            note = "" if ok else "rows=%d fail=%s" % (len(rows), fail[:2])
        except Exception as exc:  # noqa: BLE001
            ok, note = False, "异常：%s" % exc
        cases.append((name, ok, note))
        shutil.rmtree(tmp, ignore_errors=True)

    case("正向：1 页 200 且 <style> 恰 1 块 ⇒ 0 FAIL",
         lambda t: open(os.path.join(t, "a.html"), "w").write(GOOD), expect_fail=False)
    case("V1 负例：扫描面里含一个不存在的页 ⇒ HTTP 404（且测量值标注不可用）",
         lambda t: open(os.path.join(t, "a.html"), "w").write(GOOD), expect_fail=True,
         pages_fn=lambda t: ["a.html", "missing.html"], expect_pages=2)
    case("V2 负例：某页 <style> 块数 = 2",
         lambda t: open(os.path.join(t, "a.html"), "w").write(
             '<!DOCTYPE html><html><head><style>body{x:1}</style><style>p{y:2}</style></head>'
             '<body>hi</body></html>\n'), expect_fail=True)
    case("V2 负例：某页 <style> 块数 = 0",
         lambda t: open(os.path.join(t, "a.html"), "w").write(
             "<!DOCTYPE html><html><head></head><body>hi</body></html>\n"), expect_fail=True)
    case("★ 假阳样本：vendor/ 下的 HTML 不计入扫描面（避免把第三方库当页面）",
         lambda t: (open(os.path.join(t, "a.html"), "w").write(GOOD),
                    os.makedirs(os.path.join(t, "vendor"), exist_ok=True),
                    open(os.path.join(t, "vendor/lib.html"), "w").write("<html></html>")),
         expect_fail=False, expect_pages=1)
    case("★ 假阳样本：07-checkpoint/ 下的 HTML 不计入扫描面",
         lambda t: (open(os.path.join(t, "a.html"), "w").write(GOOD),
                    os.makedirs(os.path.join(t, "07-checkpoint"), exist_ok=True),
                    open(os.path.join(t, "07-checkpoint/tpl.html"), "w").write("<html></html>")),
         expect_fail=False, expect_pages=1)

    ok = all(v for _, v, _ in cases)
    for name, res, note in cases:
        print("  [%s] %s%s" % ("PASS" if res else "FAIL", name, ("  ← " + note) if note else ""))
    print("\n=== check_reachability.py 自检：%d 项，%d FAIL ===" % (len(cases), sum(1 for _, v, _ in cases if not v)))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
