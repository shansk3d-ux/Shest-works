const CACHE_NAME = "repairlog-static-v1";
const PRECACHE_URLS = ["/static/images/logo.png", "/static/images/icon-192.png"];

self.addEventListener("install", function (event) {
    event.waitUntil(
        caches.open(CACHE_NAME).then(function (cache) {
            return cache.addAll(PRECACHE_URLS);
        })
    );
    self.skipWaiting();
});

self.addEventListener("activate", function (event) {
    event.waitUntil(
        caches.keys().then(function (keys) {
            return Promise.all(
                keys
                    .filter(function (key) {
                        return key !== CACHE_NAME;
                    })
                    .map(function (key) {
                        return caches.delete(key);
                    })
            );
        })
    );
    self.clients.claim();
});

self.addEventListener("fetch", function (event) {
    var url = new URL(event.request.url);

    // Only cache same-origin static assets (images, CSS, JS). Pages, forms and
    // any data requests always go to the network so repair records are never
    // served stale from an offline cache.
    if (event.request.method !== "GET" || url.pathname.indexOf("/static/") !== 0) {
        return;
    }

    event.respondWith(
        caches.match(event.request).then(function (cached) {
            return (
                cached ||
                fetch(event.request).then(function (response) {
                    var copy = response.clone();
                    caches.open(CACHE_NAME).then(function (cache) {
                        cache.put(event.request, copy);
                    });
                    return response;
                })
            );
        })
    );
});
