import streamlit as st
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

st.title("The Multiverse of Chatbots")

st.sidebar.title("App Settings")

personality = st.sidebar.selectbox(
    "Who do u want to talk to?",
    [
        "A panicked college student at 3 AM",
        "A 1920s Mafia Boss",
        "A highly sarcastic fitness coach"
    ]
)
intensity = st.sidebar.slider("Intensity Level", min_value=1, max_value=10, value=5)
if personality == "A panicked college student at 3 AM":
    bot_avatar = "☕"
elif personality == "A 1920s Mafia Boss":
    bot_avatar = "🕶️"
elif personality == "A highly sarcastic fitness coach":
    bot_avatar = "💪"
else:
    bot_avatar = "🤖"

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

if "messages" not in st.session_state:
    st.session_state.messages=[]

for message in st.session_state.messages:
    current_avatar = bot_avatar if message["role"] == "assistant" else None
    with st.chat_message(message["role"], avatar=current_avatar):
        st.write(message["content"])

user_message = st.chat_input("Say something...")
if user_message:
    with st.chat_message("user"):
        st.write(user_message)
    st.session_state.messages.append({"role":"user","content":user_message})
    ai_instruction = (
        f"You are acting as {personality}. On a scale of 1 to 10, your commitment and intensity "
        f"level to this persona is exactly {intensity}. Respond to the message sent by the user "
        f"staying completely in character: {user_message}"
    )
    with st.spinner("Connecting...."):
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=ai_instruction
        )
        with st.chat_message("assistant",avatar=bot_avatar):
            st.write(response.text)
            
        st.session_state.messages.append({"role":"assistant","content":response.text})
else:
    st.write("Please write prompt.")
