const CACHE_NAME = 'pdf-to-anything-v3';
const ASSETS_TO_CACHE = [
    '/',
    '/static/offline.html',
    '/static/css/style.css',
    '/static/js/app.js',
    '/static/js/notifications.js',
    '/static/js/service-worker-register.js',
    '/static/manifest.json',
    '/static/icons/favicon-64x64.png',
    '/static/icons/apple-touch-icon.png',
    '/static/icons/icon-192x192.png',
    '/static/icons/icon-512x512.png',
    '/static/icons/maskable-icon-192x192.png',
    '/static/icons/maskable-icon-512x512.png'
];

// Install event
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(ASSETS_TO_CACHE))
            .then(() => self.skipWaiting())
            .catch(error => console.error('PWA precache failed:', error))
    );
});

// Activate event
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => self.clients.claim())
    );
});

// Fetch event
self.addEventListener('fetch', event => {
    // Conversion, upload, download, and API requests must always reach Flask.
    if (event.request.method !== 'GET' ||
        event.request.url.includes('/api/') ||
        event.request.url.includes('/upload/') ||
        event.request.url.includes('/convert/')) {
        return;
    }

    event.respondWith(
        fetch(event.request)
            .then(response => {
                if (response && response.ok && response.type === 'basic') {
                    const copy = response.clone();
                    caches.open(CACHE_NAME).then(cache => cache.put(event.request, copy));
                }
                return response;
            })
            .catch(() => caches.match(event.request).then(cached => {
                if (cached) return cached;
                if (event.request.mode === 'navigate') {
                    return caches.match('/static/offline.html');
                }
                return new Response('', { status: 503, statusText: 'Offline' });
            }))
    );
});
