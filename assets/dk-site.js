// 관리자에서 등록한 실적·소식·보도자료를 페이지에 붙이고, 문의 폼을 서버로 보낸다. (dk-api.js 다음에 로드)
(function () {
  if (!window.DK) return;
  var esc = DK.esc;
  function byDesc(k) { return function (a, b) { return String(b[k] || '').localeCompare(String(a[k] || '')); }; }
  function quiet() {}

  // ---------- 관리자 SEO 수정값 (모든 페이지) ----------
  var page = location.pathname.split('/').pop() || 'index.html';
  DK.seo.list().then(function (a) {
    var o = (a || []).filter(function (x) { return x.page === page; })[0];
    if (!o) return;
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
    meta('property', 'og:image', o.og_image);
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

  // ---------- 소식 / 보도자료 (news.html, press.html) ----------
  var board = document.querySelector('.boardTable[data-board]');
  if (board) {
    var body = board.querySelector('tbody');
    DK.posts.list({ board: board.dataset.board }).then(function (a) {
      if (!a || !a.length) return;
      a.sort(byDesc('date'));
      body.innerHTML = a.map(function (x, i) {
        var link = x.link ? '<p class="link"><a href="' + esc(x.link) + '" target="_blank" rel="noopener">원문 보기</a></p>' : '';
        return '<tr class="bRow" tabindex="0"><td class="no">' + (a.length - i) + '</td><td class="tit">' + esc(x.title) + '</td><td>' + esc(x.author) + '</td><td class="date">' + esc(x.date) + '</td></tr>' +
          '<tr class="bView" hidden><td colspan="4"><div class="txt">' + esc(x.body).replace(/\n/g, '<br>') + '</div>' + link + '</td></tr>';
      }).join('');
    }, quiet);
    body.addEventListener('click', function (e) {
      var tr = e.target.closest('.bRow'); if (!tr) return;
      var v = tr.nextElementSibling; v.hidden = !v.hidden; tr.classList.toggle('open', !v.hidden);
    });
    body.addEventListener('keydown', function (e) { if (e.key === 'Enter' && e.target.classList.contains('bRow')) e.target.click(); });
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
