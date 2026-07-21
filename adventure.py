import os
import json
import io
import urllib.parse
import requests
import streamlit as st
from google import genai
from google.genai import types
from gtts import gTTS
from dotenv import load_dotenv

load_dotenv()
st.title("AI Visual Novel Engine")

@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

client = get_gemini_client()

st.sidebar.title("Story Settings")
genre = st.sidebar.selectbox("Story Genre", ["Cyberpunk", "Dark Fantasy", "Sci-Fi Mystery", "Cozy Adventure", "Eldritch Horror"])
art_style = st.sidebar.selectbox("Art Style", ["Anime Concept Art", "Digital Oil Painting", "Pixel Art", "Cinematic Photorealistic", "Comic Book"])

SYSTEM_INSTRUCTION = f"""
You are an interactive Visual Novel Engine. The current genre is '{genre}' and the art style is '{art_style}'.
For every turn of the story, you MUST strictly respond with a single JSON object containing these keys:
1. "story_text": (string) 2-3 immersive narrative sentences describing the scene or consequences.
2. "image_prompt": (string) A detailed prompt for an image generator capturing the current scene in {art_style} style.
3. "options": (list of strings) 2 to 3 distinct choices for the user's next action.

Do not wrap the output in markdown fences like ```json. Output raw JSON only.
"""
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat" not in st.session_state:
    st.session_state.chat = client.chats.create(
        model="gemini-2.5-flash",
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            response_mime_type="application/json"
        )
    )

def fetch_pollinations_image(prompt: str):
    encoded_prompt = urllib.parse.quote(f"{prompt}, {art_style} style, high quality")
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        st.toast("🎨 Image server returned an error, skipping visual...", icon="⚠️")
        return None

def generate_tts_audio(text: str):
    tts = gTTS(text=text, lang="en")
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    return fp.getvalue()

def process_turn(user_action: str):
    if user_action:
        st.session_state.messages.append({"role": "user", "text": user_action})
    prompt_input = user_action if user_action else f"Begin a brand new {genre} story."
    response = st.session_state.chat.send_message(prompt_input)
    raw_text = response.text
    
    data = json.loads(raw_text)
    story_text = data.get("story_text", "")
    image_prompt = data.get("image_prompt", "")
    options = data.get("options", [])
    

    img_bytes = fetch_pollinations_image(image_prompt) if image_prompt else None
    audio_bytes = generate_tts_audio(story_text) if story_text else None

    st.session_state.messages.append({
        "role": "model",
        "story_text": story_text,
        "image": img_bytes,
        "audio": audio_bytes,
        "options": options
    })


if len(st.session_state.messages) == 0:
    process_turn(None)

for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.write(msg['text'])
    else:
        with st.chat_message("assistant"):
            st.write(msg["story_text"])
            
            if msg.get("image"):
                st.image(msg["image"], use_column_width=True)
                
            if msg.get("audio"):
                st.audio(msg["audio"], format="audio/mp3")


latest_turn = st.session_state.messages[-1] if st.session_state.messages else None

if latest_turn and latest_turn["role"] == "model" and latest_turn.get("options"):
    st.write("---")
    st.subheader("What do you do next?")
    
    cols = st.columns(len(latest_turn["options"]))
    for idx, option in enumerate(latest_turn["options"]):
        with cols[idx]:
            if st.button(option, key=f"btn_{len(st.session_state.messages)}_{idx}"):
                process_turn(option)
                st.rerun()