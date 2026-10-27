# DK ENGINEERING 하위 페이지 4개 생성 (index.html 헤더·푸터 재사용)
import csv, json, re, html, os

ROOT = r'E:\keoc-clone'
SRC = r'C:\Users\ADMIN\Downloads\대경기술_지명원_분석'
idx = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()

head = idx[:idx.index('<body>')]
header = idx[idx.index('<!-- ============ HEADER'):idx.index('<!-- ============ VISUAL')]
footer = idx[idx.index('<!-- ============ FOOTER'):idx.index('</body>')]
# 하위 페이지에서는 메인 섹션 앵커를 index.html#… 로
header = re.sub(r'href="#', 'href="index.html#', header)
footer = re.sub(r'href="#"', 'href="index.html"', footer)

# 하위 페이지 그룹: 큰 비주얼의 영문 섹션명·문구·배경과 같은 그룹 탭
GROUPS = {
    'about': ('ABOUT', '전력산업의 글로벌 리더, 대경기술', 'dk/about_svis.jpg',
              [('ceo.html', 'CEO 인사'), ('company.html', '회사 개요'), ('history.html', '연혁'), ('organ.html', '사훈/조직도'),
               ('certification.html', '인증서'), ('clients.html', '주요 고객사'), ('ci.html', 'C.I. 소개')]),
    'business': ('BUSINESS', '원자력, 화력발전소 및 플랜트 전기/계장 분야 선도 업체', 'dk/business_svis.jpg',
                 [('biz-services.html', '수행 역무'), ('biz-nuclear.html', '원자력/발전'), ('biz-plant.html', '플랜트/해양모듈'),
                  ('biz-major.html', '주요 사업'), ('rnd.html', '국책과제')]),
    'performance': ('PERFORMANCE', '국내를 넘어 세계로 향하는 기술력', 'dk/performance_svis.jpg',
                    [('perf-design.html', '설계/엔지니어링'), ('perf-nuclear.html', '원자력 공사/설치'),
                     ('perf-plant.html', '플랜트 공사/제작'), ('performance.html', '전체 실적 목록')]),
    'news': ('NEWS', '대경기술의 새로운 소식을 전합니다', 'dk/business_nuclear_power.jpg',
             [('news.html', '대경기술 소식'), ('press.html', '보도자료')]),
    'contact': ('CONTACT', '전력산업의 든든한 파트너, 대경기술', 'dk/customer_svis.jpg',
                [('inquiry.html', '고객 문의'), ('location.html', '오시는 길')]),
}
PAGE_GROUP = {f: g for g, v in GROUPS.items() for f, _ in v[3]}
e = html.escape


def page(fname, title, desc, eng, h2, lead, bg, body):
    h = re.sub(r'<title>.*?</title>', f'<title>{title} | DK ENGINEERING 대경기술</title>', head)
    h = re.sub(r'<meta name="description" content=".*?">', f'<meta name="description" content="{e(desc)}">', h)
    g_eng, g_lead, g_bg, g_tabs = GROUPS[PAGE_GROUP[fname]]
    tabs = ''.join(f'<li><a href="{f}"{" class=\"on\"" if f == fname else ""}>{t}</a></li>' for f, t in g_tabs)
    out = f'''{h}<body class="sub">

{header}<section class="subHero">
  <div class="bg" style="background-image:url(assets/img/{g_bg})"></div>
  <div class="inner">
    <h2>{g_eng}</h2>
    <p>{g_lead}</p>
  </div>
  <span class="heroLine"></span>
  <div class="scrollDown"><span></span>SCROLL</div>
</section>
<div class="pageTitle">
  <div class="inner">
    <div class="loc"><a href="index.html">HOME</a><i></i><span>{g_eng}</span><i></i><span>{h2}</span></div>
    <h3>{h2}</h3>
    <p>{lead}</p>
    <ul class="pageTab">{tabs}</ul>
  </div>
</div>

<main class="subCon">
{body}
</main>

{footer}</body>
</html>
'''
    open(os.path.join(ROOT, fname), 'w', encoding='utf-8').write(out)
    print('wrote', fname)


# ---------- 1. 연혁 ----------
HISTORY = [
    ('2006.06', '대경기술 사업자 등록', ''),
    ('2006.06', '대경일렉트릭 설계팀 대경기술로 합병', ''),
    ('2006.06', '한국수력원자력㈜ 협력업체 등록', ''),
    ('2007.08', '전기공사업 등록', '제 부산-01181호'),
    ('2007.12', '한국수력원자력㈜ 유자격공급자 등록', '전기케이블 및 전기패널 공사 (안전성 등급 A)'),
    ('2009.09', '한국수력원자력㈜ 안전운영기여 감사패 수상', '울진 1,2호기'),
    ('2009.10', '한국수력원자력㈜ 유자격공급자 등록', '전기케이블 및 전기패널 공사 (안전성 등급 Q)'),
    ('2010.03', '전문설계업 1종 등록', '2010-6260000-85-12-00002'),
    ('2010.03', '전문감리업 등록', '2010-6260000-86-22-00002'),
    ('2010.05', 'ISO 9001:2008 인증', 'K101542.01'),
    ('2011.01', '한국전력공사 부산본부 전력산업발전기여 감사패 수상', ''),
    ('2011.03', '한국수력원자력㈜ 유자격공급자 등록', '가동원전 전기설비 설계 용역 (안전성 등급 A)'),
    ('2011.07', '한전KPS㈜ 협력업체 등록', '계측제어 Q등급 / 전기 공사(전국)'),
    ('2011.10', '무정전 공사 시공업체 등록', '제11-17호'),
    ('2012.09', '지중배전 전문회사 업체 등록', '제5500-2012-123'),
    ('2012.10', '대경기술주식회사 법인등기', ''),
    ('2012.12', '정보통신공사업 등록', '제510322호'),
    ('2012.12', '신재생에너지 설비 설치전문기업 신고', '2012-12-012360'),
    ('2013.01', '소방시설업 등록', '전문소방시설공사업 · 일반소방시설설계업(기계/전기)'),
    ('2013.04', '대경기술주식회사 사옥 신축 및 이전', ''),
    ('2013.07', '공장 등록', ''),
    ('2013.07', '기업부설연구소 설립', '2013113329'),
    ('2015.02', '기술혁신형 중소기업(INNO-BIZ) 확인', '제 R150206-00478호'),
    ('2015.03', 'KS Q ISO 45001:2018 · KS Q ISO 9001:2015 인증', 'SMS-15-30-3 / QMC-1592'),
    ('2015.03', '한국수력원자력㈜ 유자격공급자 등록', '가동원전 전기설비 설계 용역 (안전성 등급 Q)'),
    ('2016.01', '한국전기기술인협회 전기산업공로 감사패 수상', ''),
    ('2016.02', '한국전력공사 전력공급기여 감사패 수상', ''),
    ('2016.02', '한국수력원자력㈜ 유자격공급자 등록', '원자력발전소 조명설비 정비 공사 (안전성 등급 A)'),
    ('2017.05', '경영혁신형 중소기업(MAIN-BIZ) 확인', '제 R170203-01011호'),
    ('2017.06', '한국수력원자력㈜ 안전운영기여 감사패 수상', '고리 1호기'),
    ('2018.02', '산업통상자원부 장관 표창 수상', '전기공사업계 및 국가산업발전 기여'),
    ('2018.07', '㈜코센 자회사 편입', ''),
    ('2019.01', '신재생에너지(태양광) 주택지원사업', ''),
    ('2021.09', '기계·설비공사업 등록', ''),
    ('2021.09', '비계·구조물해체공사업 등록', ''),
    ('2023.12', '부산시장 원전해체육성 표창 수상', ''),
    ('2025.06', '산업·환경설비공사업 등록', ''),
    ('2025.09', '한국동서발전㈜ EWP 감사패 수상', '당진 1~4호기'),
    ('2026.09', '대통령 표창 수상', '과학기술진흥발전 공로'),
]
DK = json.load(open(os.path.join(ROOT, '_tools', 'dk_pages.json'), encoding='utf-8'))
HISTORY += [tuple(x) for x in DK['history_extra']]
years = {}
for d, t, s in sorted(HISTORY, key=lambda x: x[0]):
    years.setdefault(d[:4], []).append((d[5:], t, s))
rows = []
for y in sorted(years, reverse=True):
    lis = ''.join(
        f'<li class="{"award" if ("수상" in t) else ""}"><em>{m}</em><span>{e(t)}{f"<small>{e(s)}</small>" if s else ""}</span></li>'
        for m, t, s in years[y])
    rows.append(f'<div class="yearRow ani"><div class="year">{y}</div><ul>{lis}</ul></div>')
page('history.html', '연혁', '대경기술주식회사(DK ENGINEERING) 2006~2026 연혁: 한수원 유자격공급자 등록, 면허 확장, 기업부설연구소 설립, 대통령 표창.',
     'History', '연혁', '2006년 설립 이후 원자력·전력산업과 함께 걸어온 길입니다.', 'sub-history.jpg', f'''  <div class="title ani">
    <h2>History<span class="dot"></span></h2>
    <h3>신뢰를 쌓아온 20년</h3>
  </div>
  <div class="stats ani">
    <div><b>2006</b><span>사업 시작 · 한수원 협력업체 등록</span></div>
    <div><b>Q</b><span>한수원 유자격공급자 최고 등급</span></div>
    <div><b>2013</b><span>사옥 신축 · 기업부설연구소 설립</span></div>
    <div><b>2026</b><span>대통령 표창 (과학기술진흥발전)</span></div>
  </div>
  <div class="histPhotos ani">{''.join(f'<div class="photo" style="background-image:url(assets/img/dk/about_history0{i}.jpg)"></div>' for i in range(1, 7))}</div>
  <div class="history">
    {''.join(rows)}
  </div>''')

# ---------- 2. 실적 목록 ----------
perf = []
with open(os.path.join(SRC, '실적_목록.csv'), encoding='utf-8-sig') as f:
    for r in csv.DictReader(f):
        name = re.sub(r'\s*DK ENGINEERING\s*\d+\s*$', '', r['공사/용역명']).replace('Jardan', 'Jordan').replace('Diagonosis', 'Diagnosis').replace('Slury', 'Slurry')
        perf.append([r['사업구분'], r['분야'], r['연월'], name])
# 설계·공사 표가 따로 이어져 있으므로 연월 최신순으로 합침 (날짜 없는 행은 바로 앞 행 날짜를 따름)
last = ''
for p in perf:
    if re.match(r'\d{4}\.\d{2}', p[2]): last = p[2]
    else: p[2] = last
perf = [p for _, p in sorted(enumerate(perf), key=lambda x: (x[1][2], x[0]), reverse=True)]
cnt = lambda b, g: sum(1 for p in perf if p[0].startswith(b) and p[1] == g)
data = json.dumps(perf, ensure_ascii=False)
yrs = sorted({p[2][:4] for p in perf if p[2][:4].isdigit()}, reverse=True)
opts = ''.join(f'<option value="{y}">{y}</option>' for y in yrs)
page('performance.html', '실적 목록', f'대경기술 수행 실적 {len(perf)}건: 원자력·발전 플랜트 설계 엔지니어링과 공사, 일반건설 전기·소방 실적 전체 목록.',
     'Business Performance', '실적 목록', f'2006년부터 수행한 설계·공사 실적 {len(perf)}건을 모두 공개합니다.', 'sub-perf.jpg', f'''  <div class="title ani">
    <h2>Performance<span class="dot"></span></h2>
    <h3>설계부터 시공까지, {len(perf)}건의 수행 실적</h3>
  </div>
  <div class="stats ani">
    <div><b>{cnt('설계', '발전 플랜트')}</b><span>설계 · 발전 플랜트</span></div>
    <div><b>{cnt('설계', '일반건설')}</b><span>설계 · 일반건설</span></div>
    <div><b>{cnt('원자력', '발전 플랜트')}</b><span>공사 · 발전 플랜트</span></div>
    <div><b>{cnt('원자력', '일반건설')}</b><span>공사 · 일반건설</span></div>
  </div>
  <div class="filter">
    <div class="seg" id="fBiz"><button class="on" data-v="">전체</button><button data-v="설계">설계 &amp; 엔지니어링</button><button data-v="원자력">원자력 &amp; 플랜트공사</button></div>
    <div class="seg" id="fField"><button class="on" data-v="">전 분야</button><button data-v="발전 플랜트">발전 플랜트</button><button data-v="일반건설">일반건설</button></div>
    <select id="fYear"><option value="">전체 연도</option>{opts}</select>
    <input id="fQ" type="search" placeholder="공사명 검색 (예: 고리, MCC, 신한울)">
    <div class="count">검색 결과 <b id="fCount">0</b>건</div>
  </div>
  <table class="perfTable">
    <thead><tr><th>연월</th><th>구분</th><th>공사 / 용역명</th></tr></thead>
    <tbody id="perfBody"></tbody>
  </table>
  <div class="empty" id="perfEmpty" hidden>조건에 맞는 실적이 없습니다.</div>
<script>
var PERF = {data};
(function () {{
  var st = {{ biz: '', field: '', year: '', q: '' }};
  var body = document.getElementById('perfBody');
  function esc(s) {{ return s.replace(/[&<>]/g, function (c) {{ return {{ '&': '&amp;', '<': '&lt;', '>': '&gt;' }}[c]; }}); }}
  function render() {{
    var q = st.q.trim().toLowerCase(), last = '', out = [], n = 0;
    PERF.forEach(function (p) {{
      if (st.biz && p[0].indexOf(st.biz) !== 0) return;
      if (st.field && p[1] !== st.field) return;
      if (st.year && p[2].indexOf(st.year) !== 0) return;
      if (q && p[3].toLowerCase().indexOf(q) < 0) return;
      var y = p[2].slice(0, 4);
      if (y !== last) {{ out.push('<tr class="yr"><td colspan="3">' + y + '</td></tr>'); last = y; }}
      out.push('<tr><td class="m">' + p[2] + '</td><td class="g"><span class="tag' + (p[0].indexOf('설계') === 0 ? '' : ' c') + '">' +
        (p[0].indexOf('설계') === 0 ? '설계' : '공사') + '</span><span class="tag g">' + p[1] + '</span></td><td>' + esc(p[3]) + '</td></tr>');
      n++;
    }});
    body.innerHTML = out.join('');
    document.getElementById('fCount').textContent = n;
    document.getElementById('perfEmpty').hidden = n > 0;
  }}
  ['fBiz', 'fField'].forEach(function (id) {{
    var key = id === 'fBiz' ? 'biz' : 'field';
    document.getElementById(id).addEventListener('click', function (ev) {{
      var b = ev.target.closest('button'); if (!b) return;
      this.querySelectorAll('button').forEach(function (x) {{ x.classList.toggle('on', x === b); }});
      st[key] = b.dataset.v; render();
    }});
  }});
  document.getElementById('fYear').addEventListener('change', function () {{ st.year = this.value; render(); }});
  document.getElementById('fQ').addEventListener('input', function () {{ st.q = this.value; render(); }});
  render();
}})();
</script>''')

# ---------- 3. 국책과제 ----------
ORG = {'KAIA': '국토교통과학기술진흥원', 'KETEP': '한국에너지기술평가원', 'KHNP': '한국수력원자력', 'KITECH': '한국생산기술연구원',
       'TIPA': '중소기업기술정보진흥원', 'KAIF': '한국원자력산업협회', 'BTP': '부산테크노파크'}
rnd = []
with open(os.path.join(SRC, 'RnD_국책과제.csv'), encoding='utf-8-sig') as f:
    for r in csv.DictReader(f):
        t = re.sub(r"\s*\(원문 '[^']*'\)", '', r['과제명'])
        code = r['주관기관'].split('(')[0]
        sub = r['주관기관'][len(code):].strip('()') or ORG.get(code, '')
        rnd.append((code, sub, t, r['시작'], r['종료']))
rnd.sort(key=lambda x: x[3], reverse=True)
items = ''.join(
    f'<li class="ani{" ing" if end >= "2026.10.27" else ""}"><div class="org">{code}<small>{e(sub)}</small></div>'
    f'<div class="tit">{e(t)}</div><div class="date">{s} – {end}</div></li>' for code, sub, t, s, end in rnd)
page('rnd.html', '국책과제', f'대경기술 기업부설연구소 국책과제 {len(rnd)}건: 원전해체 레이저 제염, 방사성 폐기물 관리, 원전 제어모듈 국산화, SMR 테스트베드.',
     'R&amp;D Center', '국책과제', '2013년 설립한 기업부설연구소에서 원전해체와 원전 핵심 부품 국산화 기술을 개발합니다.', 'rnd.jpg', f'''  <div class="title ani">
    <h2>R&amp;D<span class="dot"></span></h2>
    <h3>국책과제 {len(rnd)}건, 원전 기술의 국산화를 이끕니다</h3>
    <p>원전해체(레이저 제염·플라즈마 절단·액체폐기물 처리), 방사성 폐기물 IoT·블록체인 관리, 원전 밸브·제어모듈 국산화, SMR 테스트베드까지 수행하고 있습니다.</p>
  </div>
  <div class="stats ani">
    <div><b>{len(rnd)}</b><span>국책과제 수행</span></div>
    <div><b>7</b><span>주관기관 (KETEP·TIPA·KHNP 등)</span></div>
    <div><b>10</b><span>등록 특허</span></div>
    <div><b>2013</b><span>기업부설연구소 설립</span></div>
  </div>
  <ul class="rndList">{items}</ul>''')

# ---------- 4. 인증·특허 ----------
LIC = ['전기공사업, 정보통신공사업, 기계설비공사업, 소방시설업(전문소방) 등록', '전문설계업, 전문감리업 등록',
       '비계·구조물해체공사업, 산업·환경설비공사업 등록', '무정전배전 공사 자격, 지중배전 전문회사 인증, 직접생산확인증명',
       '신재생에너지 설비·설치전문기업, 위생관리용역업, 엔지니어링사업자 신고', '해외건설업 신고, 근로자 파견허가, 통신판매·소프트웨어사업자 신고']
QUAL = ['ISO 9001:2015 품질경영시스템', 'KS Q ISO 45001:2018 안전보건경영시스템', 'INNO-BIZ · MAIN-BIZ 확인',
        '벤처기업 확인 · 기업부설연구소 인정', '가족친화기업 · 원전기업 인증', '에너지특화기업 지정']
NUC = ['한국수력원자력㈜ 전기케이블 및 전기패널 정비 용역 Q등급', '한국수력원자력㈜ 조명설비 정비 공사 A등급',
       '발전 5사(남동·남부·동서·서부·중부) 정비적격기업 인증', '한국전력기술㈜ 협력업체 약정 (원자력 전기설계·계측제어 / 플랜트 계측제어)']
PAT = [
    ('퓨즈 스위치 접지 장치 및 이를 갖는 퓨즈 타입 고장 구분 개폐기', '제10-1614022호', '등록'),
    ('지중선로 작업을 위한 비접촉 방식의 지중선로 신호패턴 감지장치 및 방법', '제10-1741471호', '등록'),
    ('다중 센서의 신뢰도 향상을 위한 통합적 교차 교정 장치 및 방법', '제10-1882384호', '등록'),
    ('커널회귀 모델을 통하여 시변신호를 검증하는 온라인 검증 장치 및 방법', '제10-1967524호', '등록'),
    ('복수개의 검출기를 이용한 대면적 방사능 표면오염 측정장치', '제10-2140038호', '등록'),
    ('원자력 시설 해체용 모니터링 장치', '제10-2158770호', '등록'),
    ('나이테 구조를 이용한 방사성 폐액 섬유필터장치', '제10-2301046호', '등록'),
    ('레이저 클래딩 열처리 시스템', '제10-2665725호', '등록'),
    ('블록체인 기반의 방사성 폐기물관리 방법 및 시스템', '제10-2849123호', '등록'),
    ('원격제어 가능한 방사성 금속폐기물 레이저 제염장치', '제10-2948160호', '등록'),
    ('바인더젯 방식의 3D프린트를 이용한 미로형 트림 제조 방법', '10-2024-0195608', '출원'),
    ('데이터 연속성 복원 기능을 갖는 방사성폐기물 용기 감시 장치 및 그 방법', '10-2024-0180436', '출원'),
    ('연속 방사능감시 기반의 이동식 방사성 액체 폐기물 처리시스템 및 그 운전방법', '10-2026-0180431', '출원'),
    ('방사선 계측노드의 설정 적용 검증 및 계측 데이터 설정 상태 연계 관리 시스템 및 방법', '10-2026-0180437', '출원'),
]
box = lambda eng, h, L: f'<div class="box ani"><div class="eng">{eng}</div><h4>{h}</h4><ul>{"".join(f"<li>{e(x)}</li>" for x in L)}</ul></div>'
prow = ''.join(f'<tr><td class="n">{i}</td><td>{e(t)}</td><td class="no">{n}</td><td class="st"><span class="tag{"" if s == "등록" else " c"}">{s}</span></td></tr>'
               for i, (t, n, s) in enumerate(PAT, 1))
page('certification.html', '인증·특허', '대경기술 면허·인증 현황(한수원 Q등급, ISO 9001, ISO 45001, INNO-BIZ)과 원전해체·계측 분야 특허 등록 10건, 출원 4건.',
     'Certification', '인증·특허', '원자력·전력산업 전문 자격과 품질·안전 인증, 지식재산권 현황입니다.', 'cert-wall.jpg', f'''  <div class="title ani">
    <h2>Certification<span class="dot"></span></h2>
    <h3>주요 면허 및 인증 현황</h3>
  </div>
  <div class="certGrid">
    {box('NUCLEAR &amp; POWER', '원자력·전력산업 전문자격', NUC)}
    {box('QUALITY &amp; SAFETY', '품질·안전 및 경영 인증', QUAL)}
    {box('ENGINEERING LICENSES', '엔지니어링 및 사업 면허', LIC)}
  </div>

  <div class="block">
    <div class="title ani">
      <h2>R&amp;D &amp; IP<span class="dot"></span></h2>
      <h3>지식재산권 · 특허 등록 10건, 출원 4건</h3>
    </div>
    <table class="perfTable patentTable">
      <thead><tr><th>No.</th><th>발명의 명칭</th><th>특허 / 출원번호</th><th>구분</th></tr></thead>
      <tbody>{prow}</tbody>
    </table>
  </div>

  <div class="block">
    <div class="title ani">
      <h2>Organization<span class="dot"></span></h2>
      <h3>조직도</h3>
    </div>
    <div class="orgChart ani">
      <div class="node">대표이사</div>
      <div class="line"></div>
      <div class="row"><div class="node">기업부설연구소</div><div class="node">품질보증실<small>Q.A · Q.S</small></div><div class="node">안전보건환경팀<small>HSE</small></div></div>
      <div class="line"></div>
      <div class="row biz"><div class="node">경영지원본부</div><div class="node">원자력 사업본부</div><div class="node">플랜트 사업본부</div></div>
    </div>
  </div>

  <div class="block">
    <div class="title ani">
      <h2>Certificates<span class="dot"></span></h2>
      <h3>인증서</h3>
    </div>
    <ul class="dkList ani">{''.join(f'<li>{e(x)}</li>' for x in DK['cert_list'])}</ul>
    <ul class="certGallery ani">{''.join(f'<li><div class="frame"><img src="assets/img/dk/about_certification{i:02d}.jpg" alt="{re.sub("<br>", " ", c)}" loading="lazy"></div><p>{c}</p></li>' for i, c in enumerate(DK['cert_captions'], 1))}</ul>
  </div>

  <div class="block">
    <div class="title ani">
      <h2>Patent<span class="dot"></span></h2>
      <h3>특허 보유 현황</h3>
    </div>
    <div class="patentWrap ani">
      <img src="assets/img/dk/about_patent.jpg" alt="특허증" loading="lazy">
      <ul>{''.join(f'<li><b>{e(t)}</b><span>({e(n)})</span></li>' for t, n in DK['patents'])}</ul>
    </div>
  </div>''')


# ---------- 5. 분야별 주요 실적 (dkenc.kr 주요 실적 3개 페이지 목록) ----------
lists = json.load(open(os.path.join(ROOT, '_tools', 'dk_perf_lists.json'), encoding='utf-8'))
PERF_PAGES = [
    ('perf-design.html', 'design', '설계/엔지니어링', 'Design &amp; Engineering', '설계/엔지니어링(전/계장)',
     '원자력사업본부는 한수원 가동원전 계전설비 설계 Q등급 유자격으로 가동원전 설비개선, 신규 원전 안전계통 도면·문서, SMR·연구용 원자로의 전기·계장 설계를 수행합니다.',
     ['dk-design01.jpg', 'dk-design02.jpg']),
    ('perf-nuclear.html', 'nuclear', '원자력 공사/설치', 'Nuclear Construction', '원자력 공사 &amp; 설치(전/계장)',
     '주제어반·MCC·발전기·여자시스템 교체부터 CEDMCS·NIMS 같은 핵심 감시·제어설비 설치까지, 가동원전의 계획예방정비 기간에 맞춰 시공합니다.',
     ['dk-nuclear01.jpg', 'dk-nuclear02.jpg']),
    ('perf-plant.html', 'plant', '플랜트 공사/제작', 'Plant Construction', '플랜트 공사/제작',
     '화력·복합화력 발전소 전기·계측제어 공사와 석유화학 플랜트 E-House·CCR Module 전기/계장, 일반 건축물 전기·소방 공사를 수행합니다.',
     ['dk-plant01.jpg', 'dk-plant02.jpg']),
]
for fname, key, h2, eng, sub, intro, photos in PERF_PAGES:
    items = lists[key]
    li = ''.join(f'<li><em>{i:02d}</em><span>{e(t)}</span></li>' for i, t in enumerate(items, 1))
    imgs = ''.join(f'<div class="photo" style="background-image:url(assets/img/{p})"></div>' for p in photos)
    page(fname, h2, f'대경기술 주요 실적 - {h2}: {intro}', 'Performance', h2, intro, '', f'''  <div class="perfIntro">
    <div class="title ani">
      <h2>{eng}<span class="dot"></span></h2>
      <h3>{sub}</h3>
      <p>주요 수행 실적 <b>{len(items)}</b>건</p>
    </div>
    <div class="perfPhotos ani">{imgs}</div>
  </div>
  <ol class="perfList ani">{li}</ol>
  <div class="perfMore ani">연월·발주처별 전체 실적은 <a href="performance.html">전체 실적 목록(585건)</a>에서 확인할 수 있습니다.</div>''')


# ---------- 6. dkenc.kr 하위 페이지 (원문 그대로) ----------
def ttl(eng, h3):
    return f'<div class="title ani"><h2>{eng}<span class="dot"></span></h2><h3>{h3}</h3></div>'

def bul(L):
    return '<ul class="dkList">' + ''.join(f'<li>{e(x)}</li>' for x in L) + '</ul>'

c = DK['ceo']
page('ceo.html', 'CEO 인사', '대경기술주식회사 대표이사 임영하 인사말: 21세기 전력산업의 Global Leader.',
     'CEO Message', 'CEO 인사', e(c['sub']), '', f'''  <div class="ceoMsg">
    <div class="ceoText ani">
      <h2 class="eng">CEO Message<span class="dot"></span></h2>
      <h3>{e(c['head']).replace(' 대경기술주식회사', '<br>대경기술주식회사')}</h3>
      <h4>{e(c['sub'])}</h4>
      {''.join(f'<p>{e(x)}</p>' for x in c['body'])}
      <div class="ceoSign"><span>{e(c['sign'])}</span><img src="assets/img/dk/about_ceo_vis02.jpg" alt="대표이사 서명"></div>
    </div>
    <div class="ceoPortrait ani">
      <div class="pic"><img src="assets/img/ceo-portrait.jpg" alt="대경기술주식회사 대표이사 임영하"></div>
      <p><small>대표이사</small>임 영 하</p>
    </div>
  </div>''')

co = DK['company']
page('company.html', '회사 개요', '대경기술주식회사 회사 개요: 설립일 2006.6.1, 부산 기장 대경기술빌딩, 주요 인허가와 주요 사업.',
     'Company', '회사 개요', '창조적인 도전정신으로 새로운 기술 창출을 선도하다', '', f'''  {ttl('Company', '<br>'.join(e(x) for x in co['head']))}
  <div class="infoTable ani">{''.join(f'<dl><dt>{e(k)}</dt><dd>{bul(v) if len(v) > 1 else e(v[0])}</dd></dl>' for k, v in co['rows'])}</div>
  <div class="companyPhoto ani photo" style="background-image:url(assets/img/contact.jpg)"></div>''')

page('organ.html', '사훈/조직도', '대경기술주식회사 사훈과 조직도.', 'Organization', '사훈/조직도', '기술 중시, 경쟁력 확보', '', f'''  {ttl('Motto', '사훈')}
  <div class="figure ani"><img src="assets/img/dk/about_organ_vis01.jpg" alt="대경기술 사훈" loading="lazy"></div>
  <div class="block">
    {ttl('Organization', '조직도')}
    <div class="figure ani"><img src="assets/img/dk/about_organ_vis02.jpg" alt="대경기술 조직도" loading="lazy"></div>
  </div>''')

page('clients.html', '주요 고객사', '대경기술주식회사 주요 고객사.', 'Clients', '주요 고객사', '대경기술과 함께하는 주요 고객사입니다.', '', f'''  {ttl('Clients', '주요 고객사')}
  <div class="figure ani"><img src="assets/img/dk/about_clients_vis01.jpg" alt="대경기술 주요 고객사" loading="lazy"></div>''')

page('ci.html', 'C.I. 소개', '대경기술주식회사 C.I. 소개.', 'C.I.', 'C.I. 소개', e(DK['ci']), '', f'''  {ttl('C.I.', 'C.I.')}
  <p class="lead ani">{e(DK['ci'])}</p>
  <div class="figure ani"><img src="assets/img/dk/about_ci_vis01.jpg" alt="대경기술주식회사 C.I." loading="lazy"></div>''')

si = DK['services_intro']
proj = ''.join(f'<li class="ani"><div class="photo" style="background-image:url(assets/img/dk/business_performance0{i}.jpg)"></div><div class="txt"><h4>{e(t)}</h4>{bul(L)}</div></li>'
               for i, (t, L) in enumerate(si['projects'], 1))
page('biz-services.html', '수행 역무', '대경기술 수행 역무: 원자력, 화력발전소 및 플랜트 전기/계장 분야 선도 업체, 품질보증실, 기업부설연구소.',
     'Services', '수행 역무', '원자력, 화력발전소 및 플랜트 전기/계장 분야 선도 업체', '', f'''  <div class="splitRow">
    <div class="ani">{ttl('Services', '<br>'.join(e(x) for x in si['head']))}{''.join(f'<p class="para">{e(x)}</p>' for x in si['body'])}</div>
    <div class="photo tall ani" style="background-image:url(assets/img/dk/business_performance_top.jpg)"></div>
  </div>
  <div class="block">
    {ttl('Quality Assurance', '품질보증실')}
    <div class="ani">{bul(si['qa'])}</div>
  </div>
  <div class="block">
    {ttl('R&amp;D Center', '기업부설연구소')}
    <p class="lead ani"><b>{e(si['lab_head'])}</b><br>{e(si['lab_sub'])}</p>
    <ul class="projList">{proj}</ul>
  </div>''')

for fname, key, eng, img1, img2 in [('biz-nuclear.html', 'nuclear', 'Nuclear &amp; Power', 'business_nuclear.jpg', 'business_nuclear_power.jpg'),
                                    ('biz-plant.html', 'plant', 'Plant &amp; Offshore Module', 'business_plant_ocean.jpg', 'business_plant.jpg')]:
    d = DK[key]
    page(fname, d['head'], f'대경기술 {d["head"]} - {d["dept"]}: ' + ', '.join(d['items']), eng, d['head'], d['dept'], '', f'''  <div class="splitRow">
    <div class="photo square ani" style="background-image:url(assets/img/dk/{img1})"></div>
    <div class="ani">{ttl(eng, e(d['head']))}<h4 class="dept">{e(d['dept'])}</h4>{bul(d['items'])}</div>
  </div>
  <div class="figure wide ani"><img src="assets/img/dk/{img2}" alt="{e(d['head'])}" loading="lazy"></div>''')

major = ''.join(f'<li class="ani"><div class="photo" style="background-image:url(assets/img/dk/business_services0{i}.jpg)"></div><h4>{e(t)}</h4>{bul(L)}</li>'
                for i, (t, L) in enumerate(DK['major'], 1))
page('biz-major.html', '주요 사업', '대경기술 주요 사업: 고리 1호기 주제어반 교체, MCC 차단기반 교체, CEDMCS, TBM 국산화, KNPC E-House, CCR Module 등.',
     'Major Projects', '주요 사업', '대경기술이 수행한 대표 사업입니다.', '', f'''  {ttl('Major Projects', '주요 사업')}
  <ul class="majorGrid">{major}</ul>''')

for fname, h2, eng in [('news.html', '대경기술 소식', 'News'), ('press.html', '보도자료', 'Press')]:
    page(fname, h2, f'대경기술주식회사 {h2}.', eng, h2, '대경기술의 새로운 소식을 전합니다.', '', f'''  {ttl(eng, h2)}
  <table class="perfTable boardTable ani">
    <thead><tr><th>번호</th><th>제목</th><th>작성자</th><th>날짜</th></tr></thead>
    <tbody><tr><td colspan="4" class="empty">등록된 게시물이 없습니다.</td></tr></tbody>
  </table>''')

L = DK['location']
page('inquiry.html', '고객 문의', '대경기술주식회사 고객 문의: 051-722-0855, dk@dkenc.kr.', 'Contact', '고객 문의', '문의 내용을 남겨주시면 빠르게 답변드리겠습니다.', '', f'''  {ttl('Contact', '고객 문의')}
  <form class="inqForm ani" action="mailto:{L['email']}" method="post" enctype="text/plain">
    <div class="grid">
      <label>업체명<input type="text" name="업체명"></label>
      <label>담당자명<input type="text" name="담당자명"></label>
      <label>E-mail<input type="email" name="E-mail"></label>
      <label>제목<input type="text" name="제목"></label>
    </div>
    <label>문의 내용<textarea name="문의내용" rows="8"></textarea></label>
    <label>첨부<input type="file" name="첨부" disabled><small>첨부 파일은 메일로 보내 주세요: {L['email']}</small></label>
    <div class="agree"><strong>동의</strong>{''.join(f'<p>{e(x)}</p>' for x in DK['inquiry_privacy'])}<label class="chk"><input type="checkbox" required> 개인정보 수집 및 이용에 동의합니다.</label></div>
    <button type="submit" class="sendBtn">SEND</button>
  </form>
  <ul class="contactInfo ani">
    <li><b>ADDRESS</b>46080, 부산광역시 기장군 기장읍 청강로85번길 16 대경기술빌딩 (청강리 174-3번지)</li>
    <li><b>TEL</b><a href="tel:0517220855">{L['tel']}</a></li>
    <li><b>E-MAIL</b><a href="mailto:{L['email']}">{L['email']}</a></li>
  </ul>''')

page('location.html', '오시는 길', '대경기술주식회사 오시는 길: ' + L['addr'], 'Location', '오시는 길', e(L['addr']), '', f'''  {ttl('Location', '오시는 길')}
  <div class="figure wide ani"><img src="assets/img/dk/customer_location.jpg" alt="대경기술 약도" loading="lazy"></div>
  <div class="mapWrap ani"><iframe src="https://maps.google.com/maps?q=%EB%B6%80%EC%82%B0%EA%B4%91%EC%97%AD%EC%8B%9C+%EA%B8%B0%EC%9E%A5%EA%B5%B0+%EA%B8%B0%EC%9E%A5%EC%9D%8D+%EC%B2%AD%EA%B0%95%EB%A1%9C85%EB%B2%88%EA%B8%B8+16&output=embed" loading="lazy" title="대경기술 지도"></iframe></div>
  <ul class="contactInfo ani">
    <li><b>ADDRESS</b>{e(L['addr'])}</li>
    <li><b>TEL</b><a href="tel:0517220855">{L['tel']}</a></li>
    <li><b>FAX</b>{L['fax']}</li>
    <li><b>E-MAIL</b><a href="mailto:{L['email']}">{L['email']}</a></li>
  </ul>''')
