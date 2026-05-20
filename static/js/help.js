class HelpCenter {
    constructor() {
        this.modal = null;
        this.isOpen = false;
        this.currentSection = 'faqs';
    }

    open(section = 'faqs') {
        if (this.isOpen) return;
        
        this.currentSection = section;
        this.createModal();
        this.isOpen = true;
    }

    close() {
        if (this.modal) {
            this.modal.remove();
            this.modal = null;
        }
        this.isOpen = false;
    }

    createModal() {
        this.modal = document.createElement('div');
        this.modal.className = 'help-modal-overlay';
        this.modal.innerHTML = `
            <div class="help-modal">
                <div class="help-header">
                    <h2>🩺 Help Center</h2>
                    <button class="help-close" onclick="helpCenter.close()">✕</button>
                </div>
                
                <div class="help-tabs">
                    <button class="help-tab ${this.currentSection === 'faqs' ? 'active' : ''}" onclick="helpCenter.switchSection('faqs')">
                        FAQs
                    </button>
                    <button class="help-tab ${this.currentSection === 'guide' ? 'active' : ''}" onclick="helpCenter.switchSection('guide')">
                        Feature Guide
                    </button>
                    <button class="help-tab ${this.currentSection === 'support' ? 'active' : ''}" onclick="helpCenter.switchSection('support')">
                        Support
                    </button>
                </div>
                
                <div class="help-content">
                    ${this.getContent()}
                </div>
            </div>
        `;
        
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.close();
            }
        });
        
        document.body.appendChild(this.modal);
    }

    switchSection(section) {
        if (this.currentSection === section) return;
        
        this.currentSection = section;
        
        const tabs = this.modal.querySelectorAll('.help-tab');
        tabs.forEach(tab => {
            tab.classList.remove('active');
            if (tab.onclick.toString().includes(`'${section}'`)) {
                tab.classList.add('active');
            }
        });
        
        const contentDiv = this.modal.querySelector('.help-content');
        contentDiv.innerHTML = this.getContent();
    }

    getContent() {
        switch(this.currentSection) {
            case 'faqs':
                return this.getFAQs();
            case 'guide':
                return this.getGuide();
            case 'support':
                return this.getSupport();
            default:
                return this.getFAQs();
        }
    }

    getFAQs() {
        return `
            <div class="help-section">
                <div class="faq-item">
                    <h3>❓ What is NurseAI?</h3>
                    <p>NurseAI is your personal AI health companion that learns and evolves with you. Together, you co-create a health partnership that feels alive and adapts to your needs.</p>
                </div>
                
                <div class="faq-item">
                    <h3>💝 How does the Co-Care Score work?</h3>
                    <p>Your Co-Care Score reflects the health of your relationship with your AI nurse. It increases when you complete routines, check in regularly, and engage with your health journey.</p>
                </div>
                
                <div class="faq-item">
                    <h3>😊 Why does my nurse show different emotions?</h3>
                    <p>Your nurse has 10 distinct emotions based on your behavior patterns. She feels proud when you maintain streaks, worried when you miss routines, and excited when you set new goals. This emotional awareness makes the relationship feel genuine.</p>
                </div>
                
                <div class="faq-item">
                    <h3>🔒 Is my health data secure?</h3>
                    <p>Yes! Your health data is stored securely in an encrypted database. We use Replit Auth for secure login, and your medical records are only accessible to you.</p>
                </div>
                
                <div class="faq-item">
                    <h3>🌓 Can I change the app theme?</h3>
                    <p>Absolutely! Use the theme switcher in the top-right corner to choose Light, Dark, or Auto mode. Auto mode follows your system preferences.</p>
                </div>
                
                <div class="faq-item">
                    <h3>🔄 Can I replay the onboarding tour?</h3>
                    <p>Yes! You can replay the tour anytime. Just click the button below:</p>
                    <button class="replay-tour-btn" onclick="helpCenter.replayTour()">
                        🎯 Replay Onboarding Tour
                    </button>
                </div>
            </div>
        `;
    }

    getGuide() {
        return `
            <div class="help-section">
                <div class="feature-item">
                    <h3>🏠 Dashboard</h3>
                    <p>Your central hub for health monitoring. Check your nurse's mood, update your daily feelings, and see your Co-Care Score at a glance.</p>
                </div>
                
                <div class="feature-item">
                    <h3>📅 Co-Care Planner</h3>
                    <p>Manage your health routines including medicine, hydration, meals, sleep, and exercise. Complete tasks to build streaks and watch your nurse celebrate with you!</p>
                </div>
                
                <div class="feature-item">
                    <h3>🚑 First-Aid Co-Assist</h3>
                    <p>Chat with your AI nurse about health concerns. Toggle Emergency Mode for urgent situations. Your nurse uses advanced AI to provide helpful, personalized responses.</p>
                </div>
                
                <div class="feature-item">
                    <h3>📋 Medical History</h3>
                    <p>Upload and store your medical records, prescriptions, and health documents. Your nurse can review these to provide more personalized care.</p>
                </div>
                
                <div class="feature-item">
                    <h3>📝 Co-Reflection & Growth</h3>
                    <p>Weekly journaling space where you and your nurse reflect together. Your nurse learns your preferences and adapts to serve you better over time.</p>
                </div>
                
                <div class="feature-item">
                    <h3>⚙️ Settings</h3>
                    <p>Update your profile, change language preferences (English/Hindi), and customize your nurse's personality traits.</p>
                </div>
            </div>
        `;
    }

    getSupport() {
        return `
            <div class="help-section">
                <div class="support-item">
                    <h3>🎯 Take the Tour</h3>
                    <p>New to NurseAI? Take our interactive tour to learn all the features.</p>
                    <button class="replay-tour-btn" onclick="helpCenter.replayTour()">
                        Start Tour
                    </button>
                </div>
                
                <div class="support-item">
                    <h3>🐛 Found a Bug?</h3>
                    <p>We're constantly improving NurseAI. If you encounter any issues, please report them so we can make your experience better.</p>
                </div>
                
                <div class="support-item">
                    <h3>💡 Have a Suggestion?</h3>
                    <p>Your feedback helps NurseAI evolve. We'd love to hear your ideas for new features or improvements!</p>
                </div>
                
                <div class="support-item">
                    <h3>📚 About NurseAI</h3>
                    <p>NurseAI is built with love to create a genuine human-AI partnership for health and wellness. We believe in co-creation, emotional intelligence, and making healthcare feel alive and personal.</p>
                    <p class="support-version">Version 1.0.0 - Nov 2025</p>
                </div>
            </div>
        `;
    }

    replayTour() {
        this.close();
        if (typeof tour !== 'undefined') {
            tour.replay();
        }
    }
}

const helpCenter = new HelpCenter();

function openHelp(section = 'faqs') {
    helpCenter.open(section);
}
