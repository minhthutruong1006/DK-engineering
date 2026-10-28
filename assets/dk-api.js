// 사이트·관리자 공용 데이터 연결부. DK_API가 있으면 서버 REST, 없으면 localStorage 미리보기.
(function () {
  var BASE = (window.DK_API || '').replace(/\/$/, '');
  var LS = 'dk_demo_';

  function lsGet(k, def) { try { var v = JSON.parse(localStorage.getItem(LS + k)); return v == null ? def : v; } catch (e) { return def; } }
  function lsSet(k, v) { try { localStorage.setItem(LS + k, JSON.stringify(v)); } catch (e) {} }
  function ssGet(k) { try { return sessionStorage.getItem(k) || ''; } catch (e) { return ''; } }
  function ssSet(k, v) { try { if (v == null) sessionStorage.removeItem(k); else sessionStorage.setItem(k, v); } catch (e) {} }
  function token() { return ssGet('dk_token'); }
  function newId() { return String(Date.now()) + Math.floor(Math.random() * 1000); }
  function fail(msg) { return Promise.reject(new Error(msg)); }

  function req(method, path, body) {
    var h = { 'Content-Type': 'application/json' };
    if (token()) h.Authorization = 'Bearer ' + token();
    return fetch(BASE + path, { method: method, headers: h, body: body ? JSON.stringify(body) : undefined }).then(function (r) {
      if (r.status === 401) { var e = new Error('로그인이 필요합니다'); e.auth = true; throw e; }
      if (!r.ok) return r.json().catch(function () { return {}; }).then(function (j) { throw new Error(j.error || '서버 오류 (' + r.status + ')'); });
      return r.status === 204 ? null : r.json();
    });
  }

  // ---------- 목록형 데이터 (문의·실적·게시글) ----------
  function demo(col) {
    return {
      list: function (q) {
        return Promise.resolve(lsGet(col, []).filter(function (x) {
          return !q || Object.keys(q).every(function (k) { return x[k] === q[k]; });
        }));
      },
      create: function (d) {
        var a = lsGet(col, []);
        d = Object.assign({ id: newId(), created_at: new Date().toISOString() }, d);
        a.unshift(d); lsSet(col, a);
        return Promise.resolve(d);
      },
      update: function (id, d) {
        lsSet(col, lsGet(col, []).map(function (x) { return x.id === id ? Object.assign({}, x, d) : x; }));
        return Promise.resolve(null);
      },
      remove: function (id) {
        lsSet(col, lsGet(col, []).filter(function (x) { return x.id !== id; }));
        return Promise.resolve(null);
      }
    };
  }
  function rest(col) {
    return {
      list: function (q) { return req('GET', '/api/' + col + (q ? '?' + new URLSearchParams(q) : '')); },
      create: function (d) { return req('POST', '/api/' + col, d); },
      update: function (id, d) { return req('PATCH', '/api/' + col + '/' + encodeURIComponent(id), d); },
      remove: function (id) { return req('DELETE', '/api/' + col + '/' + encodeURIComponent(id)); }
    };
  }
  var mk = BASE ? rest : demo;

  // ---------- 미리보기 모드 계정 (브라우저 저장, 보안용 아님. 서버가 붙으면 서버 계정 사용) ----------
  var DEMO_ID = 'test', DEMO_PW = 'test1234';
  function sha(s) {
    return crypto.subtle.digest('SHA-256', new TextEncoder().encode('dk:' + s)).then(function (b) {
      return Array.prototype.map.call(new Uint8Array(b), function (x) { return ('0' + x.toString(16)).slice(-2); }).join('');
    });
  }
  function accts() {
    var a = lsGet('accounts', null);
    if (a && a.length) return Promise.resolve(a);
    return sha(DEMO_PW).then(function (h) {
      a = [{ id: '1', login_id: DEMO_ID, name: '관리자', pw_hash: h, created_at: new Date().toISOString() }];
      lsSet('accounts', a); return a;
    });
  }
  function pub(x) { return { id: x.id, login_id: x.login_id, name: x.name, created_at: x.created_at, last_login: x.last_login }; }
  var demoAccounts = {
    list: function () { return accts().then(function (a) { return a.map(pub); }); },
    create: function (d) {
      return accts().then(function (a) {
        if (a.some(function (x) { return x.login_id === d.login_id; })) return fail('이미 있는 아이디입니다');
        return sha(d.pw).then(function (h) {
          var x = { id: newId(), login_id: d.login_id, name: d.name, pw_hash: h, created_at: new Date().toISOString() };
          a.push(x); lsSet('accounts', a); return pub(x);
        });
      });
    },
    update: function (id, d) {
      return accts().then(function (a) {
        return (d.pw ? sha(d.pw) : Promise.resolve('')).then(function (h) {
          lsSet('accounts', a.map(function (x) {
            if (x.id !== id) return x;
            x = Object.assign({}, x); if (d.name) x.name = d.name; if (h) x.pw_hash = h; return x;
          }));
          return null;
        });
      });
    },
    remove: function (id) {
      return accts().then(function (a) {
        if (a.length < 2) return fail('계정이 하나뿐이라 삭제할 수 없습니다');
        if (DK.me() && DK.me().id === id) return fail('로그인한 본인 계정은 삭제할 수 없습니다');
        lsSet('accounts', a.filter(function (x) { return x.id !== id; })); return null;
      });
    }
  };

  // ---------- 설정 (알림 메일 등) ----------
  var settings = BASE ? {
    get: function () { return req('GET', '/api/settings'); },
    save: function (d) { return req('PUT', '/api/settings', d); }
  } : {
    get: function () { return Promise.resolve(lsGet('settings', {})); },
    save: function (d) { lsSet('settings', Object.assign(lsGet('settings', {}), d)); return Promise.resolve(null); }
  };

  // ---------- SEO (페이지별 덮어쓰기) ----------
  var seo = BASE ? {
    list: function () { return req('GET', '/api/seo'); },
    save: function (page, d) { return req('PUT', '/api/seo/' + encodeURIComponent(page), d); },
    reset: function (page) { return req('DELETE', '/api/seo/' + encodeURIComponent(page)); }
  } : {
    list: function () { return Promise.resolve(lsGet('seo', [])); },
    save: function (page, d) {
      var a = lsGet('seo', []).filter(function (x) { return x.page !== page; });
      a.push(Object.assign({ page: page }, d)); lsSet('seo', a); return Promise.resolve(null);
    },
    reset: function (page) { lsSet('seo', lsGet('seo', []).filter(function (x) { return x.page !== page; })); return Promise.resolve(null); }
  };

  window.DK = {
    demo: !BASE,
    inquiries: mk('inquiries'),
    perf: mk('perf'),
    posts: mk('posts'),
    accounts: BASE ? rest('accounts') : demoAccounts,
    settings: settings,
    seo: seo,
    login: function (id, pw) {
      if (BASE) {
        return req('POST', '/api/login', { id: id, pw: pw }).then(function (r) {
          ssSet('dk_token', r.token); ssSet('dk_me', JSON.stringify(r.user || { login_id: id, name: id }));
        });
      }
      return accts().then(function (a) {
        return sha(pw).then(function (h) {
          var x = a.filter(function (u) { return u.login_id === id && u.pw_hash === h; })[0];
          if (!x) { var e = new Error('아이디 또는 비밀번호가 맞지 않습니다'); e.auth = true; throw e; }
          x.last_login = new Date().toISOString(); lsSet('accounts', a);
          ssSet('dk_token', 'demo:' + x.id); ssSet('dk_me', JSON.stringify(pub(x)));
        });
      });
    },
    logout: function () {
      if (BASE && token()) req('POST', '/api/logout').catch(function () {});
      ssSet('dk_token', null); ssSet('dk_me', null);
    },
    loggedIn: function () { return !!token(); },
    me: function () { try { return JSON.parse(ssGet('dk_me')) || null; } catch (e) { return null; } },
    esc: function (s) {
      return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; });
    },
    // 파일 업로드 → { url, name, size }. 서버: POST /api/upload, 미리보기: data URL(브라우저 저장 한도 약 5MB)
    upload: function (file, name) {
      name = name || file.name || 'file';
      if (BASE) {
        var fd = new FormData(); fd.append('file', file, name);
        return fetch(BASE + '/api/upload', { method: 'POST', headers: token() ? { Authorization: 'Bearer ' + token() } : {}, body: fd }).then(function (r) {
          if (r.status === 401) { var e = new Error('로그인이 필요합니다'); e.auth = true; throw e; }
          if (!r.ok) throw new Error('업로드 실패 (' + r.status + ')');
          return r.json();
        }).then(function (j) { return { url: j.url, name: name, size: file.size }; });
      }
      if (file.size > 1.5 * 1024 * 1024) return fail('미리보기 모드에서는 1.5MB 이하 파일만 올릴 수 있습니다 (서버 연결 후 제한 없음)');
      return new Promise(function (ok, no) {
        var fr = new FileReader();
        fr.onload = function () { ok({ url: fr.result, name: name, size: file.size }); };
        fr.onerror = function () { no(new Error('파일을 읽지 못했습니다')); };
        fr.readAsDataURL(file);
      });
    },
    // 게시글 본문 HTML 정리: 허용한 태그·속성만 남김 (붙여넣기·화면 표시 공용)
    clean: function (html) {
      if (!/[<>]/.test(html || '')) return DK.esc(html).replace(/\n/g, '<br>'); // 예전 일반 텍스트 글
      var OK = { P: 1, BR: 1, B: 1, STRONG: 1, I: 1, EM: 1, U: 1, S: 1, H2: 1, H3: 1, H4: 1, UL: 1, OL: 1, LI: 1, BLOCKQUOTE: 1, A: 1, IMG: 1, FIGURE: 1, FIGCAPTION: 1, HR: 1, TABLE: 1, THEAD: 1, TBODY: 1, TR: 1, TH: 1, TD: 1, DIV: 1, SPAN: 1 };
      var ATTR = { A: ['href'], IMG: ['src', 'alt'], TD: ['colspan', 'rowspan'], TH: ['colspan', 'rowspan'] };
      var doc = new DOMParser().parseFromString('<div>' + html + '</div>', 'text/html');
      (function walk(el) {
        Array.prototype.slice.call(el.childNodes).forEach(function (n) {
          if (n.nodeType === 3) return;
          if (n.nodeType !== 1 || /^(SCRIPT|STYLE|IFRAME|OBJECT|EMBED|META|LINK|TITLE|HEAD)$/.test(n.tagName)) { n.remove(); return; }
          walk(n);
          if (!OK[n.tagName]) { while (n.firstChild) n.parentNode.insertBefore(n.firstChild, n); n.remove(); return; }
          var keep = ATTR[n.tagName] || [];
          Array.prototype.slice.call(n.attributes).forEach(function (a) { if (keep.indexOf(a.name) < 0) n.removeAttribute(a.name); });
          var u = n.getAttribute('href') || n.getAttribute('src');
          if (u && !/^(https?:|mailto:|tel:|data:image\/|\/|\.\.?\/|#)/i.test(u.trim())) { n.removeAttribute('href'); n.removeAttribute('src'); }
          if (n.tagName === 'A') { n.setAttribute('target', '_blank'); n.setAttribute('rel', 'noopener'); }
        });
      })(doc.body.firstChild);
      return doc.body.firstChild.innerHTML;
    }
  };
})();
