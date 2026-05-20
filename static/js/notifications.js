// Notification System with Sound Alerts
class NotificationSystem {
    constructor() {
        this.audioContext = null;
        this.permissionGranted = false;
        this.checkPermission();
    }

    async checkPermission() {
        if ('Notification' in window) {
            if (Notification.permission === 'granted') {
                this.permissionGranted = true;
            } else if (Notification.permission !== 'denied') {
                const permission = await Notification.requestPermission();
                this.permissionGranted = (permission === 'granted');
            }
        }
    }

    async requestPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            const permission = await Notification.requestPermission();
            this.permissionGranted = (permission === 'granted');
            return this.permissionGranted;
        }
        return this.permissionGranted;
    }

    // Generate notification sound using Web Audio API
    playNotificationSound(type = 'gentle') {
        if (!this.audioContext) {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        }

        const ctx = this.audioContext;
        const now = ctx.currentTime;

        // Create oscillator and gain nodes
        const oscillator = ctx.createOscillator();
        const gainNode = ctx.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(ctx.destination);

        // Different sound types
        switch(type) {
            case 'gentle': // Soft chime
                oscillator.frequency.setValueAtTime(800, now);
                oscillator.frequency.exponentialRampToValueAtTime(400, now + 0.3);
                gainNode.gain.setValueAtTime(0.3, now);
                gainNode.gain.exponentialRampToValueAtTime(0.01, now + 0.3);
                oscillator.start(now);
                oscillator.stop(now + 0.3);
                break;

            case 'alert': // Urgent alert
                oscillator.frequency.setValueAtTime(1200, now);
                gainNode.gain.setValueAtTime(0.4, now);
                gainNode.gain.exponentialRampToValueAtTime(0.01, now + 0.2);
                oscillator.start(now);
                oscillator.stop(now + 0.2);
                
                // Second beep
                setTimeout(() => {
                    const osc2 = ctx.createOscillator();
                    const gain2 = ctx.createGain();
                    osc2.connect(gain2);
                    gain2.connect(ctx.destination);
                    osc2.frequency.setValueAtTime(1200, ctx.currentTime);
                    gain2.gain.setValueAtTime(0.4, ctx.currentTime);
                    gain2.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.2);
                    osc2.start();
                    osc2.stop(ctx.currentTime + 0.2);
                }, 300);
                break;

            case 'success': // Success bell
                oscillator.type = 'sine';
                oscillator.frequency.setValueAtTime(523.25, now); // C5
                oscillator.frequency.setValueAtTime(659.25, now + 0.1); // E5
                oscillator.frequency.setValueAtTime(783.99, now + 0.2); // G5
                gainNode.gain.setValueAtTime(0.3, now);
                gainNode.gain.exponentialRampToValueAtTime(0.01, now + 0.5);
                oscillator.start(now);
                oscillator.stop(now + 0.5);
                break;

            case 'celebration': // Cheerful celebration
                const notes = [523.25, 659.25, 783.99, 1046.50]; // C-E-G-C chord
                notes.forEach((freq, i) => {
                    setTimeout(() => {
                        const osc = ctx.createOscillator();
                        const gain = ctx.createGain();
                        osc.connect(gain);
                        gain.connect(ctx.destination);
                        osc.frequency.setValueAtTime(freq, ctx.currentTime);
                        gain.gain.setValueAtTime(0.2, ctx.currentTime);
                        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.3);
                        osc.start();
                        osc.stop(ctx.currentTime + 0.3);
                    }, i * 100);
                });
                break;
        }
    }

    // Show browser notification
    showNotification(title, options = {}) {
        if (!this.permissionGranted) {
            console.log('Notification permission not granted');
            return;
        }

        const defaultOptions = {
            icon: '/static/assets/nurse/avatars/avatar-1.png',
            badge: '/static/assets/nurse/avatars/avatar-1.png',
            vibrate: [200, 100, 200],
            requireInteraction: false,
            ...options
        };

        const notification = new Notification(title, defaultOptions);

        notification.onclick = function(event) {
            event.preventDefault();
            window.focus();
            notification.close();
        };

        return notification;
    }

    // Schedule routine reminder
    scheduleReminder(routine) {
        if (!routine.time || !routine.reminder_enabled) return;

        const [hours, minutes] = routine.time.split(':').map(Number);
        const now = new Date();
        const scheduledTime = new Date();
        scheduledTime.setHours(hours, minutes, 0, 0);

        // If time has passed today, schedule for tomorrow
        if (scheduledTime <= now) {
            scheduledTime.setDate(scheduledTime.getDate() + 1);
        }

        const timeUntilReminder = scheduledTime - now;

        setTimeout(() => {
            this.playNotificationSound('gentle');
            this.showNotification('Routine Reminder', {
                body: `Time for: ${routine.title}`,
                tag: `routine-${routine.id}`
            });

            // Schedule next day's reminder
            this.scheduleReminder(routine);
        }, timeUntilReminder);
    }

    // Show celebration with GIF and sound
    showCelebration(emotion = 'happy') {
        this.playNotificationSound('celebration');

        const overlay = document.createElement('div');
        overlay.className = 'fixed inset-0 flex items-center justify-center z-50 pointer-events-none celebration-overlay';
        overlay.style.animation = 'fadeIn 0.3s ease';

        const animations = {
            'happy': 'congratulations.gif',
            'excited': 'glitter-sparkle.gif',
            'proud': 'thumbs-up.gif',
            'calm': 'breathing.gif'
        };

        const gifFile = animations[emotion] || 'congratulations.gif';

        overlay.innerHTML = `
            <div class="celebration-container">
                <img src="/static/assets/nurse/animations/${gifFile}" 
                     alt="Celebration!" 
                     class="celebration-gif">
                <div class="celebration-text">Great Job!</div>
            </div>
        `;

        document.body.appendChild(overlay);

        setTimeout(() => {
            overlay.style.animation = 'fadeOut 0.3s ease';
            setTimeout(() => overlay.remove(), 300);
        }, 3000);
    }
}

// Create global instance
const notificationSystem = new NotificationSystem();

// Export for use in other scripts
window.notificationSystem = notificationSystem;
