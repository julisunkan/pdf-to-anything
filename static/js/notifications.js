class NotificationSystem {
    constructor() {
        this.container = document.getElementById('notifications');
        this.timeout = 5000; // 5 seconds
    }
    
    show(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        this.container.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, this.timeout);
    }
    
    success(message) {
        this.show(message, 'success');
    }
    
    error(message) {
        this.show(message, 'error');
    }
    
    warning(message) {
        this.show(message, 'warning');
    }
    
    info(message) {
        this.show(message, 'info');
    }
}

window.showNotification = function(message, type = 'info') {
    if (!window.notificationSystem) {
        window.notificationSystem = new NotificationSystem();
    }
    window.notificationSystem.show(message, type);
};
