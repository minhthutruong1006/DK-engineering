# 한글 페이지(루트 *.html) → 영문판(en/*.html) 생성
# 번역은 _tools/en_dict.json(한글 문구 → 영문)에서 찾고, 한글 페이지를 고친 뒤 이 스크립트를 다시 돌리면 영문판이 갱신된다.
# 한글 페이지에는 EN 전환 링크와 hreflang만 넣는다(여러 번 돌려도 같은 결과).
# 사용: python -I _tools/build_en.py   → 번역이 없는 한글 문구가 있으면 목록을 출력한다.
import glob, html, io, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://minhthutruong1006.github.io/DK-engineering/'   # 정식 도메인 연결 시 SEO 블록과 함께 교체
HANGUL = re.compile(r'[가-힣]')
D = json.load(io.open(os.path.join(ROOT, '_tools', 'en_dict.json'), encoding='utf-8'))

# 사전으로 안 되는 자리(줄바꿈으로 나뉜 라벨, 스크립트 안 표시 문구, 폼 필드 이름)
RAW = {
    'biz-plant.html': [('<span class="cap">국책과제<br>(연구개발)</span>', '<span class="cap">R&amp;D<br>Projects</span>')],
    'inquiry.html': [
        ('name="업체명"', 'name="Company"'), ('name="담당자명"', 'name="Name"'),
        ('name="제목"', 'name="Subject"'), ('name="문의내용"', 'name="Message"'), ('name="첨부"', 'name="Attachment"'),
        ("'자동등록방지 숫자가 일치하지 않습니다. 다시 입력해 주세요.'", "'The numbers do not match. Please try again.'"),
    ],
    'company.html': [('<dt>주요 사업</dt>', '<dt>Main business</dt>')],  # 메뉴 '주요 사업'(Major Projects)과 뜻이 다름
    'performance.html': [
        ('<th>구분</th>', '<th>Category</th>'),  # 특허표의 '구분'(Status)과 뜻이 다름
        ("(p[0].indexOf('설계') === 0 ? '설계' : '공사') + '</span><span class=\"tag g\">' + p[1] + '</span>",
         "(p[0].indexOf('설계') === 0 ? 'Design' : 'Construction') + '</span><span class=\"tag g\">' + (p[1] === '일반건설' ? 'General Construction' : 'Power Plant') + '</span>"),
    ],
}
# 한글이 남아도 되는 곳(전체 실적 585건 공사명 데이터, 검색 예시, 필터 값)
ALLOW = re.compile(r'var PERF = \[|data-v="|indexOf\(\'설계\'\)|p\[1\] === \'일반건설\'|e\.g\. 고리|<!--|<script type="application/ld\+json">')

missing = {}


def norm(s):
    return re.sub(r'\s+', ' ', s).strip()


def tr(text, page):
    key = norm(html.unescape(text))
    if key in D:
        return D[key]
    missing.setdefault(page, set()).add(key)
    return None


GLOBAL_RAW = [('/download/DK_bro_kr.pdf', '/download/DK_bro_en.pdf')]  # 원래 사이트의 영문 브로슈어
AFTER = [('051-722-0855', '+82-51-722-0855'), ('051-722-1330', '+82-51-722-1330')]  # 번역 뒤 해외용 전화번호 표기


def translate_html(s, page):
    for a, b in GLOBAL_RAW + RAW.get(page, []):
        s = s.replace(a, b)
    parts = re.split(r'(<script\b.*?</script>|<style\b.*?</style>)', s, flags=re.S)
    for i in range(0, len(parts), 2):  # 스크립트·스타일 블록은 건너뜀
        seg = parts[i]

        def text_sub(m):
            t = m.group(1)
            if not HANGUL.search(t):
                return m.group(0)
            v = tr(t, page)
            if v is None:
                return m.group(0)
            lead = re.match(r'\s*', t).group(0)
            trail = re.search(r'\s*$', t).group(0)
            return '>' + lead + html.escape(v, quote=False) + trail + '<'
        seg = re.sub(r'>([^<>]+)<', text_sub, seg)

        def attr_sub(m):
            name, q, val = m.group(1), m.group(2), m.group(3)
            if not HANGUL.search(val):
                return m.group(0)
            v = tr(val, page)
            if v is None:
                return m.group(0)
            v = html.escape(v, quote=False).replace(q, '&quot;' if q == '"' else '&#39;')
            return f'{name}={q}{v}{q}'
        seg = re.sub(r'\b(alt|placeholder|title|aria-label|content|data-eras)=(["\'])(.*?)\2', attr_sub, seg, flags=re.S)
        parts[i] = seg
    return ''.join(parts)


def drop_echo_eyebrow(s):
    # 한글판의 영문 소제목(h2)과 번역된 제목(h3)이 같아지면 소제목을 뺀다 (예: Services / Services)
    def sub(m):
        a = norm(html.unescape(re.sub(r'<[^>]+>', '', m.group(2)))).lower()
        b = norm(html.unescape(re.sub(r'<[^>]+>', '', m.group(4)))).lower()
        return m.group(3) + m.group(4) + m.group(5) if a == b else m.group(0)
    return re.sub(r'(<h2>(.*?)<span class="dot"></span></h2>)(\s*<h3[^>]*>)(.*?)(</h3>)', sub, s)


def fix_paths(s):
    s = re.sub(r'\b(href|src)="(assets/|favicon\.ico|site\.webmanifest)', r'\1="../\2', s)
    s = s.replace('url(assets/', 'url(../assets/')
    return s


def hreflang(page):
    p = '' if page == 'index.html' else page
    return (f'<link rel="alternate" hreflang="ko" href="{BASE}{p}">\n'
            f'<link rel="alternate" hreflang="en" href="{BASE}en/{p}">\n'
            f'<link rel="alternate" hreflang="x-default" href="{BASE}{p}">\n')


def set_seo(s, page, en):
    s = re.sub(r'<link rel="alternate" hreflang="[^"]+" href="[^"]*">\n', '', s)
    s = s.replace('<!-- /SEO -->', hreflang(page) + '<!-- /SEO -->', 1)
    if en:
        p = '' if page == 'index.html' else page
        s = re.sub(r'(<link rel="canonical" href=")[^"]*(">)', lambda m: m.group(1) + BASE + 'en/' + p + m.group(2), s, count=1)
        s = re.sub(r'(<meta property="og:url" content=")[^"]*(">)', lambda m: m.group(1) + BASE + 'en/' + p + m.group(2), s, count=1)
        s = s.replace('<meta property="og:locale" content="ko_KR">', '<meta property="og:locale" content="en_US">')
    return s


def lang_link(s, page, en):
    a = (f'<a href="../{page}" class="language" hreflang="ko" lang="ko" title="한국어">KR</a>' if en
         else f'<a href="en/{page}" class="language" hreflang="en" lang="en" title="English">EN</a>')
    return re.sub(r'<a [^>]*class="language"[^>]*>(?:EN|KR)</a>', a, s, count=1)


def main():
    os.makedirs(os.path.join(ROOT, 'en'), exist_ok=True)
    pages = sorted(os.path.basename(f) for f in glob.glob(os.path.join(ROOT, '*.html')))
    for page in pages:
        path = os.path.join(ROOT, page)
        ko = io.open(path, encoding='utf-8').read()
        ko2 = lang_link(set_seo(ko, page, False), page, False)
        if ko2 != ko:
            io.open(path, 'w', encoding='utf-8', newline='').write(ko2)
        en = translate_html(ko2, page)
        for x, y in AFTER:
            en = en.replace(x, y)
        en = en.replace('<html lang="ko">', '<html lang="en">', 1)
        en = fix_paths(set_seo(drop_echo_eyebrow(en), page, True))
        en = lang_link(en, page, True)
        io.open(os.path.join(ROOT, 'en', page), 'w', encoding='utf-8', newline='').write(en)

    # 사이트맵에 영문 주소 추가
    sm = os.path.join(ROOT, 'sitemap.xml')
    x = io.open(sm, encoding='utf-8').read()
    x = re.sub(r'  <url><loc>' + re.escape(BASE) + r'en/[^<]*</loc>.*?</url>\n', '', x)
    adds = ''.join(re.sub(r'<loc>' + re.escape(BASE), '<loc>' + BASE + 'en/', l) + '\n'
                   for l in x.splitlines() if l.strip().startswith('<url><loc>' + BASE))
    x = x.replace('</urlset>', adds + '</urlset>')
    io.open(sm, 'w', encoding='utf-8', newline='\n').write(x)

    # 번역 누락·남은 한글 점검
    left = {}
    for page in pages:
        s = io.open(os.path.join(ROOT, 'en', page), encoding='utf-8').read()
        lines = [l.strip()[:90] for l in s.splitlines() if HANGUL.search(l) and not ALLOW.search(l)
                 and 'title="한국어"' not in l]
        if lines:
            left[page] = lines
    print('pages:', len(pages))
    if missing:
        print('\n[번역 없음]')
        for p, ks in missing.items():
            for k in sorted(ks):
                print(' ', p, '|', k)
    if left:
        print('\n[한글 남은 줄]')
        for p, ls in left.items():
            for l in ls[:6]:
                print(' ', p, '|', l)
    if not missing and not left:
        print('OK: 영문판에 번역 누락 없음')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
