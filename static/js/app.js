function showCelebration(element) {
    element.classList.add('celebrate');
    setTimeout(() => {
        element.classList.remove('celebrate');
    }, 600);
}

function showNotification(message, type = 'success', autoRemove = true, position = 'top') {
    const notification = document.createElement('div');
    
    // Position classes
    const positionClass = position === 'bottom' ? 'bottom-4 right-4' : 'top-4 right-4';
    
    // Type colors
    let bgColor;
    switch(type) {
        case 'success':
            bgColor = 'bg-green-500';
            break;
        case 'error':
            bgColor = 'bg-red-500';
            break;
        case 'info':
            bgColor = 'bg-blue-500';
            break;
        default:
            bgColor = 'bg-gray-500';
    }
    
    notification.className = `fixed ${positionClass} p-4 rounded-lg shadow-lg ${bgColor} text-white z-50 transition-opacity`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    if (autoRemove) {
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
    
    return notification;
}

if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission();
}

// Profile menu toggle
function toggleProfileMenu(event) {
    // Stop this click from reaching the document click handler
    event.stopPropagation();

    const dropdown = document.getElementById('profileDropdown');
    if (dropdown) {
        dropdown.classList.toggle('hidden');
    }
}

// Close dropdown when clicking outside
document.addEventListener('DOMContentLoaded', function() {
    document.addEventListener('click', function(event) {
        const dropdown = document.getElementById('profileDropdown');
        const button = document.querySelector('.nav-profile-btn');

        if (dropdown && button) {
            // Close only if click is outside both button and dropdown
            if (!button.contains(event.target) && !dropdown.contains(event.target)) {
                dropdown.classList.add('hidden');
            }
        }
    });
});

// Language update function
function updateLanguage(lang) {
    fetch('/api/update-profile', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({language: lang})
    }).then(() => {
        location.reload();
    });
}
