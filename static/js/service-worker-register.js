if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/service-worker.js', {scope: '/'})
        .then(reg => {
            console.log('Service Worker registered:', reg);
        })
        .catch(err => {
            console.log('Service Worker registration failed:', err);
        });
}

// Install prompt
let deferredPrompt;
const installBtn = document.getElementById('installBtn');

window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;

    if (installBtn) {
        installBtn.hidden = false;
    }
});

if (installBtn) {
    installBtn.addEventListener('click', async () => {
        if (!deferredPrompt) return;
        deferredPrompt.prompt();
        const choiceResult = await deferredPrompt.userChoice;
        if (choiceResult.outcome === 'accepted') {
            installBtn.hidden = true;
        }
        deferredPrompt = null;
    });
}

window.addEventListener('appinstalled', () => {
    deferredPrompt = null;
    if (installBtn) {
        installBtn.hidden = true;
    }
});

// iOS does not emit beforeinstallprompt; the app remains installable from Safari's
// Share menu and should not show a misleading button there.
if (window.matchMedia('(display-mode: standalone)').matches) {
    if (installBtn) installBtn.hidden = true;
}
