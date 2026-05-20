#!/usr/bin/env python3
"""
NurseAI Database Schema Setup Script

This script creates the complete database schema for NurseAI outside of the Replit environment.
It can be used to set up the database on any PostgreSQL server.

Usage:
    python database_schema.py

Requirements:
    - PostgreSQL database server
    - psycopg2-binary package
    - SQLAlchemy package

Environment Variables Required:
    DATABASE_URL=postgresql://user:password@host:port/database
    OR individual variables:
    PGHOST=your_host
    PGPORT=5432
    PGUSER=your_user
    PGPASSWORD=your_password
    PGDATABASE=your_database
"""

import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Create Base class for declarative models
Base = declarative_base()


class User(Base):
    """User account and profile information"""
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    profile_image_url = Column(String, nullable=True)
    
    # Extended profile fields
    name = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    dob = Column(Date, nullable=True)
    contact = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    emergency_contact = Column(String, nullable=True)
    
    # App settings
    onboarding_completed = Column(Boolean, default=False)
    tour_completed = Column(Boolean, default=False)
    language = Column(String, default='en')
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    nurse_profile = relationship("NurseProfile", back_populates="user", uselist=False)
    moods = relationship("UserMood", back_populates="user")
    routines = relationship("Routine", back_populates="user")
    medical_records = relationship("MedicalHistory", back_populates="user")
    reflections = relationship("WeeklyReflection", back_populates="user")
    chat_history = relationship("ChatMessage", back_populates="user")


class OAuth(Base):
    """
    OAuth authentication tokens (for Replit Auth/Flask-Dance integration)
    Mimics Flask-Dance's OAuthConsumerMixin schema
    """
    __tablename__ = 'oauth'
    
    id = Column(Integer, primary_key=True)
    
    # OAuthConsumerMixin columns
    provider = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    token = Column(Text, nullable=False)  # Stores JSON OAuth token
    
    # Custom columns for multi-user support
    user_id = Column(String, ForeignKey('users.id'))
    browser_session_key = Column(String, nullable=False)
    
    # Unique constraint to prevent duplicate OAuth entries
    __table_args__ = (UniqueConstraint(
        'user_id',
        'browser_session_key',
        'provider',
        name='uq_user_browser_session_key_provider',
    ),)


class NurseProfile(Base):
    """AI Nurse personality and state"""
    __tablename__ = 'nurse_profiles'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), unique=True)
    
    # Nurse identity
    nurse_name = Column(String, nullable=False, default="NurseAI")
    nurse_avatar = Column(String, nullable=False, default="default")
    
    # Care preferences
    care_style = Column(String, nullable=False, default="balanced")
    tone_preference = Column(String, nullable=False, default="warm")
    emoji_level = Column(String, default="moderate")
    strictness_level = Column(String, default="balanced")
    
    # Current state
    current_mood = Column(String, default="happy")
    current_emotion = Column(String, default="calm")
    energy_level = Column(Integer, default=80)
    heartbeat_speed = Column(String, default="normal")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    user = relationship("User", back_populates="nurse_profile")


class UserMood(Base):
    """User mood tracking"""
    __tablename__ = 'user_moods'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'))
    
    mood = Column(String, nullable=False)
    mood_emoji = Column(String, nullable=False)
    note = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    user = relationship("User", back_populates="moods")


class Routine(Base):
    """Daily health routines"""
    __tablename__ = 'routines'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'))
    
    # Routine details
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=False)  # exercise, meditation, nutrition, etc.
    time = Column(String, nullable=True)  # HH:MM format
    frequency = Column(String, default="daily")
    duration = Column(String, nullable=True)  # e.g., "7 days", "2 weeks", "ongoing"
    
    # Settings
    reminder_enabled = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    user = relationship("User", back_populates="routines")
    completions = relationship("RoutineCompletion", back_populates="routine")


class RoutineCompletion(Base):
    """Routine completion history"""
    __tablename__ = 'routine_completions'
    
    id = Column(Integer, primary_key=True)
    routine_id = Column(Integer, ForeignKey('routines.id'))
    user_id = Column(String, ForeignKey('users.id'))
    
    completed_at = Column(DateTime, default=datetime.now)
    date = Column(Date, nullable=False)
    
    # Relationships
    routine = relationship("Routine", back_populates="completions")


class MedicalHistory(Base):
    """Medical records and health history"""
    __tablename__ = 'medical_history'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'))
    
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    file_path = Column(String, nullable=True)  # Path to uploaded documents
    reflection = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    user = relationship("User", back_populates="medical_records")


class WeeklyReflection(Base):
    """Weekly journal and reflections"""
    __tablename__ = 'weekly_reflections'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'))
    
    week_start = Column(Date, nullable=False)
    user_reflection = Column(Text, nullable=True)
    ai_insight = Column(Text, nullable=True)
    co_care_score = Column(Integer, default=50)
    
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    user = relationship("User", back_populates="reflections")


class ChatMessage(Base):
    """AI chat conversation history"""
    __tablename__ = 'chat_messages'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'))
    
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    image_path = Column(String, nullable=True)
    is_emergency = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    user = relationship("User", back_populates="chat_history")


def get_database_url():
    """Get database URL from environment variables"""
    # Try DATABASE_URL first (full connection string)
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        return database_url
    
    # Try individual components
    host = os.environ.get('PGHOST', 'localhost')
    port = os.environ.get('PGPORT', '5432')
    user = os.environ.get('PGUSER', 'postgres')
    password = os.environ.get('PGPASSWORD', '')
    database = os.environ.get('PGDATABASE', 'nurseai')
    
    return f'postgresql://{user}:{password}@{host}:{port}/{database}'


def create_database():
    """Create all database tables"""
    try:
        # Get database URL
        database_url = get_database_url()
        print(f"Connecting to database...")
        print(f"Host: {database_url.split('@')[1].split('/')[0] if '@' in database_url else 'localhost'}")
        
        # Create engine
        engine = create_engine(database_url, echo=False)
        
        # Test connection
        with engine.connect() as conn:
            print("✓ Database connection successful")
        
        # Create all tables
        print("\nCreating database tables...")
        Base.metadata.create_all(engine)
        
        # Print created tables
        print("\n✓ Database schema created successfully!")
        print("\nCreated tables:")
        for table_name in Base.metadata.tables.keys():
            print(f"  - {table_name}")
        
        print("\n" + "="*60)
        print("Database setup complete!")
        print("="*60)
        print("\nYou can now run the NurseAI application.")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error creating database: {e}")
        print("\nPlease check:")
        print("  1. PostgreSQL server is running")
        print("  2. Database credentials are correct")
        print("  3. Required environment variables are set:")
        print("     - DATABASE_URL (or PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE)")
        return False


def drop_all_tables():
    """Drop all tables (use with caution!)"""
    response = input("\n⚠️  WARNING: This will DELETE ALL DATA. Type 'DELETE ALL DATA' to confirm: ")
    if response == "DELETE ALL DATA":
        try:
            database_url = get_database_url()
            engine = create_engine(database_url, echo=False)
            
            print("\nDropping all tables...")
            Base.metadata.drop_all(engine)
            print("✓ All tables dropped successfully")
            return True
        except Exception as e:
            print(f"✗ Error dropping tables: {e}")
            return False
    else:
        print("Operation cancelled.")
        return False


def show_schema_info():
    """Display schema information"""
    print("\n" + "="*60)
    print("NurseAI Database Schema Information")
    print("="*60)
    
    tables_info = {
        'users': 'User accounts and profiles',
        'oauth': 'OAuth authentication tokens',
        'nurse_profiles': 'AI Nurse personality and state',
        'user_moods': 'User mood tracking',
        'routines': 'Daily health routines',
        'routine_completions': 'Routine completion history',
        'medical_history': 'Medical records and health history',
        'weekly_reflections': 'Weekly journal and reflections',
        'chat_messages': 'AI chat conversation history'
    }
    
    print("\nTables:")
    for table, description in tables_info.items():
        print(f"  {table:25} - {description}")
    
    print("\n" + "="*60)


def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("NurseAI Database Schema Setup")
    print("="*60)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == '--info':
            show_schema_info()
            return
        
        elif command == '--drop':
            if drop_all_tables():
                print("\nRecreate tables? (y/n): ", end='')
                if input().lower() == 'y':
                    create_database()
            return
        
        elif command == '--help':
            print("\nUsage:")
            print("  python database_schema.py           Create database tables")
            print("  python database_schema.py --info    Show schema information")
            print("  python database_schema.py --drop    Drop all tables (requires confirmation)")
            print("  python database_schema.py --help    Show this help message")
            return
    
    # Default: create database
    create_database()


if __name__ == '__main__':
    main()
