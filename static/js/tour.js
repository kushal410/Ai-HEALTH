const TOUR_STEPS = [
    {
        target: '#greeting',
        title: 'Welcome to NurseAI! 👋',
        content: 'This is your personalized dashboard where your AI nurse companion greets you daily.',
        position: 'bottom'
    },
    {
        target: '.mood-btn',
        title: 'Daily Mood Check-in 💭',
        content: 'Share how you\'re feeling each day. Your nurse adapts their mood and energy based on yours!',
        position: 'bottom'
    },
    {
        target: '[data-tour="nurse-emotion"]',
        title: 'Your Nurse\'s Feelings 💙',
        content: 'Your nurse has emotions too! They feel happy when you complete tasks, worried when you miss routines, and proud of your streaks.',
        position: 'left'
    },
    {
        target: '[data-tour="co-care-score"]',
        title: 'Co-Care Score 🌟',
        content: 'This score reflects your relationship health with your nurse. Higher engagement = stronger bond!',
        position: 'left'
    },
    {
        target: '[href="/planner"]',
        title: 'Co-Care Planner 📋',
        content: 'Create and manage your health routines together. Set reminders for medications, hydration, exercise, and more!',
        position: 'bottom'
    },
    {
        target: '[href="/first-aid"]',
        title: 'First-Aid Co-Assist 🚑',
        content: 'Need health advice? Chat with your AI nurse for guidance. Emergency mode available for urgent situations.',
        position: 'bottom'
    },
    {
        target: '[href="/medical-history"]',
        title: 'Medical History 📄',
        content: 'Upload and manage your medical records. Your nurse can review them to provide personalized care.',
        position: 'bottom'
    },
    {
        target: '.nav-profile-btn',
        title: 'Your Profile Menu 👤',
        content: 'Click here to access your profile, reflections, and settings. Let me show you!',
        position: 'left',
        action: 'open_profile'
    },
    {
        target: '[href="/reflection"]',
        title: 'Co-Reflection & Growth 🌱',
        content: 'Weekly journaling where you and your nurse reflect on your health journey, set goals, and track emotional patterns.',
        position: 'left'
    },
    {
        target: '[href="/settings"]',
        title: 'Settings ⚙️',
        content: 'Customize your nurse\'s personality, avatar, care style, and app preferences to make this experience truly yours.',
        position: 'left'
    }
];

class OnboardingTour {
    constructor() {
        this.currentStep = 0;
        this.isActive = false;
        this.overlay = null;
        this.tooltip = null;
    }

    start(serverCompleted = false) {
        if (localStorage.getItem('tourCompleted') === 'true' || serverCompleted) {
            return;
        }
        
        this.isActive = true;
        this.currentStep = 0;
        this.createOverlay();
        this.showStep();
    }

    createOverlay() {
        this.overlay = document.createElement('div');
        this.overlay.className = 'tour-overlay';
        this.overlay.innerHTML = `
            <div class="tour-backdrop"></div>
        `;
        document.body.appendChild(this.overlay);

        this.tooltip = document.createElement('div');
        this.tooltip.className = 'tour-tooltip';
        document.body.appendChild(this.tooltip);
    }

    showStep() {
        const step = TOUR_STEPS[this.currentStep];
        
        // Handle profile dropdown opening for profile-related steps
        if (step.action === 'open_profile' || step.target === '.nav-profile-btn' || step.target === '[href="/reflection"]' || step.target === '[href="/settings"]') {
            const dropdown = document.getElementById('profileDropdown');
            if (dropdown && dropdown.classList.contains('hidden')) {
                dropdown.classList.remove('hidden');
            }
        } else {
            // Close dropdown for other steps
            const dropdown = document.getElementById('profileDropdown');
            if (dropdown && !dropdown.classList.contains('hidden')) {
                dropdown.classList.add('hidden');
            }
        }
        
        const target = document.querySelector(step.target);

        if (!target) {
            this.nextStep();
            return;
        }

        target.classList.add('tour-highlight');
        target.scrollIntoView({ behavior: 'smooth', block: 'center' });

        setTimeout(() => {
            this.positionTooltip(target, step);
        }, 300);
    }

    positionTooltip(target, step) {
        const rect = target.getBoundingClientRect();
        const tooltip = this.tooltip;

        tooltip.innerHTML = `
            <div class="tour-tooltip-content">
                <h3 class="tour-tooltip-title">${step.title}</h3>
                <p class="tour-tooltip-text">${step.content}</p>
                <div class="tour-tooltip-footer">
                    <div class="tour-progress">
                        Step ${this.currentStep + 1} of ${TOUR_STEPS.length}
                    </div>
                    <div class="tour-buttons">
                        <button onclick="tour.skip()" class="tour-btn-skip">Skip Tour</button>
                        ${this.currentStep > 0 ? '<button onclick="tour.previousStep()" class="tour-btn-prev">Previous</button>' : ''}
                        <button onclick="tour.nextStep()" class="tour-btn-next">
                            ${this.currentStep === TOUR_STEPS.length - 1 ? 'Finish' : 'Next'}
                        </button>
                    </div>
                </div>
            </div>
        `;

        tooltip.style.display = 'block';

        let top, left;
        const tooltipRect = tooltip.getBoundingClientRect();

        switch (step.position) {
            case 'bottom':
                top = rect.bottom + 20;
                left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
                break;
            case 'top':
                top = rect.top - tooltipRect.height - 20;
                left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
                break;
            case 'left':
                top = rect.top + (rect.height / 2) - (tooltipRect.height / 2);
                left = rect.left - tooltipRect.width - 20;
                break;
            case 'right':
                top = rect.top + (rect.height / 2) - (tooltipRect.height / 2);
                left = rect.right + 20;
                break;
        }

        tooltip.style.top = `${Math.max(10, top)}px`;
        tooltip.style.left = `${Math.max(10, Math.min(left, window.innerWidth - tooltipRect.width - 10))}px`;
    }

    nextStep() {
        this.clearHighlight();

        if (this.currentStep < TOUR_STEPS.length - 1) {
            this.currentStep++;
            this.showStep();
        } else {
            this.complete();
        }
    }

    previousStep() {
        this.clearHighlight();

        if (this.currentStep > 0) {
            this.currentStep--;
            this.showStep();
        }
    }

    skip() {
        if (confirm('Are you sure you want to skip the tour? You can replay it anytime from Settings.')) {
            localStorage.setItem('tourCompleted', 'true');
            this.complete();
        }
    }

    complete() {
        this.clearHighlight();
        
        if (this.overlay) {
            this.overlay.remove();
        }
        if (this.tooltip) {
            this.tooltip.remove();
        }

        this.isActive = false;
        
        localStorage.setItem('tourCompleted', 'true');
        fetch('/api/complete-tour', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
    }

    clearHighlight() {
        document.querySelectorAll('.tour-highlight').forEach(el => {
            el.classList.remove('tour-highlight');
        });
    }

    replay() {
        this.currentStep = 0;
        localStorage.removeItem('tourCompleted');
        this.start(false);
    }
}

const tour = new OnboardingTour();

window.startTourIfNeeded = function(serverCompleted) {
    if (window.location.pathname === '/dashboard') {
        setTimeout(() => tour.start(serverCompleted), 1000);
    }
};
