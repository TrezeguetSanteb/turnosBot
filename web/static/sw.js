// Service Worker para PWA con Notificaciones Push - TurnosBot Admin
const CACHE_NAME = 'turnos-admin-v2.0';
const OFFLINE_URL = '/mobile';

const urlsToCache = [
    '/mobile',
    '/manifest.json',
    '/static/icon-192.png',
    '/static/icon-512.png',
    '/api/turnos_semana',
    OFFLINE_URL
];

// Instalar Service Worker
self.addEventListener('install', (event) => {
    console.log('[SW] 📦 Instalando Service Worker con notificaciones...');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('[SW] Cache abierto');
                return cache.addAll(urlsToCache);
            })
            .then(() => {
                console.log('[SW] ✅ Service Worker instalado');
                return self.skipWaiting();
            })
    );
});

// Activar Service Worker
self.addEventListener('activate', (event) => {
    console.log('[SW] 🚀 Activando Service Worker...');
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('[SW] 🗑️ Eliminando cache antigua:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => {
            console.log('[SW] ✅ Service Worker activado');
            return self.clients.claim();
        })
    );
});

// 🔔 NOTIFICACIONES PUSH
self.addEventListener('push', (event) => {
    console.log('[SW] 📨 Notificación push recibida:', event);

    let notificationData = {
        title: '🔔 TurnosBot Admin',
        body: 'Nueva actividad en el sistema',
        icon: '/static/icon-192.png',
        badge: '/static/icon-192.png',
        tag: 'turno-notification',
        requireInteraction: true,
        data: { url: '/' }
    };

    // Procesar datos del push si existen
    if (event.data) {
        try {
            const pushData = event.data.json();
            notificationData = {
                title: pushData.title || '🔔 TurnosBot Admin',
                body: pushData.body || 'Nueva actividad',
                icon: '/static/icon-192.png',
                badge: '/static/icon-192.png',
                tag: pushData.tag || 'turno-notification',
                requireInteraction: pushData.important || false,
                data: {
                    url: pushData.url || '/',
                    turnoId: pushData.turnoId,
                    tipo: pushData.tipo,
                    timestamp: Date.now()
                },
                actions: pushData.actions || [
                    {
                        action: 'view',
                        title: '👀 Ver Panel',
                        icon: '/static/icon-192.png'
                    },
                    {
                        action: 'dismiss',
                        title: '❌ Cerrar'
                    }
                ]
            };
        } catch (e) {
            console.error('[SW] ❌ Error procesando datos push:', e);
        }
    }

    event.waitUntil(
        self.registration.showNotification(notificationData.title, notificationData)
    );
});

// 👆 CLICK EN NOTIFICACIONES
self.addEventListener('notificationclick', (event) => {
    console.log('[SW] 👆 Click en notificación:', event);

    event.notification.close();

    // Manejar acciones específicas
    if (event.action === 'dismiss') {
        return; // Solo cerrar la notificación
    }

    const urlToOpen = event.notification.data?.url || '/';

    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true })
            .then((clientList) => {
                // Buscar ventana existente del panel admin
                for (const client of clientList) {
                    if (client.url.includes(self.location.origin) && 'focus' in client) {
                        return client.focus();
                    }
                }

                // Abrir nueva ventana si no existe
                if (clients.openWindow) {
                    return clients.openWindow(urlToOpen);
                }
            })
    );
});

// 📥 MENSAJES DESDE EL CLIENTE
self.addEventListener('message', (event) => {
    console.log('[SW] 📥 Mensaje recibido:', event.data);

    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }

    if (event.data && event.data.type === 'GET_VERSION') {
        event.ports[0].postMessage({ version: CACHE_NAME });
    }
});

// Interceptar requests (funcionalidad básica de PWA)
self.addEventListener('fetch', (event) => {
    // Solo interceptar requests GET
    if (event.request.method !== 'GET') return;

    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                // Retornar cache si existe, sino fetch
                if (response) {
                    return response;
                }
                return fetch(event.request);
            })
            .catch(() => {
                // Si falla todo, mostrar página offline
                if (event.request.destination === 'document') {
                    return caches.match(OFFLINE_URL);
                }
            })
    );
});
