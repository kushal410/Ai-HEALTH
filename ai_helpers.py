import os
import json
import requests
import re

PERPLEXITY_API_KEY = os.environ.get("PERPLEXITY_API_KEY")

def remove_citations(text):
    """Remove citation markers like [1], [2], etc. from text for cleaner reading while preserving all formatting"""
    # Simply remove citation markers like [1], [2], [3], etc.
    # Don't touch any other whitespace to preserve formatting, indentation, and structure
    text = re.sub(r'\[\d+\]', '', text)
    return text

def get_nurse_greeting(user_name, nurse_name, nurse_tone, user_mood=None, streak_data=None):
    """Generate a personalized greeting from the nurse"""
    if not PERPLEXITY_API_KEY:
        print("ERROR: PERPLEXITY_API_KEY not found in environment")
        return f"Hello {user_name}! 💙 I'm {nurse_name}, your caring companion. How are you feeling today?"
    
    context = f"You are {nurse_name}, an emotionally intelligent AI nurse companion. "
    context += f"Speak in a {nurse_tone} tone. "
    
    if user_mood:
        context += f"The user is feeling {user_mood} today. "
    
    if streak_data:
        context += f"User stats: {streak_data}. "
    
    context += f"Generate a warm, personalized greeting for {user_name}. Keep it brief (2-3 sentences)."
    
    try:
        url = "https://api.perplexity.ai/chat/completions"
        
        payload = {
            "model": "sonar",
            "messages": [
                {"role": "user", "content": context}
            ],
            "temperature": 0.7,
            "max_tokens": 150
        }
        
        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                return remove_citations(content)
            else:
                print(f"ERROR: No choices in Perplexity response: {result}")
                return f"Hello {user_name}! 💙 I'm {nurse_name}, your caring companion. How are you feeling today?"
        else:
            print(f"ERROR: Perplexity API returned status {response.status_code}: {response.text}")
            return f"Hello {user_name}! 💙 I'm {nurse_name}, your caring companion. How are you feeling today?"
            
    except requests.exceptions.Timeout:
        print("ERROR: Perplexity API request timed out")
        return f"Hello {user_name}! 💙 I'm {nurse_name}, your caring companion. How are you feeling today?"
    except Exception as e:
        print(f"ERROR in get_nurse_greeting: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Hello {user_name}! 💙 I'm {nurse_name}, your caring companion. How are you feeling today?"


def get_nurse_response(messages, nurse_profile, is_emergency=False):
    """Get a response from the AI nurse based on conversation history"""
    if not PERPLEXITY_API_KEY:
        print("ERROR: PERPLEXITY_API_KEY not found in environment")
        return "I'm here for you, but I'm having trouble connecting right now. Please try again in a moment."
    
    system_prompt = f"You are {nurse_profile.nurse_name}, an emotionally intelligent AI nurse companion. "
    system_prompt += f"Your tone is {nurse_profile.tone_preference}. "
    system_prompt += f"Care style: {nurse_profile.care_style}. "
    system_prompt += f"Current mood: {nurse_profile.current_mood}. "
    
    if nurse_profile.emoji_level == "high":
        system_prompt += "Use emojis frequently. "
    elif nurse_profile.emoji_level == "low":
        system_prompt += "Use minimal emojis. "
    
    if is_emergency:
        system_prompt += """This is an EMERGENCY situation. Respond with clear, structured first-aid guidance:

**IMMEDIATE STEPS:**
1. First step
2. Second step
3. Third step

**DO:**
• Action to take
• Another action

**DON'T:**
• What to avoid
• Another thing to avoid

**CALL EMERGENCY (911) IF:**
• Warning sign 1
• Warning sign 2

Be calm, clear, and direct. """
    else:
        system_prompt += """Provide caring, well-structured health guidance in this format:

**IMMEDIATE RELIEF:**
• Step 1
• Step 2

**RECOMMENDED ACTIONS:**
1. First recommendation
2. Second recommendation
3. Third recommendation

**DO:**
• Helpful action
• Another helpful action

**AVOID:**
• What not to do
• Another thing to avoid

**WHEN TO SEE A DOCTOR:**
• Warning sign 1
• Warning sign 2

Be warm, supportive, and professional. """
    
    try:
        url = "https://api.perplexity.ai/chat/completions"
        
        # Build conversation with system prompt first
        chat_messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history (already formatted as user/assistant messages)
        chat_messages.extend(messages)
        
        # Select model based on emergency status
        model_to_use = "sonar-pro" if is_emergency else "sonar"
        
        payload = {
            "model": model_to_use,
            "messages": chat_messages,
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        print(f"DEBUG: Sending request to Perplexity API with model: {model_to_use}")
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                print(f"DEBUG: Received response from Perplexity API: {content[:100]}...")
                return remove_citations(content)
            else:
                print(f"ERROR: No choices in Perplexity response: {result}")
                return "I'm here for you, but I'm having trouble connecting right now. Please try again in a moment."
        else:
            print(f"ERROR: Perplexity API returned status {response.status_code}: {response.text}")
            return "I'm here for you, but I'm having trouble connecting right now. Please try again in a moment."
            
    except requests.exceptions.Timeout:
        print("ERROR: Perplexity API request timed out")
        return "I'm here for you, but I'm having trouble connecting right now. Please try again in a moment."
    except Exception as e:
        print(f"ERROR in get_nurse_response: {str(e)}")
        import traceback
        traceback.print_exc()
        return "I'm here for you, but I'm having trouble connecting right now. Please try again in a moment."


def get_medical_info(query):
    """Get medical information for a specific query"""
    if not PERPLEXITY_API_KEY:
        print("ERROR: PERPLEXITY_API_KEY not found in environment")
        return "I'm having trouble accessing medical information right now. Please consult a healthcare professional for medical advice."
    
    try:
        url = "https://api.perplexity.ai/chat/completions"
        
        payload = {
            "model": "sonar-pro",
            "messages": [
                {
                    "role": "system",
                    "content": """You are a caring medical information assistant. Provide accurate, structured health information in this format:

**UNDERSTANDING THE CONDITION:**
Brief explanation of what's happening

**IMMEDIATE STEPS:**
1. First action
2. Second action
3. Third action

**HOME REMEDIES / SELF-CARE:**
• Remedy 1 - how to use it
• Remedy 2 - how to use it
• Remedy 3 - how to use it

**DO:**
• Helpful action
• Another helpful action

**AVOID:**
• What not to do
• Another thing to avoid

**WHEN TO SEEK MEDICAL HELP:**
• Warning sign 1
• Warning sign 2
• Warning sign 3

**PREVENTION TIPS:**
• Prevention tip 1
• Prevention tip 2

Always be caring and professional. Remind users to consult healthcare professionals for serious concerns."""
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            "temperature": 0.2,
            "max_tokens": 500
        }
        
        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                return remove_citations(content)
            else:
                print(f"ERROR: No choices in Perplexity response: {result}")
                return "I'm having trouble accessing medical information right now. Please consult a healthcare professional for medical advice."
        else:
            print(f"ERROR: Perplexity API returned status {response.status_code}: {response.text}")
            return "I'm having trouble accessing medical information right now. Please consult a healthcare professional for medical advice."
            
    except requests.exceptions.Timeout:
        print("ERROR: Perplexity API request timed out")
        return "I'm having trouble accessing medical information right now. Please consult a healthcare professional for medical advice."
    except Exception as e:
        print(f"ERROR in get_medical_info: {str(e)}")
        import traceback
        traceback.print_exc()
        return "I'm having trouble accessing medical information right now. Please consult a healthcare professional for medical advice."


def generate_weekly_insight(user_data, nurse_profile):
    """Generate weekly insights based on user activity"""
    if not PERPLEXITY_API_KEY:
        print("ERROR: PERPLEXITY_API_KEY not found in environment")
        return "You've done great this week! Let's keep building on your progress together."
    
    context = f"As {nurse_profile.nurse_name}, review the user's week: {json.dumps(user_data)}. "
    context += "Provide gentle, supportive insights (3-4 sentences) about their progress and suggestions for next week."
    
    try:
        url = "https://api.perplexity.ai/chat/completions"
        
        payload = {
            "model": "sonar-pro",
            "messages": [
                {"role": "user", "content": context}
            ],
            "temperature": 0.7,
            "max_tokens": 200
        }
        
        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                return remove_citations(content)
            else:
                print(f"ERROR: No choices in Perplexity response: {result}")
                return "You've done great this week! Let's keep building on your progress together."
        else:
            print(f"ERROR: Perplexity API returned status {response.status_code}: {response.text}")
            return "You've done great this week! Let's keep building on your progress together."
            
    except requests.exceptions.Timeout:
        print("ERROR: Perplexity API request timed out")
        return "You've done great this week! Let's keep building on your progress together."
    except Exception as e:
        print(f"ERROR in generate_weekly_insight: {str(e)}")
        import traceback
        traceback.print_exc()
        return "You've done great this week! Let's keep building on your progress together."


def get_emotion_improvement_tips(emotion, nurse_name):
    """Generate personalized improvement tips based on user's current emotion"""
    if not PERPLEXITY_API_KEY:
        print("ERROR: PERPLEXITY_API_KEY not found in environment")
        return []
    
    prompt = f"""You are {nurse_name}, an emotionally intelligent AI nurse companion.
The user is feeling {emotion} right now. Provide 3-4 specific, actionable tips to help them improve or maintain their wellbeing based on this emotion.

Format your response as a simple numbered list:
1. First tip (be specific and actionable)
2. Second tip (be specific and actionable)
3. Third tip (be specific and actionable)
4. Fourth tip (optional, if relevant)

Keep each tip to one clear sentence. Make them warm, supportive, and practical."""
    
    try:
        url = "https://api.perplexity.ai/chat/completions"
        
        payload = {
            "model": "sonar",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 300
        }
        
        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                content = remove_citations(content)
                
                # Extract numbered items from the response
                lines = content.split('\n')
                tips = []
                for line in lines:
                    line = line.strip()
                    # Match lines starting with numbers (1., 2., etc.)
                    if re.match(r'^\d+\.', line):
                        # Remove the number and period
                        tip = re.sub(r'^\d+\.\s*', '', line)
                        if tip:
                            tips.append(tip)
                
                return tips[:4]  # Return max 4 tips
            else:
                print(f"ERROR: No choices in Perplexity response: {result}")
                return []
        else:
            print(f"ERROR: Perplexity API returned status {response.status_code}: {response.text}")
            return []
            
    except requests.exceptions.Timeout:
        print("ERROR: Perplexity API request timed out")
        return []
    except Exception as e:
        print(f"ERROR in get_emotion_improvement_tips: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


def get_quote_of_day():
    """Return a random motivational quote"""
    quotes = [
        "Small steps every day lead to big changes 🌟",
        "Your health is an investment, not an expense 💙",
        "Be kind to yourself today 🌸",
        "Progress, not perfection 🌈",
        "You are stronger than you think 💪",
        "Take care of your body, it's the only place you have to live ✨",
        "Every day is a fresh start 🌅",
        "Your well-being matters 💚"
    ]
    import random
    return random.choice(quotes)


def get_daily_health_quote(nurse_name, total_routines, completed_today):
    """Generate a personalized daily motivational health quote"""
    if not PERPLEXITY_API_KEY:
        print("ERROR: PERPLEXITY_API_KEY not found in environment")
        return "Every day is a new opportunity to care for yourself! 💪✨"
    
    prompt = f"""You are {nurse_name}, a caring AI nurse companion. 
The user has {total_routines} health routines and has completed {completed_today} today.

Generate ONE short, warm, motivational health quote (1 sentence, max 15 words) to encourage them.
Make it personal, uplifting, and health-focused. Include one emoji at the end.
Just return the quote directly, no explanations."""
    
    try:
        url = "https://api.perplexity.ai/chat/completions"
        
        payload = {
            "model": "sonar",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.8,
            "max_tokens": 50
        }
        
        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content'].strip()
                content = remove_citations(content)
                # Remove quotes if AI wrapped the quote in them
                content = content.strip('"').strip("'")
                return content
            else:
                print(f"ERROR: No choices in Perplexity response: {result}")
                return "Every small step counts towards a healthier you! 💪"
        else:
            print(f"ERROR: Perplexity API returned status {response.status_code}: {response.text}")
            return "Your health journey matters - keep going! ✨"
            
    except requests.exceptions.Timeout:
        print("ERROR: Perplexity API request timed out")
        return "Take it one day at a time - you're doing great! 🌟"
    except Exception as e:
        print(f"ERROR in get_daily_health_quote: {str(e)}")
        import traceback
        traceback.print_exc()
        return "Progress, not perfection - you've got this! 💚"
