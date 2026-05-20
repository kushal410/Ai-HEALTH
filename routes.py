from flask import session, render_template, request, jsonify, redirect, url_for, make_response
from flask_login import current_user
from app import app, db
from replit_auth import require_login, make_replit_blueprint
from models import User, NurseProfile, UserMood, Routine, RoutineCompletion, MissedReminder, MedicalHistory, WeeklyReflection, ChatMessage
from ai_helpers import get_nurse_greeting, get_nurse_response, get_medical_info, generate_weekly_insight, get_quote_of_day
from emotions import determine_emotion, get_emotion_info, get_all_emotions
from datetime import datetime, date, timedelta
from sqlalchemy import func
from werkzeug.utils import secure_filename
import os
import json

app.register_blueprint(make_replit_blueprint(), url_prefix="/auth")

def is_routine_within_duration(routine):
    """
    Check if a routine is still active based on its duration and created_at date.
    Returns True if the routine is still valid (within duration or ongoing), False otherwise.
    Supported formats: "7 days", "2 weeks", "1 month", "6 months", "1 year", "ongoing"
    """
    if not routine.duration or routine.duration.lower().strip() == 'ongoing':
        return True
    
    if not routine.created_at:
        return True
    
    try:
        duration_str = routine.duration.lower().strip()
        current_date = datetime.now().date()
        created_date = routine.created_at.date() if isinstance(routine.created_at, datetime) else routine.created_at
        
        # Extract the number from the duration string
        parts = duration_str.split()
        if len(parts) < 2:
            print(f"Invalid duration format for routine {routine.id}: {routine.duration}")
            return True
        
        try:
            count = int(parts[0])
        except ValueError:
            print(f"Cannot parse duration count for routine {routine.id}: {routine.duration}")
            return True
        
        unit = parts[1]
        
        # Calculate end date based on unit
        if 'day' in unit:
            end_date = created_date + timedelta(days=count)
        elif 'week' in unit:
            end_date = created_date + timedelta(weeks=count)
        elif 'month' in unit:
            # Approximate months as 30 days
            end_date = created_date + timedelta(days=count * 30)
        elif 'year' in unit:
            # Approximate years as 365 days
            end_date = created_date + timedelta(days=count * 365)
        else:
            print(f"Unknown duration unit for routine {routine.id}: {unit}")
            return True
        
        is_active = current_date <= end_date
        if not is_active:
            print(f"Routine {routine.id} has expired: created {created_date}, duration {routine.duration}, end date {end_date}")
        return is_active
        
    except Exception as e:
        print(f"Error checking routine duration for routine {routine.id}: {e}")
        return True

@app.before_request
def make_session_permanent():
    session.permanent = True

@app.route('/')
def index():
    if current_user.is_authenticated:
        if not current_user.onboarding_completed:
            return redirect(url_for('onboarding'))
        return redirect(url_for('dashboard'))
    return render_template('landing.html')

@app.route('/onboarding')
@require_login
def onboarding():
    if current_user.onboarding_completed:
        return redirect(url_for('dashboard'))
    return render_template('onboarding.html', user=current_user)

@app.route('/api/complete-onboarding', methods=['POST'])
@require_login
def complete_onboarding():
    data = request.json
    
    errors = []
    
    name = data.get('name', '').strip()
    if not name:
        errors.append('Name is required')
    elif len(name) < 2:
        errors.append('Name must be at least 2 characters')
    
    gender = data.get('gender', '').strip()
    if not gender:
        errors.append('Gender is required')
    
    dob_str = data.get('dob', '').strip()
    if not dob_str:
        errors.append('Date of birth is required')
    else:
        try:
            dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
            if dob > date.today():
                errors.append('Date of birth cannot be in the future')
        except ValueError:
            errors.append('Invalid date of birth format')
    
    contact = data.get('contact', '').strip()
    if not contact:
        errors.append('Contact number is required')
    elif len(contact) < 10:
        errors.append('Contact number must be at least 10 digits')
    
    address = data.get('address', '').strip()
    if not address:
        errors.append('Address is required')
    elif len(address) < 5:
        errors.append('Address must be at least 5 characters')
    
    emergency_contact = data.get('emergency_contact', '').strip()
    if not emergency_contact:
        errors.append('Emergency contact is required')
    elif len(emergency_contact) < 10:
        errors.append('Emergency contact must be at least 10 digits')
    
    nurse_name = data.get('nurse_name', '').strip()
    if not nurse_name:
        errors.append('Nurse name is required')
    elif len(nurse_name) < 2:
        errors.append('Nurse name must be at least 2 characters')
    
    if errors:
        return jsonify({'error': '; '.join(errors)}), 400
    
    current_user.name = name
    current_user.gender = gender
    current_user.age = data.get('age')
    current_user.dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
    current_user.contact = contact
    current_user.address = address
    current_user.emergency_contact = emergency_contact
    current_user.onboarding_completed = True
    
    nurse = NurseProfile.query.filter_by(user_id=current_user.id).first()
    if not nurse:
        nurse = NurseProfile(user_id=current_user.id)
    
    nurse.nurse_name = nurse_name
    nurse.nurse_avatar = data.get('nurse_avatar', 'heart')
    nurse.care_style = data.get('care_style', 'balanced')
    nurse.tone_preference = data.get('tone_preference', 'warm')
    
    db.session.add(nurse)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/dashboard')
@require_login
def dashboard():
    nurse = NurseProfile.query.filter_by(user_id=current_user.id).first()
    if not nurse:
        return redirect(url_for('onboarding'))
    
    today = date.today()
    routines = Routine.query.filter_by(user_id=current_user.id, is_active=True).all()
    
    completed_today = db.session.query(RoutineCompletion).filter(
        RoutineCompletion.user_id == current_user.id,
        RoutineCompletion.date == today
    ).count()
    
    total_routines = len(routines)
    completion_rate = (completed_today / total_routines * 100) if total_routines > 0 else 0
    
    last_7_days = [(today - timedelta(days=i)) for i in range(7)]
    completed_count = db.session.query(RoutineCompletion.date, func.count(RoutineCompletion.id)).filter(
        RoutineCompletion.user_id == current_user.id,
        RoutineCompletion.date.in_(last_7_days)
    ).group_by(RoutineCompletion.date).all()
    
    completed_dates = [d[0] for d in completed_count]
    
    # Calculate streak: count consecutive days with completions
    streak = 0
    start_from = 0
    
    # If today has no completions yet, start counting from yesterday
    # This way the streak persists throughout the day until you complete something
    if today not in completed_dates:
        start_from = 1
    
    # Count consecutive days backwards
    for i in range(start_from, 7):
        check_date = today - timedelta(days=i)
        if check_date in completed_dates:
            streak += 1
        else:
            break
    
    missed_count = 7 - len(completed_dates)
    
    recent_mood = UserMood.query.filter_by(user_id=current_user.id).order_by(UserMood.created_at.desc()).first()
    
    user_stats = {
        'completed_today': completed_today,
        'total_routines': total_routines,
        'streak': streak,
        'missed_count': missed_count,
        'recent_mood': recent_mood.mood if recent_mood else 'neutral',
        'engagement_level': nurse.energy_level
    }
    
    emotion_name = determine_emotion(user_stats)
    nurse.current_emotion = emotion_name
    db.session.commit()
    
    emotion_info = get_emotion_info(emotion_name)
    
    co_care_score = int(nurse.energy_level * 0.8 + completion_rate * 0.2)
    
    # Prepare 7-day analytics data with completed, coming, and missed trends
    # Query missed reminders for the last 7 days
    missed_count_by_day = db.session.query(MissedReminder.date, func.count(MissedReminder.id)).filter(
        MissedReminder.user_id == current_user.id,
        MissedReminder.date.in_(last_7_days)
    ).group_by(MissedReminder.date).all()
    
    analytics_data = []
    for i in range(6, -1, -1):  # Last 7 days, oldest to newest
        day = today - timedelta(days=i)
        completed = next((count for date, count in completed_count if date == day), 0)
        missed = next((count for date, count in missed_count_by_day if date == day), 0)
        
        analytics_data.append({
            'date': day.strftime('%a'),  # Day name (Mon, Tue, etc)
            'completed': completed,
            'missed': missed,
            'coming': 0,  # Will be set for today only
            'is_today': (day == today)
        })
    
    # Calculate nurse mode (1-10 scale based on energy level)
    nurse_mode_scale = max(1, min(10, round(nurse.energy_level / 10)))
    
    # Calculate coming and missed reminders for today
    current_time = datetime.now().time()
    completed_routine_ids = [c.routine_id for c in db.session.query(RoutineCompletion.routine_id).filter(
        RoutineCompletion.user_id == current_user.id,
        RoutineCompletion.date == today
    ).all()]
    
    coming_reminders = 0
    missed_reminders_today = 0
    
    for routine in routines:
        # Skip if already completed
        if routine.id in completed_routine_ids:
            continue
        # Skip if no time set or time is empty
        if not routine.time or routine.time.strip() == '':
            continue
        # Skip if reminders explicitly disabled
        if routine.reminder_enabled is False:
            continue
        # Check if routine is still within its duration period
        if not is_routine_within_duration(routine):
            continue
        
        try:
            routine_time = datetime.strptime(routine.time, '%H:%M').time()
            # Coming: time is in the future
            if routine_time > current_time:
                coming_reminders += 1
            # Missed: time is now or in the past and not completed
            else:
                missed_reminders_today += 1
                # Log missed reminder if not already logged today
                existing_log = MissedReminder.query.filter_by(
                    routine_id=routine.id,
                    user_id=current_user.id,
                    date=today
                ).first()
                if not existing_log:
                    missed_log = MissedReminder(
                        routine_id=routine.id,
                        user_id=current_user.id,
                        scheduled_time=routine.time,
                        date=today
                    )
                    db.session.add(missed_log)
        except Exception as e:
            print(f"Error parsing time for routine {routine.id} in dashboard: {routine.time}, Error: {e}")
            pass
    
    # Commit any missed reminder logs
    try:
        db.session.commit()
    except:
        db.session.rollback()
    
    # Update analytics_data with coming reminders for today
    for day_data in analytics_data:
        if day_data['is_today']:
            day_data['coming'] = coming_reminders
            break
    
    return render_template('dashboard.html', 
                         user=current_user,
                         nurse=nurse,
                         co_care_score=co_care_score,
                         completed_today=completed_today,
                         total_routines=total_routines,
                         streak=streak,
                         coming_reminders=coming_reminders,
                         missed_reminders_today=missed_reminders_today,
                         recent_mood=recent_mood,
                         emotion_info=emotion_info,
                         tour_completed=current_user.tour_completed,
                         analytics_data=analytics_data,
                         nurse_mode_scale=nurse_mode_scale)

@app.route('/api/dashboard-stats', methods=['GET'])
@require_login
def get_dashboard_stats():
    """API endpoint to fetch real-time dashboard statistics"""
    nurse = NurseProfile.query.filter_by(user_id=current_user.id).first()
    routines = Routine.query.filter_by(user_id=current_user.id, is_active=True).all()
    today = date.today()
    
    # Count completed today
    completed_today = db.session.query(func.count(RoutineCompletion.id)).filter(
        RoutineCompletion.user_id == current_user.id,
        RoutineCompletion.date == today
    ).scalar() or 0
    
    # Calculate coming and missed reminders
    current_time = datetime.now().time()
    completed_routine_ids = [c.routine_id for c in db.session.query(RoutineCompletion.routine_id).filter(
        RoutineCompletion.user_id == current_user.id,
        RoutineCompletion.date == today
    ).all()]
    
    coming_reminders = 0
    missed_reminders_today = 0
    
    for routine in routines:
        # Skip if already completed
        if routine.id in completed_routine_ids:
            continue
        # Skip if no time set or time is empty
        if not routine.time or routine.time.strip() == '':
            continue
        # Skip if reminders explicitly disabled
        if routine.reminder_enabled is False:
            continue
        # Check if routine is still within its duration period
        if not is_routine_within_duration(routine):
            continue
        
        try:
            routine_time = datetime.strptime(routine.time, '%H:%M').time()
            if routine_time > current_time:
                coming_reminders += 1
            else:
                missed_reminders_today += 1
                # Log missed reminder if not already logged today
                existing_log = MissedReminder.query.filter_by(
                    routine_id=routine.id,
                    user_id=current_user.id,
                    date=today
                ).first()
                if not existing_log:
                    missed_log = MissedReminder(
                        routine_id=routine.id,
                        user_id=current_user.id,
                        scheduled_time=routine.time,
                        date=today
                    )
                    db.session.add(missed_log)
        except Exception as e:
            print(f"Error parsing time for routine {routine.id} in dashboard stats: {routine.time}, Error: {e}")
            pass
    
    # Commit any missed reminder logs
    try:
        db.session.commit()
    except:
        db.session.rollback()
    
    # Calculate streak
    last_7_days = [(today - timedelta(days=i)) for i in range(7)]
    completed_count = db.session.query(RoutineCompletion.date, func.count(RoutineCompletion.id)).filter(
        RoutineCompletion.user_id == current_user.id,
        RoutineCompletion.date.in_(last_7_days)
    ).group_by(RoutineCompletion.date).all()
    
    completed_dates = [d[0] for d in completed_count]
    
    # Calculate streak: count consecutive days with completions
    streak = 0
    start_from = 0
    
    # If today has no completions yet, start counting from yesterday
    # This way the streak persists throughout the day until you complete something
    if today not in completed_dates:
        start_from = 1
    
    # Count consecutive days backwards
    for i in range(start_from, 7):
        check_date = today - timedelta(days=i)
        if check_date in completed_dates:
            streak += 1
        else:
            break
    
    total_routines = len(routines)
    completion_rate = (completed_today / total_routines * 100) if total_routines > 0 else 0
    co_care_score = int(nurse.energy_level * 0.8 + completion_rate * 0.2) if nurse else 0
    
    return jsonify({
        'success': True,
        'stats': {
            'completed_today': completed_today,
            'total_routines': total_routines,
            'streak': streak,
            'coming_reminders': coming_reminders,
            'missed_reminders_today': missed_reminders_today,
            'co_care_score': co_care_score,
            'nurse_energy': nurse.energy_level if nurse else 0,
            'nurse_emotion': nurse.current_emotion if nurse else 'neutral'
        }
    })

@app.route('/api/update-mood', methods=['POST'])
@require_login
def update_mood():
    data = request.json
    mood = UserMood(
        user_id=current_user.id,
        mood=data.get('mood'),
        mood_emoji=data.get('emoji'),
        note=data.get('note', '')
    )
    db.session.add(mood)
    
    nurse = NurseProfile.query.filter_by(user_id=current_user.id).first()
    if nurse:
        mood_map = {
            'amazing': ('happy', 90, 'fast'),
            'good': ('happy', 80, 'normal'),
            'okay': ('neutral', 70, 'normal'),
            'bad': ('concerned', 60, 'slow'),
            'terrible': ('sad', 50, 'slow')
        }
        nurse_mood, energy, heartbeat = mood_map.get(data.get('mood'), ('neutral', 70, 'normal'))
        nurse.current_mood = nurse_mood
        nurse.energy_level = energy
        nurse.heartbeat_speed = heartbeat
    
    db.session.commit()
    
    return jsonify({'success': True, 'nurse_mood': nurse.current_mood})

@app.route('/api/select-emotion', methods=['POST'])
@require_login
def select_emotion():
    data = request.json
    emotion = data.get('emotion')
    
    # Save user emotion to mood tracking
    mood = UserMood(
        user_id=current_user.id,
        mood=emotion,
        mood_emoji='',
        note=f'User feeling: {emotion}'
    )
    db.session.add(mood)
    
    nurse = NurseProfile.query.filter_by(user_id=current_user.id).first()
    
    # Human-like nurse emotional responses to user emotions
    emotion_responses = {
        'happy': {
            'nurse_emotion': 'Happy',
            'nurse_mood': 'joyful',
            'energy': 85,
            'heartbeat': 'normal',
            'message': f"I'm so happy to see you feeling good! Your joy makes my day brighter! 😊"
        },
        'sad': {
            'nurse_emotion': 'Worried',
            'nurse_mood': 'concerned',
            'energy': 55,
            'heartbeat': 'normal',
            'message': f"I'm here for you. It's okay to feel sad sometimes. Let's work through this together. 💙"
        },
        'anxious': {
            'nurse_emotion': 'Worried',
            'nurse_mood': 'concerned',
            'energy': 65,
            'heartbeat': 'stressing',
            'message': f"I can feel your anxiety. Let's take a deep breath together. I'm right here with you. 🤗"
        },
        'calm': {
            'nurse_emotion': 'Calm',
            'nurse_mood': 'peaceful',
            'energy': 70,
            'heartbeat': 'normal',
            'message': f"Your calm energy is beautiful! I'm feeling peaceful too. Let's keep this serenity. 🧘"
        },
        'energetic': {
            'nurse_emotion': 'Energetic',
            'nurse_mood': 'excited',
            'energy': 95,
            'heartbeat': 'normal',
            'message': f"Wow! Your energy is contagious! I'm feeling pumped up too! Let's make today amazing! ⚡"
        },
        'tired': {
            'nurse_emotion': 'Sleepy',
            'nurse_mood': 'tired',
            'energy': 40,
            'heartbeat': 'normal',
            'message': f"I can tell you're tired. Rest is important, dear. Let me help you recharge. 😴"
        },
        'frustrated': {
            'nurse_emotion': 'Frustrated',
            'nurse_mood': 'frustrated',
            'energy': 60,
            'heartbeat': 'stressing',
            'message': f"I understand your frustration. It's okay to feel this way. I'm here to support you. 💪"
        },
        'excited': {
            'nurse_emotion': 'Excited',
            'nurse_mood': 'thrilled',
            'energy': 90,
            'heartbeat': 'normal',
            'message': f"Your excitement is infectious! I'm thrilled for you! Let's celebrate this moment! 🎉"
        },
        'worried': {
            'nurse_emotion': 'Worried',
            'nurse_mood': 'concerned',
            'energy': 50,
            'heartbeat': 'stressing',
            'message': f"I feel your worry. Remember, I'm here to help you navigate through this. You're not alone. 🌸"
        },
        'content': {
            'nurse_emotion': 'Happy',
            'nurse_mood': 'satisfied',
            'energy': 75,
            'heartbeat': 'normal',
            'message': f"Your contentment warms my heart! I'm happy you're feeling at peace. 😌"
        }
    }
    
    response_data = emotion_responses.get(emotion, {
        'nurse_emotion': 'Happy',
        'nurse_mood': 'neutral',
        'energy': 70,
        'heartbeat': 'normal',
        'message': f"Thank you for sharing how you feel! I'm here for you always. 💜"
    })
    
    if nurse:
        nurse.current_emotion = response_data['nurse_emotion']
        nurse.current_mood = response_data['nurse_mood']
        nurse.energy_level = response_data['energy']
        nurse.heartbeat_speed = response_data['heartbeat']
    
    db.session.commit()
    
    # Get AI-powered improvement tips
    from ai_helpers import get_emotion_improvement_tips
    nurse_name = nurse.nurse_name if nurse else 'NurseAI'
    improvement_tips = get_emotion_improvement_tips(emotion, nurse_name)
    
    return jsonify({
        'success': True,
        'message': response_data['message'],
        'nurse_emotion': response_data['nurse_emotion'],
        'improvement_tips': improvement_tips
    })

@app.route('/api/complete-tour', methods=['POST'])
@require_login
def complete_tour():
    current_user.tour_completed = True
    db.session.commit()
    return jsonify({'success': True})

@app.route('/planner')
@require_login
def planner():
    nurse = NurseProfile.query.filter_by(user_id=current_user.id).first()
    routines = Routine.query.filter_by(user_id=current_user.id, is_active=True).all()
    
    today = date.today()
    completed_ids = [c.routine_id for c in RoutineCompletion.query.filter(
        RoutineCompletion.user_id == current_user.id,
        RoutineCompletion.date == today
    ).all()]
    
    # Calculate stats for planner page
    total_completed_count = db.session.query(func.count(RoutineCompletion.id)).filter(
        RoutineCompletion.user_id == current_user.id
    ).scalar() or 0
    
    current_time = datetime.now().time()
    missed_today_count = 0
    coming_reminders_count = 0
    
    for routine in routines:
        # Only count routines that are not completed, have time set, and have reminders enabled
        if routine.id in completed_ids:
            continue
        if not routine.time or routine.time.strip() == '':
            continue
        if routine.reminder_enabled is False:  # Explicitly check for False
            continue
        # Check if routine is still within its duration period
        if not is_routine_within_duration(routine):
            continue
        
        try:
            routine_time = datetime.strptime(routine.time, '%H:%M').time()
            if routine_time <= current_time:
                missed_today_count += 1
            else:
                coming_reminders_count += 1
        except Exception as e:
            print(f"Error parsing time for routine {routine.id}: {routine.time}, Error: {e}")
            pass
    
    # Sort routines: coming reminders first (by time), then past reminders
    def sort_key(routine):
        if not routine.time or not routine.reminder_enabled:
            return (2, '')  # No time set or disabled - put at end
        try:
            routine_time = datetime.strptime(routine.time, '%H:%M').time()
            if routine.id in completed_ids:
                return (3, routine.time)  # Completed - put at end
            elif routine_time > current_time:
                return (0, routine.time)  # Coming - put at start, sorted by time
            else:
                return (1, routine.time)  # Missed - put in middle
        except:
            return (2, '')
    
    routines_sorted = sorted(routines, key=sort_key)
    
    # Convert routines to dictionaries for JSON serialization
    routines_data = []
    for routine in routines_sorted:
        routines_data.append({
            'id': routine.id,
            'title': routine.title,
            'description': routine.description,
            'category': routine.category,
            'time': routine.time,
            'duration': routine.duration,
            'reminder_enabled': routine.reminder_enabled,
            'frequency': routine.frequency
        })
    
    # Generate daily motivational health quote
    from ai_helpers import get_daily_health_quote
    nurse_name = nurse.nurse_name if nurse else 'NurseAI'
    health_quote = get_daily_health_quote(nurse_name, len(routines), len(completed_ids))
    
    return render_template('planner.html', 
                         user=current_user, 
                         nurse=nurse, 
                         routines=routines_sorted,
                         routines_data=routines_data,
                         completed_ids=completed_ids,
                         total_completed_count=total_completed_count,
                         missed_today_count=missed_today_count,
                         coming_reminders_count=coming_reminders_count,
                         health_quote=health_quote)

@app.route('/api/add-routine', methods=['POST'])
@require_login
def add_routine():
    data = request.json
    current_datetime = datetime.now()
    routine = Routine(
        user_id=current_user.id,
        title=data.get('title'),
        description=data.get('description', ''),
        category=data.get('category'),
        time=data.get('time'),
        frequency=data.get('frequency', 'daily'),
        duration=data.get('duration', 'ongoing'),
        reminder_enabled=data.get('reminder_enabled', True),
        created_at=current_datetime
    )
    db.session.add(routine)
    db.session.commit()
    
    return jsonify({'success': True, 'routine_id': routine.id})

@app.route('/api/complete-routine/<int:routine_id>', methods=['POST'])
@require_login
def complete_routine(routine_id):
    today = date.today()
    
    existing = RoutineCompletion.query.filter_by(
        routine_id=routine_id,
        user_id=current_user.id,
        date=today
    ).first()
    
    if not existing:
        current_datetime = datetime.now()
        completion = RoutineCompletion(
            routine_id=routine_id,
            user_id=current_user.id,
            date=today,
            completed_at=current_datetime
        )
        db.session.add(completion)
        
        nurse = NurseProfile.query.filter_by(user_id=current_user.id).first()
        if nurse and nurse.energy_level < 95:
            nurse.energy_level = min(95, nurse.energy_level + 2)
            if nurse.energy_level > 80:
                nurse.current_mood = 'happy'
                nurse.heartbeat_speed = 'normal'
        
        db.session.commit()
        
        return jsonify({'success': True, 'celebrate': True})
    
    return jsonify({'success': True, 'celebrate': False})

@app.route('/api/update-routine/<int:routine_id>', methods=['POST'])
@require_login
def update_routine(routine_id):
    routine = Routine.query.filter_by(id=routine_id, user_id=current_user.id).first()
    if not routine:
        return jsonify({'error': 'Routine not found'}), 404
    
    data = request.json
    routine.title = data.get('title', routine.title)
    routine.description = data.get('description', routine.description)
    routine.category = data.get('category', routine.category)
    routine.time = data.get('time', routine.time)
    routine.duration = data.get('duration', routine.duration)
    routine.reminder_enabled = data.get('reminder_enabled', routine.reminder_enabled)
    
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/delete-routine/<int:routine_id>', methods=['DELETE'])
@require_login
def delete_routine(routine_id):
    routine = Routine.query.filter_by(id=routine_id, user_id=current_user.id).first()
    if not routine:
        return jsonify({'error': 'Routine not found'}), 404
    
    routine.is_active = False
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/check-reminders', methods=['GET'])
@require_login
def check_reminders():
    """Check for reminders that are due at the current time"""
    from datetime import datetime, time as datetime_time
    
    now = datetime.now()
    current_time = now.strftime('%H:%M')
    today = date.today()
    
    # Get all active routines with reminders enabled
    routines = Routine.query.filter_by(
        user_id=current_user.id,
        is_active=True,
        reminder_enabled=True
    ).all()
    
    # Check which routines haven't been completed today and are due now
    due_reminders = []
    for routine in routines:
        if routine.time:
            # Check if routine time matches current time exactly or just passed
            routine_hour, routine_minute = map(int, routine.time.split(':'))
            current_minutes = now.hour * 60 + now.minute
            routine_minutes = routine_hour * 60 + routine_minute
            
            # Show reminder at exact time or within 2 minutes after
            if routine_minutes <= current_minutes <= routine_minutes + 2:
                # Check if not completed today
                completed = RoutineCompletion.query.filter_by(
                    routine_id=routine.id,
                    user_id=current_user.id,
                    date=today
                ).first()
                
                if not completed:
                    due_reminders.append({
                        'id': routine.id,
                        'title': routine.title,
                        'description': routine.description,
                        'category': routine.category,
                        'time': routine.time
                    })
    
    return jsonify({
        'success': True,
        'reminders': due_reminders
    })

@app.route('/first-aid')
@require_login
def first_aid():
    nurse = NurseProfile.query.filter_by(user_id=current_user.id).first()
    messages = ChatMessage.query.filter_by(user_id=current_user.id).order_by(ChatMessage.created_at.desc()).limit(50).all()
    messages.reverse()
    
    return render_template('first_aid.html', user=current_user, nurse=nurse, messages=messages)

@app.route('/api/chat', methods=['POST'])
@require_login
def chat():
    data = request.json
    user_message = data.get('message', '')
    is_emergency = data.get('emergency', False)
    
    if not user_message or not user_message.strip():
        return jsonify({'error': 'Message is required'}), 400
    
    nurse = NurseProfile.query.filter_by(user_id=current_user.id).first()
    
    if is_emergency:
        nurse.heartbeat_speed = 'stressing'
    
    recent_messages = ChatMessage.query.filter_by(user_id=current_user.id).order_by(ChatMessage.created_at.desc()).limit(10).all()
    recent_messages.reverse()
    
    messages = [{'role': msg.role, 'content': msg.content} for msg in recent_messages]
    messages.append({'role': 'user', 'content': user_message})
    
    user_chat = ChatMessage(
        user_id=current_user.id,
        role='user',
        content=user_message,
        is_emergency=is_emergency
    )
    
    db.session.add(user_chat)
    
    if 'medical' in user_message.lower() or 'symptom' in user_message.lower():
        response_text = get_medical_info(user_message)
    else:
        response_text = get_nurse_response(messages, nurse, is_emergency)
    
    ai_chat = ChatMessage(
        user_id=current_user.id,
        role='assistant',
        content=response_text,
        is_emergency=is_emergency
    )
    db.session.add(ai_chat)
    db.session.commit()
    
    return jsonify({'response': response_text})

@app.route('/medical-history')
@require_login
def medical_history():
    nurse = NurseProfile.query.filter_by(user_id=current_user.id).first()
    records = MedicalHistory.query.filter_by(user_id=current_user.id).order_by(MedicalHistory.created_at.desc()).all()
    
    return render_template('medical_history.html', user=current_user, nurse=nurse, records=records)

@app.route('/api/add-medical-record', methods=['POST'])
@require_login
def add_medical_record():
    title = request.form.get('title')
    description = request.form.get('description', '')
    reflection = request.form.get('reflection', '')
    
    file_path = None
    if 'file' in request.files:
        file = request.files['file']
        if file.filename:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{current_user.id}_{datetime.now().timestamp()}_{filename}")
            file.save(file_path)
    
    record = MedicalHistory(
        user_id=current_user.id,
        title=title,
        description=description,
        file_path=file_path,
        reflection=reflection
    )
    db.session.add(record)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/download-medical-history')
@require_login
def download_medical_history():
    records = MedicalHistory.query.filter_by(user_id=current_user.id).order_by(MedicalHistory.created_at.desc()).all()
    
    data = {
        'user': {
            'name': current_user.name,
            'email': current_user.email,
            'export_date': datetime.now().isoformat()
        },
        'medical_history': []
    }
    
    for record in records:
        data['medical_history'].append({
            'title': record.title,
            'description': record.description,
            'reflection': record.reflection,
            'created_at': record.created_at.isoformat() if record.created_at else None,
            'has_file': record.file_path is not None
        })
    
    response = make_response(json.dumps(data, indent=2))
    response.headers['Content-Type'] = 'application/json'
    response.headers['Content-Disposition'] = f'attachment; filename=medical_history_{current_user.id}_{datetime.now().strftime("%Y%m%d")}.json'
    
    return response

@app.route('/api/view-medical-record/<int:record_id>')
@require_login
def view_medical_record(record_id):
    record = MedicalHistory.query.filter_by(id=record_id, user_id=current_user.id).first()
    if not record:
        return jsonify({'error': 'Record not found'}), 404
    
    return jsonify({
        'title': record.title,
        'description': record.description,
        'reflection': record.reflection,
        'created_at': record.created_at.isoformat() if record.created_at else None,
        'has_file': record.file_path is not None,
        'file_path': record.file_path
    })

@app.route('/reflection')
@require_login
def reflection():
    nurse = NurseProfile.query.filter_by(user_id=current_user.id).first()
    reflections = WeeklyReflection.query.filter_by(user_id=current_user.id).order_by(WeeklyReflection.created_at.desc()).all()
    
    return render_template('reflection.html', user=current_user, nurse=nurse, reflections=reflections)

@app.route('/api/generate-insight', methods=['POST'])
@require_login
def generate_insight():
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    
    routines_completed = db.session.query(RoutineCompletion).filter(
        RoutineCompletion.user_id == current_user.id,
        RoutineCompletion.date >= week_start
    ).count()
    
    moods = UserMood.query.filter(
        UserMood.user_id == current_user.id,
        UserMood.created_at >= week_start
    ).all()
    
    nurse = NurseProfile.query.filter_by(user_id=current_user.id).first()
    
    user_data = {
        'routines_completed': routines_completed,
        'moods': [m.mood for m in moods],
        'co_care_score': nurse.energy_level
    }
    
    insight = generate_weekly_insight(user_data, nurse)
    
    return jsonify({'insight': insight})

@app.route('/api/save-reflection', methods=['POST'])
@require_login
def save_reflection():
    data = request.json
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    
    reflection = WeeklyReflection.query.filter_by(
        user_id=current_user.id,
        week_start=week_start
    ).first()
    
    if not reflection:
        reflection = WeeklyReflection(
            user_id=current_user.id,
            week_start=week_start
        )
    
    reflection.user_reflection = data.get('user_reflection')
    reflection.ai_insight = data.get('ai_insight')
    reflection.co_care_score = data.get('co_care_score', 50)
    
    db.session.add(reflection)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/update-nurse-preferences', methods=['POST'])
@require_login
def update_nurse_preferences():
    data = request.json
    nurse = NurseProfile.query.filter_by(user_id=current_user.id).first()
    
    if nurse:
        if 'emoji_level' in data:
            nurse.emoji_level = data['emoji_level']
        if 'strictness_level' in data:
            nurse.strictness_level = data['strictness_level']
        if 'tone_preference' in data:
            nurse.tone_preference = data['tone_preference']
        
        db.session.commit()
        return jsonify({'success': True})
    
    return jsonify({'success': False})

@app.route('/settings')
@require_login
def settings():
    nurse = NurseProfile.query.filter_by(user_id=current_user.id).first()
    return render_template('settings.html', user=current_user, nurse=nurse)

@app.route('/api/update-profile', methods=['POST'])
@require_login
def update_profile():
    data = request.json
    
    if 'name' in data:
        current_user.name = data['name']
    if 'contact' in data:
        current_user.contact = data['contact']
    if 'address' in data:
        current_user.address = data['address']
    if 'emergency_contact' in data:
        current_user.emergency_contact = data['emergency_contact']
    if 'language' in data:
        current_user.language = data['language']
    
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/nurse-greeting', methods=['GET'])
@require_login
def nurse_greeting():
    nurse = NurseProfile.query.filter_by(user_id=current_user.id).first()
    recent_mood = UserMood.query.filter_by(user_id=current_user.id).order_by(UserMood.created_at.desc()).first()
    
    greeting = get_nurse_greeting(
        current_user.name or current_user.first_name or "friend",
        nurse.nurse_name,
        nurse.tone_preference,
        recent_mood.mood if recent_mood else None
    )
    
    return jsonify({'greeting': greeting})
