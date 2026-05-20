# 🩺 NurseAI - Your Living AI Health Companion

<div align="center">

**An emotionally intelligent AI co-care health companion designed to foster genuine human-AI partnership for health and wellness**
## Hackathon: Vibeathon - Polaris School of Technology x Replit
## Team: Exo-p01
## Team members: Aanand Pandit, Ch. Pranay Varna

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Latest-336791.svg)](https://www.postgresql.org/)
[![Perplexity AI](https://img.shields.io/badge/Perplexity-AI-purple.svg)](https://www.perplexity.ai/)

</div>

---

## 📖 Introduction

NurseAI is more than just a health tracking app—it's a living, emotionally responsive AI companion that evolves with you throughout your health journey. Built with the philosophy of creating genuine attachment rather than just usage, NurseAI combines cutting-edge AI technology with thoughtful UX design to provide personalized health support, routine management, medical history tracking, and intelligent health insights.

The project emphasizes:
- 🫀 **Emotional Intelligence**: Your AI nurse responds to your behavior with 10 distinct emotions
- 🎯 **Co-Care Partnership**: Work together with your AI companion, not just use a tool
- 📊 **Real-Time Analytics**: Comprehensive insights into your health routines and progress
- 🔔 **Smart Reminders**: Intelligent notification system with musical chimes and browser notifications
- 💬 **AI-Powered Assistance**: First-aid tips and health advice powered by Perplexity AI

---

## ✨ Features

### 🎨 **Emotionally Adaptive Dashboard**
- **10-Emotion System**: Your nurse displays Happy, Proud, Worried, Sad, Energetic, Frustrated, Calm, Sleepy, Excited, or Disappointed based on your behavior
- **Living Animations**: Heartbeat pulse, breathing effects, and animated GIFs for micro-interactions
- **Dynamic Theming**: UI adapts based on both user and nurse emotional states
- **Personalized Greetings**: AI-generated context-aware welcome messages

### 📊 **Comprehensive Analytics**
- **6-Stat Dashboard Grid**:
  - ✅ Completed routines today
  - ⏰ Coming reminders (scheduled for later)
  - ❌ Missed reminders (past times, not completed)
  - 📝 Total routines count
  - 🔥 Day streak tracking
  - 💯 Co-Care Score
- **7-Day Analytics Chart**: Visual representation of your weekly routine completions
- **Nurse Mode Scale**: 1-10 scale showing your nurse's energy and engagement level

### 📅 **Co-Care Planner**
- **Routine Management**: Create, edit, and track daily health routines
- **Expanded Categories**: Exercise, Meditation, Nutrition, Hydration, Sleep, Medication, Self-Care, Hobbies
- **Duration Tracking**: Set and monitor time spent on each activity
- **Smart Reminders**: Browser notifications with musical chime sounds
- **Celebration Animations**: Animated GIFs and sounds when completing tasks
- **Snooze Functionality**: 15-minute snooze for busy moments
- **One-Click Completion**: Complete routines directly from reminder pop-ups

### 🏥 **Medical History Management**
- **Comprehensive Records**: Track symptoms, diagnoses, treatments, and reflections
- **File Attachments**: Upload medical documents and images
- **AI Reflections**: Get intelligent insights on your medical history
- **View Full Details**: Modal view for complete record information
- **JSON Export**: Download all medical history for backup or portability

### 💬 **First-Aid Co-Assist**
- **AI Chat Interface**: Powered by Perplexity AI for accurate health information
- **Quick Tips UI**: Instant symptom analysis and first-aid guidance
- **Markdown Support**: Rich formatted responses with proper styling
- **Citation Cleaning**: Natural reading experience without reference markers

### 📝 **Co-Reflection & Growth**
- **Weekly Journal**: Document thoughts, feelings, and health observations
- **AI-Powered Insights**: Personalized analysis of your reflections
- **Preference Learning**: System learns and adapts to your needs
- **Mood Tracking**: Select and track your emotional state

### 🎯 **Enhanced Onboarding**
- **Interactive Setup**: Co-create your health journey from day one
- **Nurse Naming**: Personalize your AI companion
- **10 Avatar Choices**: Select from diverse, professionally designed avatars
- **Preference Settings**: Customize communication style and notification preferences
- **Guided Tour**: Interactive tooltips with pulsing highlights and directional arrows

### 🔔 **Real-Time Reminder System**
- **10-Second Checking**: Near-instant alerts (reduced from 30 seconds)
- **Live Badge Icon**: Animated bell showing upcoming reminder count
- **Musical Chimes**: Web Audio API-generated notification sounds
- **Browser Notifications**: Native alerts when tab is hidden
- **Time-Based Triggering**: Precise matching of scheduled vs. current time

### 🔐 **Authentication & Security**
- **Replit Auth Integration**: Login via Google, GitHub, or email/password
- **Session Management**: Secure user sessions with Flask-Login
- **Environment Secrets**: Proper API key and secret management

---

## 🛠️ Technology Stack

### **Backend**
- **Python 3.11+**: Core application language
- **Flask 3.0+**: Web framework
- **SQLAlchemy**: ORM for database operations
- **PostgreSQL**: Primary database (Neon-backed on Replit)
- **Gunicorn**: Production WSGI server

### **Frontend**
- **HTML5/CSS3**: Modern semantic markup and styling
- **JavaScript (ES6+)**: Dynamic interactions and API calls
- **Tailwind CSS**: Utility-first CSS framework
- **Google Material Icons**: Professional iconography
- **marked.js**: Markdown rendering for AI responses

### **AI & APIs**
- **Perplexity AI**: Exclusive AI provider for all features
  - Model: `sonar` (general queries and responses)
  - Personalized greetings, chat, medical info, weekly insights
- **Web Audio API**: Programmatic sound generation

### **Authentication**
- **Replit Auth**: OAuth integration for seamless login
- **Flask-Login**: Session management
- **Flask-Dance**: OAuth handling

---

## 🚀 Installation & Setup

### **Prerequisites**
- Python 3.11 or higher
- PostgreSQL database
- Perplexity API key
- Replit account (for Replit Auth)

### **Environment Variables**

Create a `.env` file or set the following environment variables:

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@host:port/database
PGHOST=your_host
PGPORT=5432
PGUSER=your_user
PGPASSWORD=your_password
PGDATABASE=your_database

# API Keys
OPENAI_API_KEY=your_openai_key  # Not used, kept for compatibility
PERPLEXITY_API_KEY=your_perplexity_key  # Required

# Session Security
SESSION_SECRET=your_random_secret_key

# Replit Configuration (if using Replit Auth)
REPLIT_DB_URL=your_replit_db_url
```

### **Installation Steps**

1. **Clone the Repository**
```bash
git clone <your-repo-url>
cd nurseai
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Set Up Database**

Using the provided schema file:
```bash
python database_schema.py
```

To view schema information:
```bash
python database_schema.py --info
```

To verify the schema matches the application models, you can compare the created tables with `models.py`.

Or let the application auto-create tables on first run (recommended for Replit environment).

4. **Configure Environment**

Set all required environment variables (see above).

5. **Run the Application**

**Development:**
```bash
python main.py
```

**Production:**
```bash
gunicorn --bind=0.0.0.0:5000 --reuse-port app:app
```

6. **Access the Application**

Open your browser to `http://localhost:5000`

---

## 🧪 Running Locally (Quick Start)

1. Copy `.env.example` to `.env` and edit values as needed.

```bash
cp .env.example .env
```

2. Create and activate a virtual environment, install deps:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Run the app:

```bash
python main.py
```

4. Open `http://localhost:5000` and click **Login** to use the built-in developer login.

---

## 📁 Project Structure

```
nurseai/
│
├── templates/              # HTML templates
│   ├── base.html          # Base template with navigation
│   ├── dashboard.html     # Main dashboard with analytics
│   ├── planner.html       # Routine planner
│   ├── medical_history.html  # Medical records
│   ├── chat.html          # AI chat interface
│   ├── reflections.html   # Weekly journal
│   ├── onboarding.html    # Initial setup flow
│   └── login.html         # Authentication page
│
├── static/                # Static assets
│   ├── css/
│   │   ├── animations.css    # Keyframe animations
│   │   ├── theme.css         # Color theming
│   │   ├── tour.css          # Onboarding tour styles
│   │   ├── help.css          # Help modal styles
│   │   └── z-index.css       # Centralized z-index variables
│   ├── js/
│   │   ├── app.js            # Core app functions
│   │   ├── notifications.js  # Notification system
│   │   ├── theme.js          # Dark mode toggle
│   │   ├── tour.js           # Onboarding tour
│   │   └── help.js           # Help modal
│   └── assets/
│       └── nurse/
│           ├── avatars/      # 10 nurse avatar images
│           └── animations/   # Celebration GIFs
│
├── models.py              # SQLAlchemy database models
├── routes.py              # Flask route handlers
├── app.py                 # Application factory
├── main.py                # Entry point
├── database_schema.py     # Standalone schema creator
├── requirements.txt       # Python dependencies
├── replit.md             # Project documentation
└── README.md             # This file
```

---

## 🔌 API Endpoints

### **Authentication**
- `GET /` - Landing page / redirect to dashboard
- `GET /login` - Login page
- `GET /logout` - Logout and clear session

### **Dashboard**
- `GET /dashboard` - Main dashboard with analytics
- `POST /api/update-mood` - Update user mood
- `POST /api/select-emotion` - Select emotion and get AI tips

### **Routines**
- `GET /planner` - Routine planner page
- `POST /api/add-routine` - Create new routine
- `POST /api/edit-routine/<id>` - Update routine
- `POST /api/delete-routine/<id>` - Delete routine
- `POST /api/complete-routine` - Mark routine as completed
- `GET /api/check-reminders` - Get upcoming reminders
- `POST /api/snooze-reminder/<id>` - Snooze reminder for 15 minutes

### **Medical History**
- `GET /medical-history` - Medical records page
- `POST /api/add-medical-record` - Create new medical record
- `GET /api/view-medical-record/<id>` - Get full record details
- `GET /api/download-medical-history` - Export all records as JSON

### **Chat**
- `GET /chat` - AI chat interface
- `POST /api/chat` - Send message and get AI response

### **Reflections**
- `GET /reflections` - Weekly journal page
- `POST /api/add-reflection` - Create new reflection

### **Onboarding**
- `GET /onboarding` - Initial setup flow
- `POST /api/complete-onboarding` - Finalize setup

### **Profile**
- `POST /api/update-profile` - Update user preferences

---

## 🎮 Usage Guide

### **Getting Started**

1. **Sign Up**: Use Google, GitHub, or email to create an account
2. **Onboarding**: Complete the interactive setup:
   - Choose your nurse's name
   - Select from 10 unique avatars
   - Set your preferences
3. **Dashboard**: View your health overview and analytics
4. **Create Routines**: Add daily health activities in the Planner
5. **Enable Reminders**: Set times and enable notifications
6. **Track Progress**: Watch your streak grow and Co-Care Score improve

### **Key Workflows**

**Daily Routine Management:**
1. Go to Planner
2. Click "Add New Routine"
3. Fill in title, category, duration
4. Set reminder time and enable notifications
5. Complete routines throughout the day
6. View stats: total completed, missed today

**Medical History Tracking:**
1. Navigate to Medical History
2. Click "Add Record"
3. Fill in symptoms, diagnosis, treatment
4. Upload files if needed
5. Add personal reflection
6. View full details anytime
7. Download all records as JSON for backup

**AI Chat Assistance:**
1. Go to Chat page
2. Ask health-related questions
3. Get instant AI-powered responses
4. Responses formatted in Markdown
5. Click quick tips for common symptoms

**Weekly Reflection:**
1. Visit Reflections page
2. Write your weekly journal entry
3. Get AI-generated insights
4. Track emotional patterns over time

### **Understanding Your Dashboard**

- **Completed**: Routines finished today
- **Coming**: Reminders scheduled for later today
- **Missed**: Routines with past times you haven't completed
- **Total**: All your active routines
- **Streak**: Consecutive days with at least one completion
- **Co-Care Score**: Overall engagement level (0-100)

---

## 🧠 AI Features

### **Perplexity AI Integration**

All AI features use **Perplexity's `sonar` model** exclusively:

1. **Personalized Greetings**: Context-aware welcome messages based on time, mood, and activity
2. **Chat Responses**: Medical information, health tips, and general wellness advice
3. **Improvement Tips**: 3-4 personalized suggestions after emotion selection
4. **Weekly Insights**: Analysis of reflection journal entries
5. **Symptom Analysis**: Quick first-aid guidance for common health concerns

### **Citation Cleaning**

All Perplexity responses have citation markers automatically removed for natural reading.

---

## 🎨 Design Philosophy

### **Gen-Z Vibecoding**
- Emojis throughout the interface
- Gradient backgrounds and cards
- Micro-interactions and animations
- Warm, supportive, non-judgmental tone

### **Living UI**
- Heartbeat animations
- Breathing effects
- Emotional reactions to user behavior
- Celebration GIFs on achievements

### **Genuine Attachment**
The goal is to create a companion you care about, not just a tool you use. Every interaction is designed to feel human, warm, and encouraging.

---

## 🔒 Security & Privacy

- **Encrypted Connections**: All API calls over HTTPS
- **Secure Sessions**: Flask-Login with secure cookies
- **Environment Secrets**: API keys never exposed in code
- **Input Validation**: Client and server-side validation
- **SQL Injection Protection**: SQLAlchemy ORM prevents attacks
- **XSS Prevention**: Proper escaping and sanitization

---

## 📊 Database Schema

The application uses PostgreSQL with the following main tables:

- **users**: User accounts and profiles
- **nurse_profiles**: AI nurse personality and state
- **routines**: Daily health routines and schedules
- **routine_completions**: Completion history
- **user_moods**: Mood tracking data
- **medical_history**: Health records and documents
- **reflections**: Weekly journal entries
- **chat_messages**: AI conversation history

For detailed schema with field types and relationships, see `database_schema.py`.

---

## 🚢 Deployment

### **Replit Deployment**

This project is optimized for Replit:

1. Configure deployment target in `.replit` file
2. Set environment secrets in Replit Secrets tab
3. Click "Deploy" button
4. Application runs on Gunicorn in production

### **External Deployment**

For deployment outside Replit:

1. Set up PostgreSQL database
2. Run `python database_schema.py` to create tables
3. Configure environment variables
4. Use Gunicorn or similar WSGI server:
   ```bash
   gunicorn --bind=0.0.0.0:5000 --workers=4 --reuse-port app:app
   ```

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Test thoroughly
5. Commit with clear messages: `git commit -m 'Add amazing feature'`
6. Push to your fork: `git push origin feature/amazing-feature`
7. Open a Pull Request

### **Development Guidelines**

- Follow PEP 8 style guide for Python
- Use meaningful variable and function names
- Add comments for complex logic
- Test all API endpoints
- Ensure responsive design works on mobile
- Maintain the emotional, supportive tone

---

## 🐛 Troubleshooting

### **Common Issues**

**Reminders not appearing:**
- Check browser notification permissions
- Ensure routines have reminder_enabled=True
- Verify time format is HH:MM

**AI responses failing:**
- Verify PERPLEXITY_API_KEY is set correctly
- Check API key has sufficient credits
- Review console logs for error details

**Database connection errors:**
- Confirm DATABASE_URL is correct
- Check PostgreSQL is running
- Verify credentials and permissions

**Styles not loading:**
- Clear browser cache
- Check static file paths in templates
- Verify Tailwind CDN is accessible

---

## 📈 Future Enhancements

Potential features for future development:

- [ ] Mobile native apps (iOS/Android)
- [ ] Health metrics integration (Apple Health, Google Fit)
- [ ] Multi-language support
- [ ] Voice interaction with nurse
- [ ] Community features (support groups)
- [ ] Telehealth integration
- [ ] Advanced analytics and predictions
- [ ] Wearable device synchronization
- [ ] Family sharing and collaborative care
- [ ] Insurance integration

---

## 📄 License

This project is open source and available under the MIT License.

---

## 🙏 Acknowledgments

- **Perplexity AI**: For powering all AI features with their excellent API
- **Replit**: For hosting, authentication, and database infrastructure
- **Flask Community**: For the robust web framework
- **Tailwind CSS**: For the utility-first styling approach
- **Google Material Icons**: For professional iconography

---

## 📞 Support

For questions, issues, or feature requests:

- Open an issue on GitHub
- Contact via email (add your email)
- Join our community discussions (add link)

---

## 💡 Conclusion

NurseAI represents a new paradigm in health technology—one where AI doesn't just process data but forms genuine partnerships with users. By combining emotional intelligence, beautiful design, and powerful AI, we've created more than an app; we've created a companion that truly cares about your wellbeing.

Whether you're managing chronic conditions, building healthy habits, or simply want a supportive presence in your wellness journey, NurseAI is here for you—24/7, always caring, always evolving.

**Start your journey today. Your AI health companion is waiting to meet you.** 🫀

---

<div align="center">

**Made with 💙 for better health and wellness**

[Website](#) | [Documentation](#) | [API Docs](#) | [Community](#)

</div>
