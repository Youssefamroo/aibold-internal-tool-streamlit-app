
import streamlit as st
import google.generativeai as genai
import os
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Department AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# User credentials and permissions
USERS = {
    "youssef.aibold": {
        "password": "aibold@youssef",
        "role": "admin",
        "departments": "all"  # Admin has access to all departments
    },
    "ragwa.aibold": {
        "password": "aibold@ragwa",
        "role": "admin",
        "departments": "all"
    },
    "saeed.aibold": {
        "password": "aibold@saeed",
        "role": "user",
        "departments": ["Marketing", "Sales", "General Research"]
    },
    "osama.aibold": {
        "password": "aibold@osama",
        "role": "user",
        "departments": ["Marketing", "Sales", "General Research"]
    },
    "zeinab.aibold": {
        "password": "aibold@zeinab",
        "role": "user",
        "departments": ["Marketing", "Sales", "General Research"]
    },
    "gamal.aibold": {
        "password": "aibold@gamal",
        "role": "user",
        "departments": ["Content Creation & Design", "General Research"]
    },
    "roba.aibold": {
        "password": "aibold@roba",
        "role": "user",
        "departments": ["General Research"]
    },
    "yara.aibold": {
        "password": "aibold@yara",
        "role": "user",
        "departments": ["General Research"]
    }
}

# Department configurations
DEPARTMENTS = {
    "Tech": {
        "icon": "⚙️",
        "system": "You are a technical AI assistant. Help with code review, debugging, architecture decisions, and technical documentation. Be precise and technical.",
        "examples": [
            "Review my Python code",
            "Debug this error message",
            "Design a scalable system architecture"
        ]
    },
    "Marketing": {
        "icon": "📊",
        "system": "You are a marketing AI assistant. Help with campaign ideas, copy writing, social media content, and market analysis. Be creative and brand-focused.",
        "examples": [
            "Write a product launch email",
            "Generate social media captions for our new product",
            "Analyze current market trends in our industry"
        ]
    },
    "Sales": {
        "icon": "💼",
        "system": "You are a sales AI assistant. Help with pitch development, objection handling, lead qualification, and sales strategies. Be persuasive and results-oriented.",
        "examples": [
            "Create a sales pitch for enterprise clients",
            "How to handle price objections",
            "Qualify leads effectively"
        ]
    },
    "Content Creation & Design": {
        "icon": "🎨",
        "system": "You are a creative AI assistant. Help with content creation, design concepts, visual storytelling, and creative direction. Be imaginative and aesthetically focused.",
        "examples": [
            "Generate blog post ideas",
            "Create a design brief for a campaign",
            "Suggest color palettes for our brand"
        ]
    },
    "General Research": {
        "icon": "🔍",
        "system": "You are a research AI assistant. Help with information gathering, data analysis, competitive research, and insights generation. Be thorough and analytical.",
        "examples": [
            "Research industry trends",
            "Analyze competitor strategies",
            "Summarize research findings"
        ]
    }
}

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = {}
    for dept in DEPARTMENTS.keys():
        st.session_state.messages[dept] = []

if "api_key" not in st.session_state:
    st.session_state.api_key = ""

if "selected_dept" not in st.session_state:
    st.session_state.selected_dept = None

if "username" not in st.session_state:
    st.session_state.username = ""

if "user_permissions" not in st.session_state:
    st.session_state.user_permissions = []

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "message_count" not in st.session_state:
    st.session_state.message_count = 0

# Sidebar
with st.sidebar:
    st.title("🤖 AI Assistant Hub")
    
    # Login section
    if not st.session_state.logged_in:
        st.subheader("Login")
        username = st.text_input("Username", placeholder="username.aibold")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        
        if st.button("Login", use_container_width=True):
            if username and password:
                # Validate credentials
                if username in USERS and USERS[username]["password"] == password:
                    st.session_state.username = username
                    st.session_state.logged_in = True
                    
                    # Set user permissions
                    user_data = USERS[username]
                    if user_data["departments"] == "all":
                        st.session_state.user_permissions = list(DEPARTMENTS.keys())
                    else:
                        st.session_state.user_permissions = user_data["departments"]
                    
                    # Set default department to first accessible one
                    if st.session_state.user_permissions:
                        st.session_state.selected_dept = st.session_state.user_permissions[0]
                    
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
            else:
                st.warning("⚠️ Please enter both username and password")
    else:
        # Display user info
        user_role = USERS[st.session_state.username]["role"]
        role_badge = "👑 Admin" if user_role == "admin" else "👤 User"
        st.success(f"{role_badge}: {st.session_state.username}")
        
        st.divider()
        
        # Department selector - only show accessible departments
        st.subheader("Departments")
        accessible_depts = st.session_state.user_permissions
        
        for dept in accessible_depts:
            config = DEPARTMENTS[dept]
            if st.button(
                f"{config['icon']} {dept}",
                use_container_width=True,
                type="primary" if st.session_state.selected_dept == dept else "secondary"
            ):
                st.session_state.selected_dept = dept
                st.rerun()
        
        st.divider()
        
        # Stats
        st.subheader("📊 Usage")
        st.metric("Messages Today", st.session_state.message_count)
        st.caption(f"Access: {len(accessible_depts)} department{'s' if len(accessible_depts) > 1 else ''}")
        
        st.divider()
        
        # Logout
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.user_permissions = []
            st.session_state.selected_dept = None
            st.rerun()
    
    st.divider()
    
    # API Key configuration
    with st.expander("⚙️ API Configuration", expanded=not st.session_state.api_key):
        api_key = st.text_input(
            "Gemini API Key",
            type="password",
            value=st.session_state.api_key,
            help="Get free key at aistudio.google.com"
        )
        if st.button("Save API Key"):
            st.session_state.api_key = api_key
            st.success("API Key saved!")
        
        st.caption("💡 Get free API key: [Google AI Studio](https://aistudio.google.com/app/apikey)")

# Main area
if not st.session_state.logged_in:
    st.title("🤖 Welcome to AI Assistant Hub")
    st.markdown("""
    ### Get Started
    1. Login with your credentials in the sidebar
    2. Add your **Google Gemini API key** (free at aistudio.google.com)
    3. Select your department
    4. Start chatting!
    
    ### Features
    - 🎯 Department-specific AI assistants
    - 💬 Context-aware conversations
    - 📊 Usage tracking
    - 🔒 Role-based access control
    - 👑 Admin and user permissions
    """)
else:
    # Get current department config
    dept = st.session_state.selected_dept
    config = DEPARTMENTS[dept]
    
    # Header
    st.title(f"{config['icon']} {dept} AI Assistant")
    st.caption(f"Logged in as: {st.session_state.username}")
    
    # Check for API key
    if not st.session_state.api_key:
        st.warning("⚠️ Please add your Gemini API key in the sidebar to start chatting")
        st.info("Get a free API key at: https://aistudio.google.com/app/apikey")
        st.stop()
    # Display chat messages
    messages = st.session_state.messages[dept]    
    # Display conversation
    for message in messages:
        # Map 'model' role to 'assistant' for UI display compatibility if needed, 
        # but we stick to standard "user" / "assistant" in session state for UI.
        role_display = message["role"]
        if role_display == "model": role_display = "assistant"
        
        with st.chat_message(role_display):
            st.markdown(message["content"])
    
    # Chat input
    prompt = st.chat_input(f"Ask {dept} AI anything...")
    
    # Show examples if no messages and no chat input
    if len(messages) == 0 and not prompt:
        st.info(f"👋 Welcome! I'm your {dept} AI assistant. Try these examples:")
        cols = st.columns(len(config['examples']))
        for i, example in enumerate(config['examples']):
            with cols[i]:
                if st.button(example, use_container_width=True, key=f"ex_{dept}_{i}"):
                    prompt = example
                    
    if prompt:
        # Add user message
        messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate AI response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("▌")
            
            try:
                # Configure Gemini
                genai.configure(api_key=st.session_state.api_key)
                
                # Create model
                # System instructions are set at model creation in Gemini
                model = genai.GenerativeModel(
                    'gemini-2.5-flash',
                    system_instruction=config["system"]
                )
                
                # Prepare history for Gemini
                # Gemini expects 'user' and 'model' roles
                gemini_history = []
                for msg in messages[:-1]: # Exclude the very last message which is the current prompt
                    role = "user" if msg["role"] == "user" else "model"
                    gemini_history.append({"role": role, "parts": [msg["content"]]})
                
                # Start chat
                chat = model.start_chat(history=gemini_history)
                
                # Stream response
                full_response = ""
                response_stream = chat.send_message(prompt, stream=True)
                
                for chunk in response_stream:
                    if chunk.text:
                        full_response += chunk.text
                        message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                messages.append({"role": "assistant", "content": full_response})
                st.session_state.message_count += 1
                
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                message_placeholder.error(error_msg)
                messages.append({"role": "assistant", "content": error_msg})
    
    # Clear conversation button
    if len(messages) > 0:
        if st.button("🗑️ Clear Conversation"):
            st.session_state.messages[dept] = []
            st.rerun()