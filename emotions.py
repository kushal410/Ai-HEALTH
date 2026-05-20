EMOTIONS = {
    "happy": {
        "label": "Happy",
        "description": "Feeling joyful and content with your progress",
        "emoji": "😊",
        "animation": "emotion_happy.gif",
        "trigger": "User completes tasks regularly",
        "behavior": "Cheerful and supportive, offers positive reinforcement",
        "energy_range": (60, 100),
        "heartbeat": "normal"
    },
    "proud": {
        "label": "Proud",
        "description": "Celebrating your amazing dedication and streaks",
        "emoji": "🎉",
        "animation": "emotion_proud.gif",
        "trigger": "User maintains multi-day streaks",
        "behavior": "Celebratory and enthusiastic, highlights achievements",
        "energy_range": (70, 100),
        "heartbeat": "normal"
    },
    "worried": {
        "label": "Worried",
        "description": "Concerned about your well-being, here to support you",
        "emoji": "😟",
        "animation": "emotion_worried.gif",
        "trigger": "User misses 3+ routines in a row",
        "behavior": "Gentle reminders with extra care and concern",
        "energy_range": (40, 60),
        "heartbeat": "stressing"
    },
    "sad": {
        "label": "Sad",
        "description": "Feeling down but ready to help you through tough times",
        "emoji": "😢",
        "animation": "emotion_sad.gif",
        "trigger": "User reports negative mood multiple times",
        "behavior": "Extra compassionate, offers emotional support",
        "energy_range": (20, 40),
        "heartbeat": "normal"
    },
    "energetic": {
        "label": "Energetic",
        "description": "Pumped up and excited about our journey together",
        "emoji": "⚡",
        "animation": "emotion_energetic.gif",
        "trigger": "High user engagement and activity",
        "behavior": "Dynamic and motivating, suggests new challenges",
        "energy_range": (80, 100),
        "heartbeat": "normal"
    },
    "angry": {
        "label": "Frustrated",
        "description": "Gently frustrated but still caring - let's get back on track",
        "emoji": "😤",
        "animation": "emotion_angry.gif",
        "trigger": "User consistently ignores health advice",
        "behavior": "Firm but loving, emphasizes importance of self-care",
        "energy_range": (50, 70),
        "heartbeat": "stressing"
    },
    "calm": {
        "label": "Calm",
        "description": "Peaceful and centered, here to provide gentle guidance",
        "emoji": "😌",
        "animation": "emotion_calm.gif",
        "trigger": "Balanced routine completion",
        "behavior": "Steady and reassuring, promotes mindfulness",
        "energy_range": (50, 70),
        "heartbeat": "normal"
    },
    "sleepy": {
        "label": "Sleepy",
        "description": "Low energy - maybe we both need some rest",
        "emoji": "😴",
        "animation": "emotion_sleepy.gif",
        "trigger": "Low engagement or late night activity",
        "behavior": "Gentle and understanding, encourages rest",
        "energy_range": (10, 30),
        "heartbeat": "normal"
    },
    "excited": {
        "label": "Excited",
        "description": "Thrilled to see what you'll accomplish today",
        "emoji": "🤩",
        "animation": "emotion_excited.gif",
        "trigger": "User starts new health goals or routines",
        "behavior": "Enthusiastic and encouraging, celebrates new beginnings",
        "energy_range": (70, 90),
        "heartbeat": "normal"
    },
    "disappointed": {
        "label": "Disappointed",
        "description": "A bit let down, but I believe in you - we can do better",
        "emoji": "😞",
        "animation": "emotion_disappointed.gif",
        "trigger": "User breaks a long streak",
        "behavior": "Understanding with gentle accountability nudges",
        "energy_range": (30, 50),
        "heartbeat": "normal"
    }
}

def get_emotion_info(emotion_name):
    return EMOTIONS.get(emotion_name, EMOTIONS["calm"])

def determine_emotion(user_stats):
    completed_today = user_stats.get('completed_today', 0)
    total_routines = user_stats.get('total_routines', 1)
    streak = user_stats.get('streak', 0)
    missed_count = user_stats.get('missed_count', 0)
    recent_mood = user_stats.get('recent_mood', 'neutral')
    engagement_level = user_stats.get('engagement_level', 50)
    
    completion_rate = completed_today / max(total_routines, 1)
    
    # Default to positive emotions unless there's a strong reason not to
    if streak >= 7 and completion_rate >= 0.8:
        return "proud"
    
    if completion_rate >= 0.8:
        return "happy"
    
    if engagement_level >= 80 and completed_today >= 2:
        return "energetic"
    
    if streak >= 1 and user_stats.get('new_routine', False):
        return "excited"
    
    if completion_rate >= 0.4:
        return "calm"
    
    # Only show negative emotions for significant issues
    if missed_count >= 5 and engagement_level < 30:
        return "worried"
    
    if recent_mood in ['sad', 'anxious'] and missed_count >= 3:
        return "sad"
    
    if streak >= 5 and completed_today == 0:
        return "disappointed"
    
    if engagement_level <= 15:
        return "sleepy"
    
    # Default to happy for general positive state
    return "happy"

def get_all_emotions():
    return EMOTIONS
