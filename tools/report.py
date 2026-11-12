"""Turn a JUnit XML into a one-page HTML report + a manual-effort estimate.

usage: python tools/report.py reports/junit.xml reports/report.html
Tune MANUAL_MINUTES_PER_CASE to your own measured average.
"""
import sys
import xml.etree.ElementTree as ET
from html import escape

MANUAL_MINUTES_PER_CASE = 2.0  # time to verify one permission cell by hand


def main(junit, out):
    root = ET.parse(junit).getroot()
    cases = list(root.iter("testcase"))
    failed = []
    for c in cases:
        f = c.find("failure")
        if f is not None:
            failed.append((c.get("classname", ""), c.get("name", ""), f.get("message", "")))
    total, nfail = len(cases), len(failed)
    runtime = sum(float(c.get("time", 0)) for c in cases)
    manual_min = total * MANUAL_MINUTES_PER_CASE

    rows = "".join(
        f"<tr><td>{escape(n)}</td><td>{escape(m[:160])}</td></tr>" for _, n, m in failed
    ) or "<tr><td colspan=2>No failures</td></tr>"
    status = "PASS" if nfail == 0 else "FAIL"
    html = f"""<!doctype html><meta charset=utf-8><title>RBAC Report</title>
<style>body{{font:15px system-ui;max-width:820px;margin:2rem auto;padding:0 1rem}}
.{status}{{color:{'#0a7' if nfail==0 else '#c22'}}}td,th{{border-bottom:1px solid #ddd;padding:6px;text-align:left}}
.k{{display:flex;gap:2rem;margin:1rem 0}}.k b{{font-size:1.6rem;display:block}}</style>
<h1>RBAC / Sharing regression: <span class={status}>{status}</span></h1>
<div class=k><div><b>{total}</b>checks</div><div><b>{nfail}</b>failed</div>
<div><b>{runtime:.2f}s</b>automated</div>
<div><b>~{manual_min/60:.1f}h</b>manual equivalent</div></div>
<h2>Failures</h2><table><tr><th>Test</th><th>Reason</th></tr>{rows}</table>"""
    open(out, "w").write(html)
    print(f"{status}: {total} checks, {nfail} failed, {runtime:.2f}s vs ~{manual_min/60:.1f}h manual")
    return 1 if nfail else 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:3]))
