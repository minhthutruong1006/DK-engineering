# DK ENGINEERING 관리자 서버 API 규격

사이트(GitHub Pages 정적 페이지)와 관리자(`/admin/`)는 이 규격의 REST API만 호출합니다.
서버를 만든 뒤 `assets/dk-config.js`의 `window.DK_API`에 서버 주소를 넣으면 바로 연결됩니다.
비워 두면 미리보기 모드(브라우저 localStorage 저장)로 동작합니다.

- 형식: JSON (`Content-Type: application/json`), 문자 UTF-8
- 인증: `POST /api/login`이 준 토큰을 `Authorization: Bearer <token>`으로 보냄. 토큰이 없거나 만료면 **401** 응답 (관리자가 로그인 화면으로 돌아감)
- CORS: 사이트 도메인(`https://minhthutruong1006.github.io`, 이후 정식 도메인)에서 `GET, POST, PATCH, DELETE, OPTIONS`와 `Authorization, Content-Type` 헤더 허용
- `id`는 서버가 만드는 문자열(숫자여도 문자열로 응답), `created_at`은 ISO 8601
- 수정·삭제 성공은 `200`(JSON) 또는 `204`(본문 없음) 둘 다 됨

## 로그인

| 메서드 | 경로 | 인증 | 요청 | 응답 |
|---|---|---|---|---|
| POST | `/api/login` | 없음 | `{ "id": "admin", "pw": "..." }` | `{ "token": "...", "user": { "id": "1", "login_id": "admin", "name": "관리자" } }`, 틀리면 401 |
| POST | `/api/logout` | 필요 | 없음 | 토큰 폐기 |

비밀번호는 bcrypt/argon2 해시로 저장하고, 로그인 실패 횟수 제한(예: 5회 실패 시 10분 잠금)을 둡니다. 토큰 유효기간은 8~12시간 정도.
첫 계정은 서버 설치 때 직접 만들어 두세요(관리자 미리보기 모드의 기본 계정은 브라우저용이라 서버와 무관).

## 관리자 계정 `accounts` (전부 인증 필요)

| 메서드 | 경로 | 설명 |
|---|---|---|
| GET | `/api/accounts` | 목록 (비밀번호 해시는 절대 응답에 넣지 않음) |
| POST | `/api/accounts` | 추가 `{ "login_id", "name", "pw" }`. 아이디 중복이면 409 + `{ "error": "이미 있는 아이디입니다" }` |
| PATCH | `/api/accounts/{id}` | `{ "name"?, "pw"? }` (pw가 오면 비밀번호 변경) |
| DELETE | `/api/accounts/{id}` | 삭제. 본인 계정·마지막 1개는 거부(400 + `error`) |

```json
{ "id": "1", "login_id": "admin", "name": "관리자", "created_at": "...", "last_login": "..." }
```
오류 응답은 `{ "error": "사람이 읽을 메시지" }` 형식이면 관리자 화면에 그대로 표시됩니다.

## 설정 `settings` (전부 인증 필요)

| 메서드 | 경로 | 설명 |
|---|---|---|
| GET | `/api/settings` | `{ "notify_emails": ["dk@dkenc.kr", ...] }` |
| PUT | `/api/settings` | 보낸 키만 덮어쓰기 |

`notify_emails`: 고객 문의가 접수될 때(`POST /api/inquiries`) 알림 메일을 받을 주소들. 메일 제목 예: `[홈페이지 문의] {업체명} - {제목}`, 본문에 업체명·담당자·E-mail·내용과 관리자 링크.

## SEO `seo`

| 메서드 | 경로 | 인증 | 설명 |
|---|---|---|---|
| GET | `/api/seo` | **없음** (모든 페이지가 읽음) | 수정한 페이지만 배열로 |
| PUT | `/api/seo/{page}` | 필요 | 저장 (`page` 예: `perf-design.html`) |
| DELETE | `/api/seo/{page}` | 필요 | 원래 값으로 되돌림 |

```json
{ "page": "perf-design.html", "title": "...", "description": "...", "og_image": "https://..." }
```
사이트 공통 값은 `page`가 `_site`인 항목으로 같은 API에 저장합니다:
```json
{ "page": "_site", "site_name": "...", "favicon": "https://.../icon.png", "og_image": "https://.../share.jpg", "google_verify": "코드값", "naver_verify": "코드값" }
```
`google_verify`·`naver_verify`는 검색엔진이 HTML 원문에서만 확인하므로, 서버가 index.html `<head>`에
`<meta name="google-site-verification" content="...">`, `<meta name="naver-site-verification" content="...">`로 직접 써 넣어야 합니다.
정식 도메인을 연결하면 각 HTML의 `<!-- SEO -->` 블록(canonical·og:url·og:image), `sitemap.xml`, `robots.txt`의 `https://minhthutruong1006.github.io/DK-engineering/` 주소를 새 도메인으로 바꿔야 합니다.
지금은 페이지가 열릴 때 JS로 title·description·og 태그를 바꿉니다(구글은 반영, 네이버는 JS 반영이 약함).
서버가 생기면 이 값을 HTML `<head>`에 직접 써 넣는 굽기 작업(저장 시 또는 주기적으로 GitHub에 커밋)을 붙이는 것을 권장합니다.

## 고객 문의 `inquiries`

| 메서드 | 경로 | 인증 | 설명 |
|---|---|---|---|
| POST | `/api/inquiries` | **없음** (사이트 문의 폼) | 접수. 스팸 대비 IP당 횟수 제한 권장 |
| GET | `/api/inquiries` | 필요 | 전체 목록 |
| PATCH | `/api/inquiries/{id}` | 필요 | `status`, `memo` 변경 |
| DELETE | `/api/inquiries/{id}` | 필요 | 삭제 |

```json
{
  "id": "17",
  "created_at": "2026-10-28T15:20:00+09:00",
  "company": "업체명",
  "name": "담당자명",
  "email": "a@b.com",
  "title": "제목",
  "content": "문의 내용",
  "status": 0,
  "memo": ""
}
```
`status`: 0 신규, 1 확인(관리자가 열면 자동), 2 답변 완료. POST로 받은 `status`·`memo`는 무시하고 0·빈값으로 저장.
접수 시 dk@dkenc.kr로 알림 메일을 보내면 좋음.

## 주요 실적 `perf`

| 메서드 | 경로 | 인증 | 설명 |
|---|---|---|---|
| GET | `/api/perf` · `/api/perf?cat=design` | **없음** (사이트 표시) | 목록, `cat` 필터 |
| POST | `/api/perf` | 필요 | 등록 |
| PATCH | `/api/perf/{id}` | 필요 | 수정 |
| DELETE | `/api/perf/{id}` | 필요 | 삭제 |

```json
{ "id": "3", "cat": "design", "field": "발전 플랜트", "ym": "2026.10", "title": "공사 / 용역명" }
```
`cat`: `design` 설계/엔지니어링, `nuclear` 원자력 공사/설치, `plant` 플랜트 공사/제작
`field`: `발전 플랜트` 또는 `일반건설`. `ym`: `YYYY.MM`
등록 건은 해당 분야 페이지 맨 위와 전체 실적 목록(연월순)에 함께 나옵니다. 기존 홈페이지 실적은 HTML에 그대로 있고 API에는 없습니다.

## 소식·보도자료 `posts`

| 메서드 | 경로 | 인증 | 설명 |
|---|---|---|---|
| GET | `/api/posts?board=news` · `?board=press` | **없음** (사이트 표시) | 목록 |
| POST | `/api/posts` | 필요 | 등록 |
| PATCH | `/api/posts/{id}` | 필요 | 수정 |
| DELETE | `/api/posts/{id}` | 필요 | 삭제 |

```json
{
  "id": "5", "board": "news", "title": "제목", "author": "대경기술", "date": "2026-10-28",
  "body": "<p>본문 <b>HTML</b></p><p><img src=\"https://.../a.jpg\" alt=\"\"></p>",
  "link": "https://... (선택)",
  "pinned": false,
  "files": [ { "url": "https://.../brochure.pdf", "name": "brochure.pdf", "size": 482113 } ],
  "created_at": "..."
}
```
`board`: `news` 대경기술 소식, `press` 보도자료. `pinned`: 목록 맨 위 공지 고정.
`body`는 관리자 에디터가 만든 HTML입니다. 화면에 낼 때는 사이트·관리자가 허용 태그만 남기도록 다시 정리하지만(`DK.clean`), 서버에서도 저장 전에 같은 허용 목록으로 정리하세요:
`p br b strong i em u s h2 h3 h4 ul ol li blockquote a[href] img[src,alt] figure figcaption hr table thead tbody tr th td div span`, 그 외 태그·속성(style, on* 이벤트 등)과 `javascript:` 주소는 제거.
예전 글처럼 `body`에 태그가 없으면 일반 텍스트로 보고 줄바꿈을 살려 표시합니다.

사이트 상세 보기 주소는 `news.html?id={id}`, `press.html?id={id}` 입니다(목록·검색·10개씩 페이지·이전글/다음글은 사이트에서 처리).

## 파일 업로드

| 메서드 | 경로 | 인증 | 요청 | 응답 |
|---|---|---|---|---|
| POST | `/api/upload` | 필요 | `multipart/form-data`, 필드 이름 `file` | `{ "url": "https://.../파일" }` |

게시글 본문 사진(관리자가 긴 변 1600px JPEG로 줄여서 보냄)과 첨부파일에 씁니다. 공개 주소로 바로 열려야 하고, 확장자 허용 목록(jpg png webp gif pdf hwp hwpx doc docx xls xlsx ppt pptx zip)과 용량 제한(예: 20MB)을 두세요.
미리보기 모드에서는 파일을 data URL로 브라우저에 저장하므로 1.5MB 이하만 받습니다.

## 공개 GET 응답
`GET /api/perf`, `GET /api/posts`는 로그인 없이 열려 있어야 합니다(사이트 방문자가 읽음). 그 외 쓰기와 `GET /api/inquiries`는 반드시 인증 필요.
