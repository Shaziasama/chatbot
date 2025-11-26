import streamlit as st
import os
import google.generativeai as genai
from datetime import datetime 

# --- 1. Configuration and API Key Handling ---

# Set Streamlit Page Configuration for better aesthetics and layout
st.set_page_config(
    page_title="Intelligent Chatbot 🤖",
    layout="wide", 
    initial_sidebar_state="expanded" 
)

st.title("💡 Personal AI Chatbot")
st.markdown("---") 

# Key Loading Logic (Crucial for secure deployment on Streamlit Cloud)
GEMINI_API_KEY = None
try:
    # 1. Prioritize Streamlit Secrets (This is how it works on Streamlit Cloud)
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"] 
except KeyError:
    # 2. Fallback to OS environment (For local testing)
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    # Error message shown if the key is not set in Streamlit Cloud Secrets
    st.error("❌ **GEMINI_API_KEY** nahi mili. Please Streamlit Cloud Secrets mein set karein.")
    st.stop()
    
# Gemini Configuration and Model Initialization
try:
    genai.configure(api_key=GEMINI_API_KEY)
    MODEL_NAME = "gemini-2.5-flash"
    # Initialize GenerativeModel once and store it in session state
    if "gemini_model" not in st.session_state:
         st.session_state["gemini_model"] = genai.GenerativeModel(MODEL_NAME)
except Exception as e:
    st.error(f"Error configuring Gemini: Could not initialize model. Details: {e}")
    st.stop()


# --- Sidebar for Settings and Features ---
with st.sidebar:
    st.header("⚙️ Chat Settings")
    
    # Define personality options for the user to select
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
    
    # Clear Chat Button Function
    def clear_chat_history():
        st.session_state.messages = []
        # Reset the chat session to clear model context (essential for memory)
        st.session_state["chat_session"] = st.session_state["gemini_model"].start_chat(history=[])

    if st.button("🗑️ Clear Chat", help="Removes all messages from the history."):
        clear_chat_history()
        st.rerun()

selected_personality_instruction = personality_options[selected_personality_name]

# --- Session State Initialization (Chat History and Chat Session) ---
if "messages" not in st.session_state:
    st.session_state["messages"] = []
    
# Gemini Chat Session initialization (Using start_chat() for context)
if "chat_session" not in st.session_state:
    try:
        # start_chat() is used to maintain conversation context and memory
        st.session_state["chat_session"] = st.session_state["gemini_model"].start_chat(history=[])
    except Exception as e:
        st.error(f"Error starting chat session: {e}")
        st.stop()
        
# --- Display Chat History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        try:
            timestamp_str = datetime.fromisoformat(message["timestamp"]).strftime("%H:%M")
        except:
            timestamp_str = "Time N/A"
        
        st.caption(f"_{message['role'].capitalize()} at {timestamp_str}_")
        st.markdown(message['content']) 

# --- Handle User Input and Generate Response ---

if prompt := st.chat_input("What is up?"):
    current_time = datetime.now()
    
    # 1. Display and save user message immediately
    with st.chat_message("user"):
        timestamp_str = current_time.strftime("%H:%M")
        st.caption(f"_User at {timestamp_str}_")
        st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt, "timestamp": current_time.isoformat()})

    # 2. Generate bot response (Using persistent chat session)
    with st.chat_message("assistant"):
        with st.spinner(f"AI Assistant ({selected_personality_name}) thinking..."):
            try:
                # Add personality instruction to the prompt to guide the AI's tone
                full_prompt = f"[{selected_personality_instruction}] {prompt}"
                
                # Send message through the persistent chat session
                response = st.session_state["chat_session"].send_message(full_prompt).text
                
                # Display and save assistant response
                current_time = datetime.now()
                timestamp_str = current_time.strftime("%H:%M")
                st.caption(f"_Bot at {timestamp_str}_")
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response, "timestamp": current_time.isoformat()})
            
            except Exception as e:
                error_msg = f"An API Error occurred: {e}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": f"Sorry, I ran into an error. Please check the console.", "timestamp": current_time.isoformat()})
