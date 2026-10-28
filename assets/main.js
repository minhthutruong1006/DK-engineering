(function () {
  var header = document.getElementById('header');
  var btnTop = document.querySelector('.btnTop');

  // 헤더: 스크롤 시 흰 배경, 내릴 때 숨기고 올릴 때 표시
  var lastY = 0;
  function onScroll() {
    var y = window.scrollY;
    header.classList.toggle('fix', y > 80);
    header.classList.toggle('hide', y > lastY && y > 400);
    btnTop.classList.toggle('show', y > 600);
    lastY = y;
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
  btnTop.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: 'smooth' }); });

  // 메인 비주얼 슬라이드(페이드)
  var slides = document.querySelectorAll('.visual .slide');
  var cur = 0;
  if (slides.length > 1) setInterval(function () {
    slides[cur].classList.remove('on');
    cur = (cur + 1) % slides.length;
    slides[cur].classList.add('on');
  }, 5000);

  // 스크롤 등장 애니메이션
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (e.isIntersecting) { e.target.classList.add('on'); io.unobserve(e.target); }
    });
  }, { threshold: 0.15 });
  document.querySelectorAll('.ani').forEach(function (el) { io.observe(el); });

  // 전체메뉴: PC 메뉴를 그대로 복사해 구성
  var allmenu = document.querySelector('.allmenu');
  var depth1 = allmenu.querySelector('.depth1');
  var depth2 = allmenu.querySelector('.depth2');
  document.querySelectorAll('.pcNav > ul > li').forEach(function (li, i) {
    var item = document.createElement('li');
    item.innerHTML = '<a>' + li.querySelector('a').textContent + '</a>';
    depth1.appendChild(item);
    var sub = li.querySelector('ul').cloneNode(true);
    depth2.appendChild(sub);
    function act() {
      depth1.querySelectorAll('li').forEach(function (n) { n.classList.remove('act'); });
      depth2.querySelectorAll('ul').forEach(function (n) { n.classList.remove('act'); });
      item.classList.add('act');
      sub.classList.add('act');
    }
    item.addEventListener('mouseenter', act);
    item.addEventListener('click', act);
    if (i === 0) act();
  });
  function toggleMenu(open) {
    allmenu.classList.toggle('open', open);
    allmenu.setAttribute('aria-hidden', !open);
    document.body.style.overflow = open ? 'hidden' : '';
  }
  document.querySelector('.btnMenu').addEventListener('click', function () { toggleMenu(true); });
  allmenu.querySelector('.btnClose').addEventListener('click', function () { toggleMenu(false); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape') toggleMenu(false); });

  // 연혁: 화면 가운데를 지나는 연도에 맞춰 왼쪽 시기·사진과 가운데 진행선을 바꿈
  var tl = document.querySelector('.hTimeline');
  if (tl) {
    var eras = JSON.parse(tl.getAttribute('data-eras'));
    var hYears = tl.querySelectorAll('.hYear');
    var thumbs = tl.querySelectorAll('.hThumb img');
    var from = tl.querySelector('.hRange .from'), to = tl.querySelector('.hRange .to'), cat = tl.querySelector('.hCat');
    var hBar = tl.querySelector('.hLine .bar');
    var lastEra = -1, WIPE = 360, firstOf = {};
    hYears.forEach(function (y) { var k = +y.getAttribute('data-img'); if (!(k in firstOf)) firstOf[k] = y; });
    function updateHistory() {
      var mid = window.innerHeight * 0.5, act = 0;
      hYears.forEach(function (y, i) { if (y.getBoundingClientRect().top < mid) act = i; });
      hYears.forEach(function (y, i) { y.classList.toggle('on', i === act); });
      var cur = hYears[act], era = +cur.getAttribute('data-era'), img = +cur.getAttribute('data-img');
      // 사진: 해당 사진의 첫 연도가 화면 가운데에 오기 직전 구간(WIPE px) 동안 스크롤만큼 아래에서 위로 덮음
      thumbs.forEach(function (t, i) {
        if (i === 0) { t.style.clipPath = 'inset(0 0 0 0)'; return; }
        var first = firstOf[i];
        var f = first ? Math.min(Math.max((mid - (first.getBoundingClientRect().top - WIPE)) / WIPE, 0), 1) : 0;
        t.style.clipPath = 'inset(' + ((1 - f) * 100).toFixed(2) + '% 0 0 0)';
      });
      if (era !== lastEra) {
        lastEra = era;
        from.textContent = eras[era][0]; to.textContent = eras[era][1]; cat.textContent = eras[era][2];
        tl.querySelector('.hLeft').classList.remove('swap'); void tl.offsetWidth; tl.querySelector('.hLeft').classList.add('swap');
      }
      var r = tl.querySelector('.hRight').getBoundingClientRect();
      var p = Math.min(Math.max((mid - r.top) / r.height, 0), 1);
      hBar.style.height = p * 100 + '%';
    }
    window.addEventListener('scroll', updateHistory, { passive: true });
    window.addEventListener('resize', updateHistory);
    updateHistory();
  }

  // 인증: 왼쪽 고정 사진 패널 + 오른쪽 목록, 화면 가운데 그룹에 맞춰 이름·앵커 변경
  var cf = document.querySelector('.certFlow');
  if (cf) {
    var cBg = cf.querySelector('.cfBg'), cDark = cf.querySelector('.cfDark'), cCenter = cf.querySelector('.cfCenter');
    var cBlock = cf.querySelector('.cfBlock'), cCont = cf.querySelector('.cfContents');
    var lerp = function (a, b, t) { return a + (b - a) * t; };
    var cName = cf.querySelector('.cfName');
    var cNames = JSON.parse(cName.getAttribute('data-names'));
    var cPanels = cf.querySelectorAll('.cfPanel'), cAnch = cf.querySelectorAll('.cfAnchors a');
    var cImg = cBg.querySelector('img'), cAct = 0, cItems = cf.querySelectorAll('.cfEng, .cfTitle, .cfPanel li');
    cItems.forEach(function (el) { el.classList.add('cfRv'); });
    // saltlux처럼 관성 스크롤(Lenis)로 부드럽게
    var lenis = window.Lenis && window.innerWidth > 1024 && matchMedia('(pointer: fine)').matches ? new Lenis({ duration: 1.1 }) : null;
    if (lenis) (function raf(t) { lenis.raf(t); requestAnimationFrame(raf); })(performance.now());
    cAnch.forEach(function (a) {
      a.addEventListener('click', function (ev) {
        var el = document.querySelector(a.getAttribute('href'));
        if (!el) return; ev.preventDefault();
        var off = -(window.innerHeight - el.offsetHeight) / 2;
        if (lenis) lenis.scrollTo(el, { offset: off, duration: 1.2 }); else window.scrollTo({ top: el.getBoundingClientRect().top + window.scrollY + off, behavior: 'smooth' });
      });
    });
    function setGroup(i) {
      if (i === cAct) return; cAct = i;
      cName.style.opacity = 0;
      setTimeout(function () { cName.textContent = cNames[i]; cName.style.opacity = 1; }, 250);
      cAnch.forEach(function (a, k) { a.classList.toggle('on', k === i); });
    }
    function updateCert() {
      var vw = window.innerWidth, vh = window.innerHeight, mid = vh * 0.5;
      var act = 0;
      cPanels.forEach(function (p, i) { if (p.getBoundingClientRect().top < mid) act = i; });
      setGroup(act);
      // saltlux처럼: 처음엔 넓은 사진 → 스크롤하면 왼쪽(45%)으로 줄어들고 오른쪽(45%)에 내용
      if (vw > 1024) {
        var cr = cf.getBoundingClientRect(), W = cr.width;
        var H = Math.min(vh * 0.7, 640);
        var t = Math.min(Math.max(-cr.top / vh, 0), 1);
        var e = t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
        var w0 = Math.min(vw * 0.8, 1440), x0 = (vw - w0) / 2 - cr.left;
        cBg.style.left = lerp(x0, 0, e) + 'px';
        cBg.style.width = lerp(w0, W * 0.45, e) + 'px';
        cBg.style.height = lerp(vh * 0.8, H, e) + 'px';
        cBg.style.top = lerp(vh * 0.1, (vh - H) / 2, e) + 'px';
        cBg.style.borderRadius = lerp(30, 26, e) + 'px';
        cImg.style.transform = 'scale(' + lerp(1, 1.28, e).toFixed(4) + ')';
        // 넓은 상태에서는 화면 비율과 상관없이 인증서 선반 전체(원본 y 550px 중심)가 가운데 오도록
        var bw = w0, bh = vh * 0.8, sc = Math.max(bw / 1195, bh / 1689);
        var p0 = Math.min(Math.max((550 * sc - bh / 2) / (1689 * sc - bh) * 100, 0), 100);
        cImg.style.objectPosition = '50% ' + lerp(p0, 26, e).toFixed(2) + '%';
        cDark.style.opacity = lerp(.2, .5, e);
        cCenter.style.opacity = Math.max(1 - e * 2.5, 0);
        cBlock.style.opacity = Math.min(Math.max((e - .6) / .4, 0), 1);
        cCont.style.opacity = Math.min(Math.max((e - .7) / .3, 0), 1);
      } else {
        ['left', 'width', 'height', 'top', 'borderRadius'].forEach(function (k) { cBg.style[k] = ''; });
        cDark.style.opacity = cCenter.style.opacity = cBlock.style.opacity = cCont.style.opacity = cImg.style.transform = cImg.style.objectPosition = '';
      }
      // 오른쪽 항목은 화면에 들어오면 하나씩 등장
      var k = 0;
      cItems.forEach(function (el) {
        if (!el.classList.contains('on') && el.getBoundingClientRect().top < vh * 0.88) {
          el.style.transitionDelay = (k++ * 0.08) + 's, ' + ((k - 1) * 0.08) + 's, 0s';
          el.classList.add('on');
        }
      });
    }
    window.addEventListener('scroll', updateCert, { passive: true });
    window.addEventListener('resize', updateCert);
    updateCert();
  }

  // Press: 드래그 스크롤 + 진행 바
  var track = document.querySelector('.press .track');
  var bar = document.querySelector('.press .scrollbar span');
  if (!track) return;
  function updateBar() {
    var max = track.scrollWidth - track.clientWidth;
    var ratio = track.clientWidth / track.scrollWidth;
    bar.style.width = Math.min(ratio, 1) * 100 + '%';
    bar.style.left = (max > 0 ? track.scrollLeft / max : 0) * (100 - ratio * 100) + '%';
  }
  track.addEventListener('scroll', updateBar, { passive: true });
  window.addEventListener('resize', updateBar);
  updateBar();
  var down = false, startX = 0, startLeft = 0, moved = false;
  track.addEventListener('mousedown', function (e) {
    down = true; moved = false; startX = e.pageX; startLeft = track.scrollLeft;
    track.style.scrollSnapType = 'none';
  });
  window.addEventListener('mouseup', function () { down = false; track.style.scrollSnapType = ''; });
  track.addEventListener('mousemove', function (e) {
    if (!down) return;
    if (Math.abs(e.pageX - startX) > 5) moved = true;
    track.scrollLeft = startLeft - (e.pageX - startX);
  });
  track.addEventListener('click', function (e) { if (moved) e.preventDefault(); }, true);
})();

/* Clients 그룹: 헤드라인 줄별 등장 + 카드가 덮을수록 헤드라인 흐려짐 */
(function () {
  var g = document.querySelector('.clGroup');
  if (!g) return;
  var head = g.querySelector('.clSticky');
  var io = new IntersectionObserver(function (es) {
    es.forEach(function (e) { if (e.isIntersecting) { g.classList.add('on'); io.disconnect(); } });
  }, { threshold: .35 });
  io.observe(head);
  function dim() {
    var r = g.getBoundingClientRect(), vh = window.innerHeight;
    var p = Math.min(1, Math.max(0, (-r.top - vh * .15) / (vh * .7)));
    head.style.opacity = 1 - p * .62;
  }
  window.addEventListener('scroll', dim, { passive: true });
  window.addEventListener('resize', dim);
  dim();
})();
