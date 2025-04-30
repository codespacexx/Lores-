import random
import json
from datetime import datetime
from groq import Groq
import gradio as gr
import requests
import os

# ===== 🔥 CONFIGURATION =====
GROQ_API_KEY = "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"  # Replace if needed

# ===== 🧠 USER MEMORY SYSTEM =====
user_profiles = {}

def load_user_data():
    try:
        with open('user_data.json', 'r') as f:
            return json.load(f)
    except:
        return {}

def save_user_data():
    with open('user_data.json', 'w') as f:
        json.dump(user_profiles, f)

user_profiles = load_user_data()

# ===== 🤖 LORES PERSONALITY CORE =====
LORES_PERSONALITY = """
**You are Lores 4.0** - Bangladesh's most advanced AI with:

🔥 **Features**:
- Banglish (Bangla+English) responses
- Bangladeshi cultural references
- Witty humor with emojis (😂, 🥲, 🤣)
- Memory of past conversations

🎯 **Rules**:
1. Keep responses under 2 sentences
2. Never repeat the same joke
3. Adapt to user's mood
"""

# ===== 🎭 CONTENT LIBRARY =====
BANGLADESHI_MEMES = {
    "food": [
        "https://i.imgur.com/Fc7WX7B.jpg",  # Fuchka meme
        "https://i.imgur.com/JtQY9ZL.jpg"   # Biryani meme
    ],
    "sports": [
        "https://i.imgur.com/KLmW5xU.jpg",  # Cricket meme
        "https://i.imgur.com/NqQ3rRt.jpg"   # Football meme
    ],
    "traffic": [
        "https://i.imgur.com/PqXwCb1.jpg",  # Dhaka traffic
        "https://i.imgur.com/XyZ1wQ9.jpg"   # CNG meme
    ]
}

# ===== 🚀 INITIALIZE SERVICES =====
try:
    client = Groq(api_key=GROQ_API_KEY)
    print("✅ Groq client initialized")
except Exception as e:
    print(f"❌ Groq init error: {e}")
    client = None

# ===== 💎 CORE FUNCTIONS =====
def generate_ai_response(user_id, prompt):
    if not client:
        return "Amar AI brain offline! 😵 Try again later."
    
    user = user_profiles.get(user_id, {"conversation_history": []})
    last_messages = "\n".join([msg["text"] for msg in user["conversation_history"][-3:]])
    
    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"{LORES_PERSONALITY}\n\nConversation History:\n{last_messages}"
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
        return response.choices[0].message.content
    except Exception as e:
        print(f"API error: {e}")
        return "Amar server e gorom lagtese! 🥵"

def get_meme_url(category):
    return random.choice(BANGLADESHI_MEMES.get(category, BANGLADESHI_MEMES["food"]))

# ===== 🎨 GRADIO INTERFACE =====
def chat_with_lores(message, history):
    user_id = "gradio_user"
    
    # Initialize user profile
    if user_id not in user_profiles:
        user_profiles[user_id] = {
            "name": "Gradio User",
            "conversation_history": []
        }
    
    # Store message
    user_profiles[user_id]["conversation_history"].append({
        "text": message,
        "time": datetime.now().isoformat()
    })
    
    # Generate response
    if "meme" in message.lower():
        category = detect_meme_category(message)
        meme_url = get_meme_url(category)
        return f"Here's your meme! 😄", meme_url
    else:
        response = generate_ai_response(user_id, message)
        save_user_data()
        return response, None

def detect_meme_category(text):
    text = text.lower()
    if "traffic" in text:
        return "traffic"
    elif any(word in text for word in ["cricket", "football", "sports"]):
        return "sports"
    return "food"

# ===== 🖥️ CUSTOM THEME =====
custom_css = """
#chatbot {
    font-family: "Helvetica Neue", Arial, sans-serif;
    min-height: 400px;
}
.meme-container {
    margin-top: 20px;
    text-align: center;
}
footer {
    visibility: hidden;
}
"""

# ===== 🚀 LAUNCH APP =====
with gr.Blocks(css=custom_css, theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🤖 Lores AI - Bangladeshi Chatbot
    *"Ami Banglai ghum nei, English-eo pari!"* 😄
    """)
    
    with gr.Row():
        chatbot = gr.Chatbot(
            elem_id="chatbot",
            bubble_full_width=False,
            avatar_images=(
                "https://i.imgur.com/7W6wCwW.png",  # User avatar
                "https://i.imgur.com/4Z3QZ2y.png"   # Bot avatar
            )
        )
        
    with gr.Row():
        msg = gr.Textbox(
            placeholder="Ki bolben? (What will you say?)",
            label="Type your message",
            container=False
        )
        
    with gr.Row():
        meme_output = gr.Image(
            label="Meme of the Day",
            visible=False,
            elem_classes="meme-container"
        )
    
    # Event handlers
    msg.submit(
        chat_with_lores,
        [msg, chatbot],
        [chatbot, meme_output],
    ).then(
        lambda: gr.Textbox(value="", interactive=True),
        None,
        [msg],
        queue=False
    )
    
    # Examples
    gr.Examples(
        examples=[
            ["Ki khobor Lores?"],
            ["Amake ekta meme dekhaiyen"],
            ["Dhaka traffic er meme pathan"]
        ],
        inputs=msg
    )

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True
)
