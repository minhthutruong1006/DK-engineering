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
  setInterval(function () {
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

  // Press: 드래그 스크롤 + 진행 바
  var track = document.querySelector('.press .track');
  var bar = document.querySelector('.press .scrollbar span');
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
