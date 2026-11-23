
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
