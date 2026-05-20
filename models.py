from datetime import datetime
from app import db
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from flask_login import UserMixin
from sqlalchemy import UniqueConstraint

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=True)
    first_name = db.Column(db.String, nullable=True)
    last_name = db.Column(db.String, nullable=True)
    profile_image_url = db.Column(db.String, nullable=True)
    
    name = db.Column(db.String, nullable=True)
    gender = db.Column(db.String, nullable=True)
    age = db.Column(db.Integer, nullable=True)
    dob = db.Column(db.Date, nullable=True)
    contact = db.Column(db.String, nullable=True)
    address = db.Column(db.Text, nullable=True)
    emergency_contact = db.Column(db.String, nullable=True)
    
    onboarding_completed = db.Column(db.Boolean, default=False)
    tour_completed = db.Column(db.Boolean, default=False)
    language = db.Column(db.String, default='en')
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.String, db.ForeignKey(User.id))
    browser_session_key = db.Column(db.String, nullable=False)
    user = db.relationship(User)

    __table_args__ = (UniqueConstraint(
        'user_id',
        'browser_session_key',
        'provider',
        name='uq_user_browser_session_key_provider',
    ),)

class NurseProfile(db.Model):
    __tablename__ = 'nurse_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey(User.id), unique=True)
    
    nurse_name = db.Column(db.String, nullable=False, default="NurseAI")
    nurse_avatar = db.Column(db.String, nullable=False, default="default")
    care_style = db.Column(db.String, nullable=False, default="balanced")
    tone_preference = db.Column(db.String, nullable=False, default="warm")
    emoji_level = db.Column(db.String, default="moderate")
    strictness_level = db.Column(db.String, default="balanced")
    
    current_mood = db.Column(db.String, default="happy")
    current_emotion = db.Column(db.String, default="calm")
    energy_level = db.Column(db.Integer, default=80)
    heartbeat_speed = db.Column(db.String, default="normal")
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    user = db.relationship(User, backref='nurse_profile')

class UserMood(db.Model):
    __tablename__ = 'user_moods'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey(User.id))
    
    mood = db.Column(db.String, nullable=False)
    mood_emoji = db.Column(db.String, nullable=False)
    note = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    user = db.relationship(User, backref='moods')

class Routine(db.Model):
    __tablename__ = 'routines'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey(User.id))
    
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String, nullable=False)
    time = db.Column(db.String, nullable=True)
    frequency = db.Column(db.String, default="daily")
    duration = db.Column(db.String, nullable=True)  # e.g., "7 days", "2 weeks", "ongoing"
    reminder_enabled = db.Column(db.Boolean, default=True)
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    user = db.relationship(User, backref='routines')

class RoutineCompletion(db.Model):
    __tablename__ = 'routine_completions'
    id = db.Column(db.Integer, primary_key=True)
    routine_id = db.Column(db.Integer, db.ForeignKey(Routine.id))
    user_id = db.Column(db.String, db.ForeignKey(User.id))
    
    completed_at = db.Column(db.DateTime, default=datetime.now)
    date = db.Column(db.Date, nullable=False)
    
    routine = db.relationship(Routine, backref='completions')
    user = db.relationship(User)

class MissedReminder(db.Model):
    __tablename__ = 'missed_reminders'
    id = db.Column(db.Integer, primary_key=True)
    routine_id = db.Column(db.Integer, db.ForeignKey(Routine.id))
    user_id = db.Column(db.String, db.ForeignKey(User.id))
    
    scheduled_time = db.Column(db.String, nullable=False)  # 24-hour format HH:MM
    missed_at = db.Column(db.DateTime, default=datetime.now)
    date = db.Column(db.Date, nullable=False)
    
    routine = db.relationship(Routine, backref='missed_reminders')
    user = db.relationship(User, backref='missed_reminders')

class MedicalHistory(db.Model):
    __tablename__ = 'medical_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey(User.id))
    
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.Text, nullable=True)
    file_path = db.Column(db.String, nullable=True)
    reflection = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    user = db.relationship(User, backref='medical_records')

class WeeklyReflection(db.Model):
    __tablename__ = 'weekly_reflections'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey(User.id))
    
    week_start = db.Column(db.Date, nullable=False)
    user_reflection = db.Column(db.Text, nullable=True)
    ai_insight = db.Column(db.Text, nullable=True)
    co_care_score = db.Column(db.Integer, default=50)
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    user = db.relationship(User, backref='reflections')

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey(User.id))
    
    role = db.Column(db.String, nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String, nullable=True)
    is_emergency = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    user = db.relationship(User, backref='chat_history')
