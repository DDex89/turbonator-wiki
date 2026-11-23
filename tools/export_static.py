#!/usr/bin/env python3
"""
Export the Turbonator Tuning Wiki (DokuWiki) into a static HTML site.

The static site needs no PHP or server: open index.html from disk, or upload
the folder to any web host / GitHub Pages. Pages are rendered by the real
DokuWiki, so they look exactly like the live wiki.

Requirements: Python 3.8+, PHP 8.x on PATH (only for the export itself),
              pip install beautifulsoup4

Usage:
    python export_static.py --wiki ../wiki --out ../static

The wiki folder is not modified: the script works on a temporary copy.
"""
import argparse
import hashlib
import html
import json
import os
import posixpath
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request

try:
    from bs4 import BeautifulSoup, Comment
except ImportError:
    sys.exit("beautifulsoup4 is required: pip install beautifulsoup4")

# Namespaces that are not exported (scratch pages)
SKIP_NAMESPACES = ("playground",)

# Settings used only while exporting: no login, editing, history or sessions
EXPORT_CONF = r"""
// ---- static export settings (temporary copy only) ----
$conf['disableactions'] = 'register,login,logout,edit,source,revisions,recent,index,media,backlink,subscribe,profile,resendpwd,diff,export_raw,export_xhtml,export_pdf,sitemap,admin,check';
$conf['breadcrumbs'] = 0;
$conf['youarehere'] = 0;
$conf['canonical'] = 0;
$conf['dontlog'] = 'debug,deprecated,error';
"""

BANNER = (
    '<div class="static-archive-banner" style="background:#fcf8e3;border:1px solid #faebcc;'
    'color:#8a6d3b;padding:6px 12px;margin:0 0 12px 0;border-radius:4px;font-size:90%">'
    'Static archive of the <b>Turbonator Tuning Wiki</b> (BoostButton, 2014&ndash;2017). '
    'Read-only copy.</div>'
)


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def page_ids(wiki):
    root = os.path.join(wiki, "data", "pages")
    ids, skipped = [], []
    for dirpath, _, files in os.walk(root):
        for f in files:
            if not f.endswith(".txt"):
                continue
            rel = os.path.relpath(os.path.join(dirpath, f), root)[:-4]
            pid = rel.replace(os.sep, ":")
            if any(part in SKIP_NAMESPACES for part in pid.split(":")):
                skipped.append(pid)
                continue
            ids.append(pid)
    return sorted(ids), set(skipped)


def page_file(pid):
    """Static file name for a page id: all pages in one folder, ':' -> '.'"""
    return "index.html" if pid == "start" else pid.replace(":", ".") + ".html"


class Exporter:
    def __init__(self, base, out, ids):
        self.base = base.rstrip("/")
        self.out = out
        self.ids = set(ids)
        self.skipped = set()
        self.assets = {}  # server path+query -> local relative path

    def get(self, path):
        url = path if path.startswith("http") else self.base + path
        with urllib.request.urlopen(url, timeout=60) as r:
            return r.read()

    # ---- assets ---------------------------------------------------------
    def local_asset(self, url, from_css=False):
        """Download a server-relative asset once; return its path in the export."""
        p = urllib.parse.urlsplit(url)
        if p.scheme or p.netloc or not p.path.startswith("/"):
            return None
        key = p.path + ("?" + p.query if p.query else "")
        if key in self.assets:
            return self.assets[key]
        q = urllib.parse.parse_qs(p.query)
        if p.path.endswith("/lib/exe/fetch.php") and "media" in q and re.match(r"^https?://", q["media"][0]):
            return q["media"][0]  # external image: link to it directly
        if p.path.endswith("/lib/exe/fetch.php") and "media" in q:
            media = q["media"][0].lstrip(":")
            name, ext = posixpath.splitext(media.replace(":", "/"))
            suffix = ""
            if "w" in q or "h" in q:
                suffix = "_%sx%s" % (q.get("w", [""])[0], q.get("h", [""])[0])
            local = "_media/" + name + suffix + ext
        elif p.path.endswith("/lib/exe/css.php"):
            kind = q.get("s", ["screen"])[0]
            local = "_static/style_%s.css" % kind
        elif p.path.startswith("/lib/") and "/exe/" not in p.path:
            local = "_static" + p.path
        else:
            return None
        try:
            data = self.get(key)
        except Exception as e:  # missing image etc.
            print("  ! asset not available:", key, e)
            self.assets[key] = None
            return None
        dest = os.path.join(self.out, local)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        if local.endswith(".css"):
            data = self.fix_css(data.decode("utf-8", "replace"), local).encode("utf-8")
        with open(dest, "wb") as f:
            f.write(data)
        self.assets[key] = local
        return local

    def fix_css(self, css, css_local):
        css_dir = posixpath.dirname(css_local)
        # css.php output: url(/lib/...) absolute; template css files: relative urls
        def repl(m):
            raw = m.group(2).strip()
            if raw.startswith("data:") or raw.startswith("#") or re.match(r"^[a-z]+://", raw):
                return m.group(0)
            if raw.startswith("/"):
                server = raw
            else:  # relative to the css file's own server location
                server_dir = "/" + css_dir[len("_static/"):] if css_dir.startswith("_static/lib") else "/lib/exe"
                server = posixpath.normpath(posixpath.join(server_dir, raw.split("?")[0].split("#")[0]))
            local = self.local_asset(server)
            if not local:
                return m.group(0)
            return "url(%s%s%s)" % (m.group(1), posixpath.relpath(local, css_dir), m.group(1))
        return re.sub(r"url\(\s*(['\"]?)([^'\")]+)\1\s*\)", repl, css)

    # ---- pages ----------------------------------------------------------
    def link_target(self, href):
        """Map a wiki link to the static page, or None if it must be dropped."""
        p = urllib.parse.urlsplit(href)
        if p.netloc and href.startswith(self.base):
            p = urllib.parse.urlsplit(href[len(self.base):])
        elif p.scheme or p.netloc:
            return href  # external
        if not p.path.endswith("doku.php") and p.path not in ("/", ""):
            return False  # not a page link
        q = urllib.parse.parse_qs(p.query)
        if "do" in q or "rev" in q:
            return None
        if "id" not in q and p.fragment:
            return "#" + p.fragment  # same-page anchor (e.g. back to top)
        pid = q.get("id", ["start"])[0].lstrip(":")
        if pid in self.skipped:
            return "DROP"
        if pid not in self.ids:
            return None
        return page_file(pid) + ("#" + p.fragment if p.fragment else "")

    def process(self, pid, raw):
        soup = BeautifulSoup(raw, "html.parser")
        for c in soup.find_all(string=lambda t: isinstance(t, Comment)):
            c.extract()
        # head: drop server-only links and DokuWiki's own scripts
        for tag in soup.find_all("link"):
            rel = " ".join(tag.get("rel", []))
            if rel in ("search", "start", "contents", "manifest", "alternate", "canonical", "edit"):
                tag.decompose()
        for tag in soup.find_all("script"):
            src = tag.get("src", "")
            if "/lib/exe/" in src or (not src and ("JSINFO" in (tag.string or "") or "DOKU_BASE" in (tag.string or ""))):
                tag.decompose()
        for tag in soup.find_all("meta", attrs={"name": "generator"}):
            tag.decompose()
        # section edit buttons, background task runner
        for tag in soup.select(".secedit, form.btn_secedit, img[src*='taskrunner.php']"):
            tag.decompose()

        # search box -> static search page
        form = soup.find("form", id="dw__search")
        if form:
            new = BeautifulSoup(
                '<form action="search.html" method="get" class="navbar-form navbar-right" id="dw__search" role="search">'
                '<div class="form-group"><input type="text" name="q" class="form-control" placeholder="Search"></div></form>',
                "html.parser")
            form.replace_with(new)
        for tag in soup.select("#qsearch__out"):
            tag.decompose()

        # links
        for a in soup.find_all("a", href=True):
            href = a["href"]
            tgt = self.link_target(href)
            if tgt is False:
                p = urllib.parse.urlsplit(href)
                if p.path.endswith("/lib/exe/detail.php"):
                    q = urllib.parse.parse_qs(p.query)
                    local = self.local_asset("/lib/exe/fetch.php?media=" + urllib.parse.quote(q.get("media", [""])[0]))
                    if local:
                        a["href"] = local
                        continue
                local = self.local_asset(href)
                if local:
                    a["href"] = local
                    continue
                tgt = None
            if tgt == "DROP":
                a.decompose()
                continue
            if tgt is None:
                li = a.find_parent("li")
                if li is not None and len(li.find_all("a")) == 1 and li.get_text(strip=True) == a.get_text(strip=True):
                    li.decompose()
                elif href.startswith("#"):
                    continue
                else:
                    a.unwrap()
            else:
                a["href"] = tgt
                if "wikilink2" in a.get("class", []):
                    a["class"] = [c for c in a["class"] if c != "wikilink2"] + ["wikilink1"]
        # dropdowns left empty after removing actions
        for li in soup.select("li.dropdown"):
            if not [x for x in li.select("ul.dropdown-menu a") if not x.get("href", "").startswith("#")]:
                li.decompose()
        for sub in soup.find_all("sub"):
            if not sub.get_text(strip=True):
                sub.decompose()
        # images, css, scripts
        for tag, attr in (("img", "src"), ("link", "href"), ("script", "src")):
            for t in soup.find_all(tag):
                v = t.get(attr)
                if v:
                    local = self.local_asset(v)
                    if local:
                        t[attr] = local
        for t in soup.find_all("img"):
            t.attrs.pop("srcset", None)
        # navbar brand link
        for a in soup.select("a.navbar-brand"):
            if a.get("href", "").startswith("http://127.0.0.1") or a.get("href") == "/":
                a["href"] = "index.html"
        # archive banner on top of the page content
        page = soup.select_one("div.page")
        col = soup.select_one("#dokuwiki__content") or page
        if col:
            col.insert(0, BeautifulSoup(BANNER, "html.parser"))
        text = page.get_text(" ", strip=True) if page else ""
        h = page.find(["h1", "h2"]) if page else None
        title = h.get_text(" ", strip=True) if h else pid
        if soup.title:
            soup.title.string = title + " [Turbonator Tuning Wiki]"
        return soup, title, text

    def search_page(self, shell_soup):
        """Build search.html from the start page shell."""
        soup = BeautifulSoup(str(shell_soup), "html.parser")
        if soup.title:
            soup.title.string = "Search - Turbonator Tuning Wiki"
        page = soup.select_one("div.page")
        page.clear()
        page.append(BeautifulSoup(
            '<h1>Search</h1>'
            '<form action="search.html" method="get" style="margin-bottom:1em">'
            '<input type="text" name="q" id="static-q" class="form-control" style="max-width:420px;display:inline-block"> '
            '<button type="submit" class="btn btn-default">Search</button></form>'
            '<div id="static-results"></div>', "html.parser"))
        for t in soup.select("#dw_toc, .toc, #dw__toc, #dw__toc_wrapper, .dw-toc"):
            t.decompose()
        for li in soup.select("#dokuwiki__footer ul.doc li"):
            if li.find("bdi"):
                li.decompose()
        body = soup.body
        body.append(BeautifulSoup('<script src="_static/search_index.js"></script><script src="_static/search.js"></script>', "html.parser"))
        return soup


SEARCH_JS = r"""
(function () {
  var idx = window.SEARCH_INDEX || [];
  var params = new URLSearchParams(location.search);
  var q = (params.get('q') || '').trim();
  var box = document.getElementById('static-q');
  var out = document.getElementById('static-results');
  if (box) box.value = q;
  if (!q || !out) return;
  var terms = q.toLowerCase().split(/\s+/).filter(Boolean);
  function esc(s) { return s.replace(/[&<>"]/g, function (c) { return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]; }); }
  var res = [];
  idx.forEach(function (p) {
    var t = p.title.toLowerCase(), b = p.text.toLowerCase(), score = 0, ok = true;
    terms.forEach(function (w) {
      var n = b.split(w).length - 1, inT = t.indexOf(w) >= 0;
      if (!n && !inT) ok = false;
      score += n + (inT ? 20 : 0);
    });
    if (ok) res.push({p: p, s: score});
  });
  res.sort(function (a, b) { return b.s - a.s; });
  if (!res.length) { out.innerHTML = '<p>Nothing found for <b>' + esc(q) + '</b>.</p>'; return; }
  var html = '<style>.static-results mark{padding:0;background:#fff3a3}</style><p>' + res.length + ' page(s) found for <b>' + esc(q) + '</b>:</p><ul class="static-results">';
  res.forEach(function (r) {
    var b = r.p.text, i = b.toLowerCase().indexOf(terms[0]), snip = '';
    if (i >= 0) {
      var s = Math.max(0, i - 80);
      snip = (s ? '... ' : '') + esc(b.substr(s, 220)) + ' ...';
      terms.forEach(function (w) {
        snip = snip.replace(new RegExp('(' + w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'ig'), '<mark>$1</mark>');
      });
    }
    html += '<li style="margin-bottom:.8em"><a href="' + r.p.url + '"><b>' + esc(r.p.title) + '</b></a><br><small>' + snip + '</small></li>';
  });
  out.innerHTML = html + '</ul>';
})();
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--wiki", required=True, help="DokuWiki folder (the one with doku.php)")
    ap.add_argument("--out", required=True, help="output folder (recreated)")
    ap.add_argument("--php", default="php", help="PHP executable (default: php)")
    args = ap.parse_args()

    wiki = os.path.abspath(args.wiki)
    out = os.path.abspath(args.out)
    if not os.path.isfile(os.path.join(wiki, "doku.php")):
        sys.exit("not a DokuWiki folder: " + wiki)

    tmp = tempfile.mkdtemp(prefix="dwexport_")
    work = os.path.join(tmp, "wiki")
    print("copying wiki ...")
    shutil.copytree(wiki, work, ignore=shutil.ignore_patterns("cache", "index", "log", "tmp", "locks", "attic", "media_attic", ".git"))
    for d in ("cache", "index", "log", "tmp", "locks", "attic", "media_attic"):
        os.makedirs(os.path.join(work, "data", d), exist_ok=True)
    with open(os.path.join(work, "conf", "local.php"), "a", encoding="utf-8") as f:
        f.write(EXPORT_CONF)

    port = free_port()
    srv = subprocess.Popen([args.php, "-S", "127.0.0.1:%d" % port], cwd=work,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        base = "http://127.0.0.1:%d" % port
        for _ in range(50):
            try:
                urllib.request.urlopen(base + "/doku.php?id=start", timeout=5).read()
                break
            except Exception:
                time.sleep(0.2)
        else:
            sys.exit("PHP server did not start")

        if os.path.isdir(out):
            shutil.rmtree(out)
        os.makedirs(out)
        ids, skipped = page_ids(work)
        ex = Exporter(base, out, ids)
        ex.skipped = skipped
        index = []
        shell = None
        for pid in ids:
            print("page", pid)
            raw = ex.get("/doku.php?id=" + urllib.parse.quote(pid, safe=":")).decode("utf-8")
            soup, title, text = ex.process(pid, raw)
            if pid == "start":
                shell = soup
            with open(os.path.join(out, page_file(pid)), "w", encoding="utf-8") as f:
                f.write(str(soup))
            index.append({"url": page_file(pid), "title": re.sub(r"\s*\[.*\]$", "", title), "text": text})

        os.makedirs(os.path.join(out, "_static"), exist_ok=True)
        with open(os.path.join(out, "_static", "search_index.js"), "w", encoding="utf-8") as f:
            f.write("window.SEARCH_INDEX = " + json.dumps(index, ensure_ascii=False) + ";\n")
        with open(os.path.join(out, "_static", "search.js"), "w", encoding="utf-8") as f:
            f.write(SEARCH_JS)
        with open(os.path.join(out, "search.html"), "w", encoding="utf-8") as f:
            f.write(str(ex.search_page(shell)))
        with open(os.path.join(out, ".nojekyll"), "w") as f:
            f.write("")  # GitHub Pages: serve folders starting with "_"
        n_media = sum(1 for v in ex.assets.values() if v and v.startswith("_media/"))
        print("done: %d pages, %d media files -> %s" % (len(ids), n_media, out))
    finally:
        srv.terminate()
        srv.wait()
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
