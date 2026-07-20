import streamlit as st
import requests
from google import genai
import os
import random
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
st.title("MY AI IMAGE GENERATOR")
st.sidebar.title("Settings")
art_style = st.sidebar.selectbox("Select Art Style", [
    "Photorealistic",
    "Cyberpunk",
    "3D Render",
    "Watercolor"
])

inspiration_prompts = [
    "An astronaut riding a horse on Mars",
    "A cyberpunk street food vendor in Tokyo with neon signs",
    "An underwater palace carved out of glowing coral reef",
    "A majestic steampunk owl flying over a Victorian city",
    "A cozy cottage built inside a giant translucent mushroom in a magical forest"
]

if "prompt_input" not in st.session_state:
    st.session_state["prompt_input"] = ""

width = st.sidebar.slider("Image Width", min_value=256, max_value=1024, value=768)
height = st.sidebar.slider("Image Height", min_value=256, max_value=1024, value=768)

def enhance_prompt():
    current_text = st.session_state["prompt_input"]
    if current_text:
        ai_instruction = (
            f"Create a highly detailed image of {current_text}. The scene should be captured using a [e.g., 35mm lens], "
            f"featuring [e.g., dramatic golden hour lighting], with sharp focus, realistic textures, and a cinematic environment. "
            f"Render it as a professional DSLR photograph with 8k resolution."
        )
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=ai_instruction
        )
        st.session_state["prompt_input"] = response.text
    else:
        st.session_state["show_warning"] = True

def surprise_me():
    random_prompt = random.choice(inspiration_prompts)
    st.session_state["prompt_input"] = random_prompt
    st.session_state["trigger_surprise_generation"] = True


user_prompt = st.text_input(
    "Describe your masterpiece",
    key="prompt_input"
)

if st.session_state.pop("show_warning", False):
    st.warning("Please add an image description.")


col1, col2 = st.columns(2)
with col1:
    st.button("Enhance Prompt by AI", on_click=enhance_prompt)
with col2:
    st.button("Surprise Me!", on_click=surprise_me)

should_generate = st.button("Generate Image") or st.session_state.pop("trigger_surprise_generation", False)
        
if should_generate:
    current_prompt = st.session_state["prompt_input"]
    if current_prompt:
        with st.spinner("Rendering the image"):
            full_prompt = f"{current_prompt}. Art style: {art_style}"
            url = f"https://image.pollinations.ai/prompt/{full_prompt}?width={width}&height={height}"
            response = requests.get(url)
            
            if response.status_code == 200:
                st.success("Image Generated")
                st.image(response.content, caption=current_prompt)
                st.download_button(
                    "Download Image",
                    data=response.content,
                    file_name=f"{art_style}_image.png",
                    mime="image/png"
                )
            else:
                st.error(f"Failed to generate image. Error code: {response.status_code}")
    else:
        st.warning("Please add an image description.")