"""Build the 2.1 site from REPORT_2.1.md and move the 1.0 site to an archive folder.

Run from the repository root:  python scripts/build_site.py

What it does (all local; nothing is pushed or published):
  docs/v1.0/            the 1.0 site exactly as published (index.html, study.css, caic-framework.html),
                        created once from the 1.0 files if it does not exist yet
  docs/index.html       the 2.1 report as a web page
  docs/archive.html     a page listing every version
  docs/report21.css     styles for the 2.1 pages
The converter handles only the Markdown this repository uses: headings, paragraphs, lists,
pipe tables, images, links, bold, italic, inline code and fenced code blocks.
"""
import html
import os
import re
import shutil

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
P = lambda *a: os.path.join(ROOT, *a)
REPO = "https://github.com/ketibak-ai/cincinnati-ai-labor-market"

# ---- 1. archive 1.0 once
v1 = P("docs", "v1.0")
if not os.path.exists(os.path.join(v1, "index.html")):
    os.makedirs(v1, exist_ok=True)
    src = open(P("docs", "index.html"), encoding="utf-8").read()
    assert "2.1" not in src[:3000], "docs/index.html is not the 1.0 page; refusing to archive it"
    banner = ('<div style="background:#fff4d6;border-bottom:1px solid #e0c97a;padding:10px 16px;font:14px/1.4 sans-serif">'
              'This is <strong>version 1.0</strong> (November 2026), kept as published. Several of its claims were corrected in '
              '<a href="../index.html">version 2.1</a>. <a href="../archive.html">All versions</a></div>')
    src = src.replace('href="Cincinnati_AI_Labor_Market_Dataset.xlsx"', 'href="../Cincinnati_AI_Labor_Market_Dataset.xlsx"')
    src = re.sub(r"(<body[^>]*>)", r"\1" + banner, src, count=1)
    open(os.path.join(v1, "index.html"), "w", encoding="utf-8").write(src)
    for f in ("study.css", "caic-framework.html"):
        shutil.copyfile(P("docs", f), os.path.join(v1, f))


# ---- 2. Markdown -> HTML
def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", lambda m: '<img src="%s" alt="%s">' % (m.group(2).replace("docs/", ""), m.group(1)), t)
    def link(m):
        url = m.group(2)
        if not url.startswith(("http", "#")) and not url.endswith((".html", ".png")):
            url = REPO + "/blob/main/" + url
        return '<a href="%s">%s</a>' % (url, m.group(1))
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"<em>\1</em>", t)
    return t


def slug(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


def convert(md):
    out, toc, lines, i = [], [], md.split("\n"), 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("```"):
            j = i + 1
            while j < len(lines) and not lines[j].startswith("```"):
                j += 1
            out.append("<pre><code>%s</code></pre>" % html.escape("\n".join(lines[i + 1:j]))); i = j + 1; continue
        if re.match(r"^---+\s*$", ln):
            out.append("<hr>"); i += 1; continue
        m = re.match(r"^(#{1,4})\s+(.*)$", ln)
        if m:
            lvl, txt = len(m.group(1)), m.group(2)
            if lvl == 2:
                toc.append((slug(txt), txt))
            out.append('<h%d id="%s">%s</h%d>' % (lvl, slug(txt), inline(txt), lvl)); i += 1; continue
        if ln.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|\s*$", lines[i + 1]):
            cells = lambda r: [c.strip() for c in r.strip().strip("|").split("|")]
            head = cells(ln); j = i + 2; rows = []
            while j < len(lines) and lines[j].startswith("|"):
                rows.append(cells(lines[j])); j += 1
            out.append('<div class="tw"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (
                "".join("<th>%s</th>" % inline(c) for c in head),
                "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % inline(c) for c in r) for r in rows)))
            i = j; continue
        m = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", ln)
        if m:
            ordered = m.group(2)[0].isdigit(); items = []; j = i
            while j < len(lines):
                mm = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", lines[j])
                if mm:
                    items.append(mm.group(3)); j += 1
                elif lines[j].startswith("  ") and lines[j].strip():
                    items[-1] += " " + lines[j].strip(); j += 1
                elif not lines[j].strip() and j + 1 < len(lines) and re.match(r"^(\s*)([-*]|\d+\.)\s+", lines[j + 1]):
                    j += 1
                else:
                    break
            tag = "ol" if ordered else "ul"
            out.append("<%s>%s</%s>" % (tag, "".join("<li>%s</li>" % inline(x) for x in items), tag)); i = j; continue
        if not ln.strip():
            i += 1; continue
        j = i; para = []
        while j < len(lines) and lines[j].strip() and not re.match(r"^(#{1,4}\s|\||```|---+\s*$|\s*([-*]|\d+\.)\s)", lines[j]):
            para.append(lines[j].strip()); j += 1
        txt = inline(" ".join(para))
        out.append(('<figure>%s</figure>' if txt.startswith("<img") else "<p>%s</p>") % txt); i = j
    return "\n".join(out), toc


CSS = """:root{--ink:#0b0b0b;--ink2:#52514e;--line:#e3e2dc;--bg:#f9f9f7;--card:#fcfcfb;--accent:#2a78d6}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.6 Georgia,'Source Serif 4',serif}
.top{background:var(--card);border-bottom:1px solid var(--line);padding:10px 20px;font:14px/1.4 system-ui,sans-serif;display:flex;gap:18px;flex-wrap:wrap}
.top a{color:var(--ink2);text-decoration:none}.top a:hover{color:var(--accent)}.top strong{color:var(--ink)}
main{max-width:860px;margin:0 auto;padding:28px 22px 80px}
h1{font:700 34px/1.2 system-ui,sans-serif;margin:18px 0 12px;text-wrap:balance}
h2{font:700 24px/1.25 system-ui,sans-serif;margin:46px 0 10px;padding-top:14px;border-top:2px solid var(--ink)}
h3{font:600 18.5px/1.3 system-ui,sans-serif;margin:28px 0 6px}h4{font:600 16px system-ui,sans-serif;margin:20px 0 4px}
p{margin:0 0 14px}a{color:var(--accent)}hr{border:0;border-top:1px solid var(--line);margin:30px 0}
ul,ol{margin:0 0 16px;padding-left:24px}li{margin:0 0 7px}
code{font:13.5px ui-monospace,Consolas,monospace;background:#efeee9;padding:1px 5px;border-radius:3px}
pre{background:#efeee9;padding:12px 14px;overflow-x:auto;border-radius:6px}pre code{background:none;padding:0}
.tw{overflow-x:auto;margin:6px 0 18px}table{border-collapse:collapse;width:100%;font:14.5px/1.45 system-ui,sans-serif}
th{text-align:left;border-bottom:2px solid var(--ink);padding:7px 10px 7px 0;vertical-align:bottom}
td{border-bottom:1px solid var(--line);padding:7px 10px 7px 0;vertical-align:top}
figure{margin:18px 0 22px}figure img{width:100%;height:auto;border:1px solid var(--line);border-radius:4px;display:block}
.toc{font:14.5px/1.5 system-ui,sans-serif;background:var(--card);border:1px solid var(--line);border-radius:6px;padding:12px 18px;margin:18px 0 8px;columns:2;column-gap:28px}
.toc a{display:block;color:var(--ink2);text-decoration:none;padding:2px 0}.toc a:hover{color:var(--accent)}
.draft{font:14px/1.45 system-ui,sans-serif;background:#fff4d6;border:1px solid #e0c97a;border-radius:6px;padding:10px 14px;margin:0 0 6px}
@media(max-width:640px){body{font-size:16px}h1{font-size:27px}.toc{columns:1}}
"""
PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>%(title)s</title><link rel="stylesheet" href="report21.css"></head><body>
<div class="top"><strong>Cincinnati AI Labor Market</strong><a href="index.html">Version 2.1</a><a href="archive.html">All versions</a>
<a href="%(repo)s">Data, code and tests</a></div>
<main>%(body)s</main></body></html>
"""
open(P("docs", "report21.css"), "w", encoding="utf-8").write(CSS)
md = open(P("REPORT_2.1.md"), encoding="utf-8").read()
body, toc = convert(md)
nav = '<nav class="toc">%s</nav>' % "".join('<a href="#%s">%s</a>' % t for t in toc)
body = body.replace("</h1>", "</h1>", 1)
k = body.index("<hr>")
body = body[:k] + nav + body[k:]
open(P("docs", "index.html"), "w", encoding="utf-8").write(PAGE % dict(title="Cincinnati AI Labor Market 2.1", repo=REPO, body=body))

arch = """<h1>All versions</h1>
<p>Each version stays reachable as it was published. Later versions correct earlier ones; the corrections are listed in the
<a href="%s/blob/main/AUDIT.md">audit log</a>.</p>
<div class="tw"><table><thead><tr><th>Version</th><th>Date</th><th>What it is</th></tr></thead><tbody>
<tr><td><a href="index.html">2.1</a> (<a href="https://claude.ai/artifact/HmTGiep1fUHFH2EgoZnysg">editable doc</a>, <a href="https://claude.ai/artifact/52uT1dxWPsjeDuVzvFSyJP">slides</a>)</td><td>17 November 2026</td><td>Re-tests 1.0 against peer metros with pre-registered tests. Adds AI awareness and participation,
a register of AI agents at large employers, capability measures and a full data-center section.</td></tr>
<tr><td>2.0</td><td>13 November 2026</td><td>Design stage only: a research design memo and pre-registration. Never published as a report.</td></tr>
<tr><td><a href="v1.0/index.html">1.0</a></td><td>November 2026</td><td>The first published study. Kept unchanged.
Its <a href="Cincinnati_AI_Labor_Market_Dataset.xlsx">dataset workbook</a> is also unchanged.</td></tr>
</tbody></table></div>""" % REPO
open(P("docs", "archive.html"), "w", encoding="utf-8").write(PAGE % dict(title="All versions - Cincinnati AI Labor Market", repo=REPO, body=arch))
print("docs/index.html", len(body), "chars |", len(toc), "sections | 1.0 archived at docs/v1.0/index.html:", os.path.exists(os.path.join(v1, "index.html")))
