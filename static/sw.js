// Service Worker para PWA - Sistema de Turnos Admin
const CACHE_NAME = 'turnos-admin-v1.2';
const OFFLINE_URL = '/mobile';

const urlsToCache = [
    '/mobile',
    '/manifest.json',
    '/static/icon-192.png',
    '/static/icon-512.png',
    '/api/turnos_semana',
    // Archivos críticos para funcionamiento offline
    OFFLINE_URL
];

// Instalar Service Worker
self.addEventListener('install', (event) => {
    console.log('[SW] Install event');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('[SW] Cache opened');
                return cache.addAll(urlsToCache);
            })
            .then(() => {
                // Forzar activación inmediata
                return self.skipWaiting();
            })
    );
});

// Activar Service Worker
self.addEventListener('activate', (event) => {
    console.log('[SW] Activate event');
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('[SW] Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => {
            // Tomar control inmediato
            return self.clients.claim();
        })
    );
});

// Interceptar requests
self.addEventListener('fetch', (event) => {
    // Solo manejar requests GET
    if (event.request.method !== 'GET') return;

    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                // Si está en cache, devolverlo
                if (response) {
                    console.log('[SW] Serving from cache:', event.request.url);
                    return response;
                }

                // Si no está en cache, intentar fetch
                return fetch(event.request)
                    .then((response) => {
                        // Solo cachear respuestas válidas
                        if (!response || response.status !== 200 || response.type !== 'basic') {
                            return response;
                        }

                        // Clonar respuesta para cache
                        const responseToCache = response.clone();

                        // Guardar en cache las APIs y páginas importantes
                        if (event.request.url.includes('/api/') ||
                            event.request.url.includes('/mobile') ||
                            event.request.url.includes('/static/')) {
                            caches.open(CACHE_NAME)
                                .then((cache) => {
                                    cache.put(event.request, responseToCache);
                                });
                        }

                        return response;
                    })
                    .catch(() => {
                        // Si falla la red, devolver página offline para navegación
                        if (event.request.mode === 'navigate') {
                            return caches.match(OFFLINE_URL);
                        }

                        // Para APIs, devolver respuesta JSON vacía
                        if (event.request.url.includes('/api/')) {
                            return new Response(
                                JSON.stringify({
                                    success: false,
                                    error: 'Sin conexión',
                                    offline: true
                                }),
                                {
                                    status: 503,
                                    headers: { 'Content-Type': 'application/json' }
                                }
                            );
                        }
                    });
            })
    );
});

// Manejar mensajes del cliente
self.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
});
