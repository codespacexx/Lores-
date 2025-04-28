from flask import Flask, request, jsonify
import requests
from groq import Groq
import random
import time
import os
from datetime import datetime
import json

app = Flask(__name__)

# ===== 🔥 PREMIUM CONFIGURATION =====
ACCESS_TOKEN = "EAAAAUaZA8jlABOxzLZBVPzOaJHbp5ObiZCDjnq1yAasOZAdMWWdhJi5GZC37nyzkbvbKEcY0d6rrHI3ndsIw4maHFGera6wHxVo1hYT2rVZC7KDHuUIwOpleRLTv9YMjlnyWuikEdSkvQzZCPaQvzo2PILZA4qvIS5sZBOiOJoBzEWQRBKLpjoJJBqEa7b0QmLzfgeESHo9mxnQZDZD"
VERIFY_TOKEN = "lores_4ever_bangladesh"
GROQ_API_KEY = "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"

# ===== 🧠 USER MEMORY SYSTEM =====
user_profiles = {}

def load_user_data():
    global user_profiles
    try:
        with open('user_data.json', 'r') as f:
            user_profiles = json.load(f)
    except:
        user_profiles = {}

def save_user_data():
    with open('user_data.json', 'w') as f:
        json.dump(user_profiles, f)

# ===== 🤖 LORES 4.0 PERSONALITY CORE =====
LORES_PERSONALITY = """
**You are Lores 4.0** - Bangladesh's most advanced AI with:

🔥 **Hyper-Realistic Personality**:
- Remembers user preferences ("Last time you said you love fuchka!")
- Adapts humor style to each user
- Uses natural conversational flow

💎 **Premium Features**:
1. Mood Detection (Happy/Sad/Angry responses)
2. Personal Meme Recommendations
3. Bangladeshi Pop Culture Expert
4. Multi-conversation Memory
5. Emotional Support Mode

🎯 **Response Rules**:
- Use perfect Banglish mixing
- 20% chance to send voice replies
- Include 1-2 emojis per message (😂, 🫠, 💀)
- Never repeat the same joke twice
"""

# ===== 🎭 CONTENT LIBRARY =====
BANGLADESHI_MEMES = {
    "food": ["https://i.imgur.com/fuchka.jpg", "https://i.imgur.com/borhani.jpg"],
    "sports": ["https://i.imgur.com/bpl_roast.jpg", "https://i.imgur.com/shakib_meme.jpg"],
    "traffic": ["https://i.imgur.com/dhaka_jam.jpg", "https://i.imgur.com/cng_meme.jpg"]
}

VOICE_RESPONSES = [
    "https://example.com/voice1.mp3",
    "https://example.com/voice2.mp3"
]

# ===== 🚀 INITIALIZE SERVICES =====
client = Groq(api_key=GROQ_API_KEY)
load_user_data()

# ===== 🌐 FLASK ROUTES =====
@app.route('/', methods=['GET'])
def verify():
    if request.args.get('hub.mode') == 'subscribe':
        if request.args.get('hub.verify_token') == VERIFY_TOKEN:
            return request.args['hub.challenge'], 200
        return "Token mismatch!", 403
    return "Lores 4.0 is OPERATIONAL 🔥", 200

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    if data.get('object') == 'page':
        for entry in data['entry']:
            for event in entry.get('messaging', []):
                process_event(event)
    return jsonify({"status": "ok"}), 200

# ===== 💎 CORE FUNCTIONALITY =====
def process_event(event):
    sender_id = event['sender']['id']
    
    # Initialize user profile if new
    if sender_id not in user_profiles:
        user_profiles[sender_id] = {
            "name": get_user_name(sender_id),
            "preferences": {},
            "conversation_history": [],
            "mood": "neutral"
        }
    
    if 'message' in event:
        handle_message(sender_id, event['message'])
    elif 'postback' in event:
        handle_postback(sender_id, event['postback'])

def handle_message(sender_id, message):
    # Skip if bot's own message
    if message.get('is_echo'):
        return
    
    # Update conversation history
    user_text = message.get('text', '')
    user_profiles[sender_id]['conversation_history'].append({
        "text": user_text,
        "time": datetime.now().isoformat()
    })
    
    # Special commands
    if "meme" in user_text.lower():
        send_personalized_meme(sender_id)
    elif "voice" in user_text.lower():
        send_voice_response(sender_id)
    else:
        generate_ai_response(sender_id, user_text)
    
    save_user_data()

# ===== 🧠 INTELLIGENT FUNCTIONS =====
def generate_ai_response(user_id, prompt):
    # Get user context
    user = user_profiles[user_id]
    last_5_messages = "\n".join([msg['text'] for msg in user['conversation_history'][-5:]])
    
    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": f"{LORES_PERSONALITY}\n\nUser Context:\nName: {user['name']}\nLast Messages:\n{last_5_messages}"
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            model="llama3-70b-8192",
            temperature=0.7,
            max_tokens=150
        )
        
        reply = response.choices[0].message.content
        
        # 20% chance to send voice instead of text
        if random.random() < 0.2:
            send_voice_response(user_id)
        else:
            send_message(user_id, reply)
            
    except Exception as e:
        print(f"Error: {e}")
        send_message(user_id, "Amar server e gorom lagtese! 🥵 Try again later.")

def send_personalized_meme(user_id):
    user = user_profiles[user_id]
    
    # Determine preferred meme category
    preferred_category = "food"  # Default
    if "traffic" in user['conversation_history'][-1]['text'].lower():
        preferred_category = "traffic"
    elif "sports" in user['conversation_history'][-1]['text'].lower():
        preferred_category = "sports"
    
    meme_url = random.choice(BANGLADESHI_MEMES[preferred_category])
    
    requests.post(
        f"https://graph.facebook.com/v19.0/me/messages?access_token={ACCESS_TOKEN}",
        json={
            "recipient": {"id": user_id},
            "message": {
                "attachment": {
                    "type": "image",
                    "payload": {"url": meme_url}
                }
            }
        }
    )

# ===== ✨ ENHANCED MESSAGING =====
def send_message(recipient_id, text):
    # Typing indicator
    requests.post(
        f"https://graph.facebook.com/v19.0/me/messages?access_token={ACCESS_TOKEN}",
        json={
            "recipient": {"id": recipient_id},
            "sender_action": "typing_on"
        }
    )
    time.sleep(1)
    
    # Send message
    requests.post(
        f"https://graph.facebook.com/v19.0/me/messages?access_token={ACCESS_TOKEN}",
        json={
            "recipient": {"id": recipient_id},
            "message": {"text": text[:2000]}
        }
    )

def send_voice_response(recipient_id):
    voice_url = random.choice(VOICE_RESPONSES)
    requests.post(
        f"https://graph.facebook.com/v19.0/me/messages?access_token={ACCESS_TOKEN}",
        json={
            "recipient": {"id": recipient_id},
            "message": {
                "attachment": {
                    "type": "audio",
                    "payload": {"url": voice_url}
                }
            }
        }
    )

def get_user_name(user_id):
    try:
        response = requests.get(
            f"https://graph.facebook.com/v19.0/{user_id}",
            params={"access_token": ACCESS_TOKEN}
        )
        return response.json().get('name', 'User')
    except:
        return "User"

# ===== 🏁 RUN THE BOT =====
if __name__ == '__main__':
    print("""
    ██╗      ██████╗ ██████╗ ███████╗███████╗
    ██║     ██╔═══██╗██╔══██╗██╔════╝██╔════╝
    ██║     ██║   ██║██████╔╝█████╗  ███████╗
    ██║     ██║   ██║██╔══██╗██╔══╝  ╚════██║
    ███████╗╚██████╔╝██║  ██║███████╗███████║
    ╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚══════╝
    """)
    print("🔥 Lores 4.0 - Bangladeshi AI Assistant")
    print(f"🤖 Developer: Alvee Mahmud | {datetime.now().year}")
    app.run(host='0.0.0.0', port=5000, debug=True)