# 21개 한글 페이지에서 번역이 필요한 한글 문구를 뽑는다 (영문판 사전 작성·누락 검사용)
# 사용: python -I _tools/i18n_extract.py [출력.json]
import glob, io, json, os, re, sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HANGUL = re.compile(r'[가-힣]')
ATTRS = ('alt', 'placeholder', 'title', 'aria-label', 'content', 'data-eras')


class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.skip = [], 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style'):
            self.skip += 1
        for k, v in attrs:
            if k in ATTRS and v and HANGUL.search(v):
                self.out.append(v.strip())

    def handle_endtag(self, tag):
        if tag in ('script', 'style'):
            self.skip -= 1

    def handle_data(self, d):
        if not self.skip and HANGUL.search(d):
            self.out.append(re.sub(r'\s+', ' ', d).strip())


def page_strings(path):
    s = io.open(path, encoding='utf-8').read()
    p = P(); p.feed(s)
    seen, res = set(), []
    for t in p.out:
        if t not in seen:
            seen.add(t); res.append(t)
    return res


if __name__ == '__main__':
    data = {os.path.basename(f): page_strings(f) for f in sorted(glob.glob(os.path.join(ROOT, '*.html')))}
    out = sys.argv[1] if len(sys.argv) > 1 else None
    if out:
        io.open(out, 'w', encoding='utf-8').write(json.dumps(data, ensure_ascii=False, indent=1))
    allu = {t for v in data.values() for t in v}
    print('unique strings:', len(allu), 'chars:', sum(len(t) for t in allu))
    for k, v in data.items():
        print(k, len(v))
