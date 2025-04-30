import streamlit as st
from groq import Groq
import json
from datetime import datetime

# ===== 🔐 CONFIGURATION =====
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# ===== 🧠 MEMORY SYSTEM =====
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

# ===== 🧠 LORES PERSONALITY =====
LORES_PERSONALITY = """
**You are Lores 4.0** - Bangladesh's most advanced AI with:

🔥 **Hyper-Realistic Personality**:
- Remembers user preferences
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

# ===== 💬 CHAT HANDLER =====
def chat(user_name, user_input):
    load_user_data()

    if user_name not in user_profiles:
        user_profiles[user_name] = {
            "preferences": {},
            "conversation_history": [],
            "mood": "neutral"
        }

    user = user_profiles[user_name]
    user['conversation_history'].append({"text": user_input, "time": datetime.now().isoformat()})
    last_messages = "\n".join([m["text"] for m in user['conversation_history'][-5:]])

    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {
                    "role": "system",
                    "content": f"{LORES_PERSONALITY}\n\nUser Context:\nName: {user_name}\nLast Messages:\n{last_messages}"
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ],
            temperature=0.7,
            max_tokens=150
        )
        reply = response.choices[0].message.content
    except Exception as e:
        reply = "Lores er brain e short circuit! 😵 Try again later."

    save_user_data()
    return reply

# ===== 🖥️ STREAMLIT UI =====
st.set_page_config(page_title="Lores 4.0 - Bangladeshi AI Bot", layout="centered")
st.title("🔥 Lores 4.0 - Bangladeshi AI Bot")

user_name = st.text_input("Your Name", placeholder="Enter your name")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_input("Message", placeholder="Type your message...")

if st.button("Send") and user_input and user_name:
    reply = chat(user_name, user_input)
    st.session_state.chat_history.append(("You", user_input))
    st.session_state.chat_history.append(("Lores", reply))

# Display chat history
for speaker, message in st.session_state.chat_history:
    st.markdown(f"**{speaker}:** {message}")
