// 관리자에서 등록한 실적·소식·보도자료를 페이지에 붙이고, 문의 폼을 서버로 보낸다. (dk-api.js 다음에 로드)
(function () {
  if (!window.DK) return;
  var esc = DK.esc;
  function byDesc(k) { return function (a, b) { return String(b[k] || '').localeCompare(String(a[k] || '')); }; }
  function quiet() {}

  // ---------- 관리자 SEO 수정값 (모든 페이지) ----------
  var page = location.pathname.split('/').pop() || 'index.html';
  DK.seo.list().then(function (a) {
    var o = (a || []).filter(function (x) { return x.page === page; })[0] || {};
    var site = (a || []).filter(function (x) { return x.page === '_site'; })[0] || {};
    if (site.favicon) document.querySelectorAll('link[rel="icon"],link[rel="apple-touch-icon"]').forEach(function (l) { l.href = site.favicon; l.removeAttribute('type'); });
    meta('property', 'og:site_name', site.site_name);
    meta('property', 'og:image', o.og_image || site.og_image);
    function meta(attr, key, val) {
      if (!val) return;
      var m = document.head.querySelector('meta[' + attr + '="' + key + '"]');
      if (!m) { m = document.createElement('meta'); m.setAttribute(attr, key); document.head.appendChild(m); }
      m.setAttribute('content', val);
    }
    if (o.title) document.title = o.title;
    meta('name', 'description', o.description);
    meta('property', 'og:title', o.title);
    meta('property', 'og:description', o.description);
  }, quiet);

  // ---------- 분야별 실적 카드 (perf-*.html) ----------
  var grid = document.querySelector('.pdGrid[data-cat]');
  if (grid) {
    DK.perf.list({ cat: grid.dataset.cat }).then(function (a) {
      if (!a || !a.length) return;
      a.sort(byDesc('ym'));
      grid.insertAdjacentHTML('afterbegin', a.map(function (x) {
        return '<li><div class="top"><em></em></div><p>' + esc(x.title) + '</p></li>';
      }).join(''));
      grid.querySelectorAll('em').forEach(function (e, i) { e.textContent = (i < 9 ? '0' : '') + (i + 1); });
      var n = document.querySelector('.perfIntro .title p b');
      if (n) n.textContent = grid.children.length;
    }, quiet);
  }

  // ---------- 전체 실적 목록 (performance.html) ----------
  if (window.PERF && window.perfRender) {
    DK.perf.list().then(function (a) {
      if (!a || !a.length) return;
      a.forEach(function (x) {
        PERF.push([x.cat === 'design' ? '설계 & 엔지니어링' : '원자력 & 플랜트공사', x.field || '발전 플랜트', x.ym, x.title]);
      });
      PERF.sort(function (p, q) { return q[2].localeCompare(p[2]); });
      window.perfRender();
    }, quiet);
  }

  // ---------- 소식 / 보도자료 게시판 (news.html, press.html) ----------
  var board = document.querySelector('.boardTable[data-board]');
  if (board) {
    var PER = 10, all = [], view = [], pageNo = 1;
    var body = board.querySelector('tbody');
    board.insertAdjacentHTML('beforebegin', '<div class="bbsTop"><span class="bbsCount">전체 <b>0</b>건</span><form class="bbsSearch" role="search"><input type="search" placeholder="제목·내용 검색" aria-label="게시글 검색"><button>검색</button></form></div>');
    board.insertAdjacentHTML('afterend', '<div class="bbsPager" hidden></div><div class="postView" hidden></div>');
    var top = board.previousElementSibling, pager = board.nextElementSibling, pv = pager.nextElementSibling;
    var input = top.querySelector('input');
    function text(h) { var d = document.createElement('div'); d.innerHTML = DK.clean(h || ''); return d.textContent; }
    function size(n) { return n > 1048576 ? (n / 1048576).toFixed(1) + 'MB' : Math.max(1, Math.round((n || 0) / 1024)) + 'KB'; }

    function list() {
      var q = input.value.trim().toLowerCase();
      view = all.filter(function (x) { return !q || (x.title + ' ' + text(x.body)).toLowerCase().indexOf(q) >= 0; });
      top.querySelector('b').textContent = view.length;
      var pages = Math.max(1, Math.ceil(view.length / PER));
      pageNo = Math.min(pageNo, pages);
      var rows = view.slice((pageNo - 1) * PER, pageNo * PER);
      var left = view.filter(function (x) { return !x.pinned; }).length, nos = {};
      view.forEach(function (x) { if (!x.pinned) nos[x.id] = left--; }); // 공지 제외 최신글이 가장 큰 번호
      body.innerHTML = rows.length ? rows.map(function (x) {
        var no = x.pinned ? '<span class="pin">공지</span>' : nos[x.id];
        var clip = x.files && x.files.length ? '<i class="clip" title="첨부파일">첨부</i>' : '';
        return '<tr class="bRow' + (x.pinned ? ' pinned' : '') + '"><td class="no">' + no + '</td><td class="tit"><a href="?id=' + encodeURIComponent(x.id) + '" data-id="' + DK.esc(x.id) + '">' + DK.esc(x.title) + '</a>' + clip + '</td><td>' + DK.esc(x.author) + '</td><td class="date">' + DK.esc(x.date) + '</td></tr>';
      }).join('') : '<tr><td colspan="4" class="empty">' + (q ? '검색 결과가 없습니다.' : '등록된 게시물이 없습니다.') + '</td></tr>';
      pager.hidden = pages < 2;
      var h = '<button data-p="' + (pageNo - 1) + '"' + (pageNo < 2 ? ' disabled' : '') + ' aria-label="이전 페이지">‹</button>';
      for (var p = 1; p <= pages; p++) h += '<button data-p="' + p + '"' + (p === pageNo ? ' class="on" aria-current="page"' : '') + '>' + p + '</button>';
      pager.innerHTML = h + '<button data-p="' + (pageNo + 1) + '"' + (pageNo >= pages ? ' disabled' : '') + ' aria-label="다음 페이지">›</button>';
    }

    function show(id) {
      var seq = all.slice().sort(function (x, y) { return String(y.date || '').localeCompare(String(x.date || '')) || String(y.created_at || '').localeCompare(String(x.created_at || '')); });
      var i = -1;
      seq.forEach(function (x, k) { if (x.id === id) i = k; });
      var on = i >= 0;
      board.hidden = top.hidden = on; pv.hidden = !on; pager.hidden = on || pager.innerHTML.indexOf('data-p="2"') < 0;
      if (!on) return;
      var x = seq[i], prev = seq[i + 1], next = seq[i - 1];
      var files = (x.files || []).map(function (f) {
        return '<li><a href="' + DK.esc(f.url) + '" download="' + DK.esc(f.name) + '">' + DK.esc(f.name) + '</a><em>' + size(f.size) + '</em></li>';
      }).join('');
      function nav(lbl, y) {
        return '<li><span>' + lbl + '</span>' + (y ? '<a href="?id=' + encodeURIComponent(y.id) + '" data-id="' + DK.esc(y.id) + '">' + DK.esc(y.title) + '</a><em>' + DK.esc(y.date) + '</em>' : '<span class="none">' + lbl + '이 없습니다.</span>') + '</li>';
      }
      pv.innerHTML = '<div class="pvHead"><h3>' + DK.esc(x.title) + '</h3><div class="meta"><span>' + DK.esc(x.author) + '</span><span>' + DK.esc(x.date) + '</span></div></div>' +
        '<div class="pvBody">' + DK.clean(x.body) + '</div>' +
        (x.link ? '<p class="pvLink"><a href="' + DK.esc(x.link) + '" target="_blank" rel="noopener">원문 보기</a></p>' : '') +
        (files ? '<div class="pvFiles"><strong>첨부파일</strong><ul>' + files + '</ul></div>' : '') +
        '<ul class="pvNav">' + nav('다음글', next) + nav('이전글', prev) + '</ul>' +
        '<div class="pvBtns"><a href="' + location.pathname.split('/').pop() + '" class="btnList">목록</a></div>';
      document.title = x.title + ' | ' + document.title.split(' | ').slice(-1)[0];
    }

    function route() {
      var id = new URLSearchParams(location.search).get('id');
      show(id || '');
      if (id) { var t = document.querySelector('.subCon'); if (t) window.scrollTo(0, t.getBoundingClientRect().top + scrollY - 120); }
    }
    function go(id) { history.pushState(null, '', id ? '?id=' + encodeURIComponent(id) : location.pathname); route(); }

    DK.posts.list({ board: board.dataset.board }).then(function (a) {
      all = (a || []).slice().sort(function (x, y) {
        return (y.pinned ? 1 : 0) - (x.pinned ? 1 : 0) || String(y.date || '').localeCompare(String(x.date || '')) || String(y.created_at || '').localeCompare(String(x.created_at || ''));
      });
      list(); route();
    }, quiet);

    top.querySelector('form').addEventListener('submit', function (e) { e.preventDefault(); pageNo = 1; list(); });
    input.addEventListener('search', function () { pageNo = 1; list(); });
    pager.addEventListener('click', function (e) { var b = e.target.closest('button[data-p]'); if (!b || b.disabled) return; pageNo = +b.dataset.p; list(); board.scrollIntoView({ block: 'start' }); });
    document.addEventListener('click', function (e) {
      var a = e.target.closest('.boardTable a[data-id], .postView a[data-id], .postView .btnList');
      if (!a) return;
      e.preventDefault(); go(a.dataset.id || '');
    });
    window.addEventListener('popstate', route);
  }

  // ---------- 고객 문의 폼 (inquiry.html) ----------
  var form = document.querySelector('.inqForm');
  if (form) {
    form.addEventListener('submit', function (e) {
      if (e.defaultPrevented) return; // 자동등록방지 실패
      var d = {
        company: form.elements['업체명'].value.trim(),
        name: form.elements['담당자명'].value.trim(),
        email: form.elements['E-mail'].value.trim(),
        title: form.elements['제목'].value.trim(),
        content: form.elements['문의내용'].value.trim(),
        status: 0
      };
      if (DK.demo) { DK.inquiries.create(d); return; } // 미리보기: 기록만 남기고 기존 메일 전송 그대로
      e.preventDefault();
      var btn = form.querySelector('.sendBtn'); btn.disabled = true;
      DK.inquiries.create(d).then(function () {
        alert('문의가 접수되었습니다. 빠르게 답변드리겠습니다.');
        form.reset();
        var re = document.getElementById('capRe'); if (re) re.click();
      }, function () {
        alert('일시적인 오류로 접수하지 못했습니다. dk@dkenc.kr 또는 051-722-0855로 문의해 주세요.');
      }).then(function () { btn.disabled = false; });
    });
  }
})();
