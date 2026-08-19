// Main application logic
document.addEventListener('DOMContentLoaded', function() {
    // Initialize notification system
    if (!window.notificationSystem) {
        window.notificationSystem = new NotificationSystem();
    }
    
    // Handle offline status
    window.addEventListener('offline', () => {
        showNotification('You are offline. Some features may not be available.', 'warning');
    });
    
    window.addEventListener('online', () => {
        showNotification('You are back online.', 'success');
    });
});

// Job polling
function pollJobStatus(jobId, callback) {
    const poll = setInterval(() => {
        fetch(`/convert/status/${jobId}`)
            .then(r => r.json())
            .then(data => {
                callback(data);
                
                if (data.status === 'completed' || data.status === 'failed') {
                    clearInterval(poll);
                }
            })
            .catch(e => {
                console.error('Error polling job status:', e);
            });
    }, 2000); // Poll every 2 seconds
    
    return poll;
}

// Format size display
function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Format time
function formatTime(date) {
    return new Date(date).toLocaleString();
}
