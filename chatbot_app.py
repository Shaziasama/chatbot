import streamlit as st
import google.generativeai as genai
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv() 

# 1. Page Configuration for UI
st.set_page_config(
    page_title="Intelligent Chatbot 🤖",
    layout="wide",                       
    initial_sidebar_state="expanded"     
)

# --- Main Title (English) ---
st.title("💡 Personal AI Chatbot")
st.markdown("---") 

# --- Sidebar for Settings ---
with st.sidebar:
    st.header("⚙️ Chat Settings")
    
    # Personality selection
    personality_options = {
        "Friendly": "Be friendly and encouraging.",
        "Professional": "Be professional and concise.",
        "Funny": "Be humorous and witty."
    }
    selected_personality_name = st.selectbox(
        "Choose Chatbot Personality:",
        list(personality_options.keys()),
        key="chatbot_personality"
    )
    st.markdown("---")
    
    # Clear Chat Button
    if st.button("🗑️ Clear Chat", help="Removes all messages from the history."):
        st.session_state.messages = []
        st.rerun()

selected_personality_instruction = personality_options[selected_personality_name]

# Configure Google Gemini API
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    st.error("Error: GEMINI_API_KEY not found. Please set it in your .env file.")
else:
    genai.configure(api_key=gemini_api_key)


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 2. Display Chat History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        try:
            timestamp_str = datetime.fromisoformat(message["timestamp"]).strftime("%H:%M")
        except ValueError:
            timestamp_str = "Time"
        
        # Display caption in English
        st.caption(f"_{message['role'].capitalize()} at {timestamp_str}_")
        st.markdown(message['content']) 

# --- 3. React to User Input ---
if prompt := st.chat_input("What is up?"):
    current_time = datetime.now()
    
    # 3a. Display and save user message immediately
    with st.chat_message("user"):
        timestamp_str = current_time.strftime("%H:%M")
        st.caption(f"_User at {timestamp_str}_") # English caption
        st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt, "timestamp": current_time.isoformat()})

    # 3b. Generate bot response (Using the corrected model name)
    try:
        model = genai.GenerativeModel("gemini-2.5-flash") 
        full_prompt = f"Respond briefly. {selected_personality_instruction} {prompt}"
        response = model.generate_content(full_prompt).text
    except genai.types.StopCandidateException:
         response = "Sorry, my response was blocked due to safety settings."
    except Exception as e:
        response = f"API Error: Could not get a response. Please check your API key and connection. Details: {e}"

    # 3c. Display and save assistant response immediately
    with st.chat_message("assistant"):
        current_time = datetime.now()
        timestamp_str = current_time.strftime("%H:%M")
        st.caption(f"_Bot at {timestamp_str}_") # English caption
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response, "timestamp": current_time.isoformat()})
