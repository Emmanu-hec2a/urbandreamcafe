const CACHE_NAME = "urbanfoods-cache-v2";
const urlsToCache = [
  "/",
  "/static/styles.css",
  "/static/js/order_detail.js",
  "/static/js/homepage.js",
  "/static/images/favicon.png",
  "/static/images/bg.jpeg",
  "/static/images/bg-pattern.jpg",
  "/static/manifest.json"
];

// Install service worker
self.addEventListener("install", (event) => {
  self.skipWaiting(); // Activate immediately
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log("Opened cache");
      return cache.addAll(urlsToCache);
    })
  );
});

// Fetch from cache if available, with offline fallback
self.addEventListener("fetch", (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      if (response) {
        return response;
      }
      return fetch(event.request).catch(() => {
        // Offline fallback: return cached homepage for navigation requests
        if (event.request.mode === 'navigate') {
          return caches.match('/');
        }
      });
    })
  );
});

// Update service worker and claim clients
self.addEventListener("activate", (event) => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then((cacheNames) =>
      Promise.all(
        cacheNames.map((name) => {
          if (!cacheWhitelist.includes(name)) {
            return caches.delete(name);
          }
        })
      )
    ).then(() => {
      return self.clients.claim(); // Take control of all open clients
    })
  );
});
