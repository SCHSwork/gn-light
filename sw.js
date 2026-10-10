// GN Light offline helper: keeps a copy of the page so it opens instantly and
// works offline. Always tries the network first, so updates show right away.
const C = "gnl-1";
self.addEventListener("install", e => { self.skipWaiting(); e.waitUntil(caches.open(C).then(c => c.add("./"))); });
self.addEventListener("activate", e => e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== C).map(k => caches.delete(k)))).then(() => self.clients.claim())));
self.addEventListener("fetch", e => {
  if (e.request.mode !== "navigate") return;
  e.respondWith(fetch(e.request).then(r => { const copy = r.clone(); caches.open(C).then(c => c.put("./", copy)); return r; })
    .catch(() => caches.match("./")));
});
