from flask import Flask, request, jsonify
import requests
from groq import Groq
import random
import time
import os
from datetime import datetime
import json

app = Flask(__name__)

# ===== 🔥 DIRECT CONFIGURATION =====
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

# ===== 🤖 LORES PERSONALITY CORE =====
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
- Include 1-2 emojis per message (😂, 🫠, 💀)
- Never repeat the same joke twice
"""

# ===== 🎭 CONTENT LIBRARY =====
BANGLADESHI_MEMES = {
    "food": [
        "https://i.imgur.com/xyz123.jpg",  # Replace with actual URLs
        "https://i.imgur.com/abc456.jpg"
    ],
    "sports": [
        "https://i.imgur.com/def789.jpg",
        "https://i.imgur.com/ghi012.jpg"
    ],
    "traffic": [
        "https://i.imgur.com/jkl345.jpg",
        "https://i.imgur.com/mno678.jpg"
    ]
}

# ===== 🚀 INITIALIZE SERVICES =====
try:
    client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    print(f"Failed to initialize Groq client: {str(e)}")
    client = None

load_user_data()

# ===== 🌐 FLASK ROUTES =====
@app.route('/', methods=['GET'])
def verify():
    if request.args.get('hub.mode') == 'subscribe':
        if request.args.get('hub.verify_token') == VERIFY_TOKEN:
            return request.args.get('hub.challenge'), 200
        return "Invalid verification token", 403
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
    if message.get('is_echo'):
        return
    
    user_text = message.get('text', '')
    user_profiles[sender_id]['conversation_history'].append({
        "text": user_text,
        "time": datetime.now().isoformat()
    })
    
    if "meme" in user_text.lower():
        send_personalized_meme(sender_id)
    else:
        generate_ai_response(sender_id, user_text)
    
    save_user_data()

def generate_ai_response(user_id, prompt):
    if not client:
        send_message(user_id, "Amar AI brain offline! 😵 Try again later.")
        return
    
    user = user_profiles[user_id]
    last_messages = "\n".join([msg['text'] for msg in user['conversation_history'][-5:]])
    
    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": f"{LORES_PERSONALITY}\n\nUser Context:\nName: {user['name']}\nLast Messages:\n{last_messages}"
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
        send_message(user_id, response.choices[0].message.content)
    except Exception as e:
        print(f"Error: {e}")
        send_message(user_id, "Amar server e gorom lagtese! 🥵 Try again later.")

def send_personalized_meme(user_id):
    user = user_profiles[user_id]
    preferred_category = "food"  # Default
    
    last_msg = user['conversation_history'][-1]['text'].lower()
    if "traffic" in last_msg:
        preferred_category = "traffic"
    elif "sports" in last_msg:
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
