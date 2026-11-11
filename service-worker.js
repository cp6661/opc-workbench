/* 一人公司工作台 - Service Worker（离线缓存） */
const CACHE = 'opc-v23';
const ASSETS = [
  './',
  './index.html',
  './word-quiz.html',
  './data.js',
  './manifest.json',
  './icon-192.png',
  './icon-512.png'
];

/* 这些页面永远优先取网络，保证改版后手机立刻看到新版；断网才回退缓存 */
const NET_FIRST = ['/', '/index.html', '/word-quiz.html'];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(ASSETS)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

function netFirst(req, url) {
  return fetch(req, { cache: 'no-store' }).then((res) => {
    const copy = res.clone();
    caches.open(CACHE).then((c) => c.put(url.origin + url.pathname, copy));
    return res;
  }).catch(() => caches.match(req).then((c) => c || caches.match('./index.html')));
}

self.addEventListener('fetch', (e) => {
  if (e.request.method !== 'GET') return;
  const url = new URL(e.request.url);

  // 跨域请求（拉取每日最新数据）直接走网络，不进缓存
  if (url.origin !== self.location.origin) {
    e.respondWith(fetch(e.request));
    return;
  }

  // 页面导航 / HTML：网络优先，避免手机长时间停在旧版本
  if (e.request.mode === 'navigate' || NET_FIRST.includes(url.pathname) || url.pathname.endsWith('.html')) {
    e.respondWith(netFirst(e.request, url));
    return;
  }

  // 其他静态资源：缓存优先
  e.respondWith(
    caches.match(e.request).then((cached) => {
      if (cached) return cached;
      return fetch(e.request).then((res) => {
        const copy = res.clone();
        caches.open(CACHE).then((c) => c.put(e.request, copy));
        return res;
      }).catch(() => caches.match('./index.html'));
    })
  );
});
