
import streamlit as st
import google.generativeai as genai
import os
from datetime import datetime

# Page config
st.set_page_config(
    page_title="AIBold | Internal AI OS",
    page_icon="⚡",
    layout="wide"
)

# Custom Styling for AIBold Branding
st.markdown("""
<style>
    /* Main background and font */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        color: #e0e0e0;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: rgba(15, 12, 41, 0.8) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 700 !important;
        color: #ffffff !important;
        letter-spacing: -0.5px;
    }
    
    /* Custom primary color for buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        border-color: #6c5ce7;
        color: #6c5ce7;
        transform: translateY(-1px);
    }
    
    /* Chat message aesthetic */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 10px;
    }
    
    /* Sidebar Titles */
    .sidebar-title {
        font-size: 1.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #a29bfe, #6c5ce7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    
    /* Success/Info boxes */
    .stAlert {
        background-color: rgba(108, 92, 231, 0.1);
        border: 1px solid rgba(108, 92, 231, 0.2);
        color: #a29bfe;
    }
</style>
""", unsafe_allow_html=True)

# User credentials and permissions
USERS = {
    "youssef@aibold": {
        "password": "aibold.youssef",
        "role": "admin",
        "departments": "all"  # Admin has access to all departments
    },
    "ragwa@aibold": {
        "password": "aibold.ragwa",
        "role": "admin",
        "departments": "all"
    },
    "saeed@aibold": {
        "password": "aibold.saeed",
        "role": "user",
        "departments": ["Marketing", "Sales", "General Research"]
    },
    "osama@aibold": {
        "password": "aibold.osama",
        "role": "user",
        "departments": ["Marketing", "Sales", "General Research"]
    },
    "zeinab@aibold": {
        "password": "aibold.zeinab",
        "role": "user",
        "departments": ["Marketing", "Sales", "General Research"]
    },
    "gamal@aibold": {
        "password": "aibold.gamal",
        "role": "user",
        "departments": ["Content Creation & Design", "General Research"]
    },
    "roba@aibold": {
        "password": "aibold.roba",
        "role": "user",
        "departments": ["General Research"]
    },
    "yara@aibold": {
        "password": "aibold.yara",
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
    st.markdown('<p class="sidebar-title">AIBold Core ⚡</p>', unsafe_allow_html=True)
    st.caption("AI as a Service | Internal OS v1.2")
    
    # Login section
    if not st.session_state.logged_in:
        st.subheader("Login")
        username = st.text_input("Username", placeholder="name@aibold")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        api_key = st.text_input("Gemini API Key", type="password", placeholder="Enter your API key")
        st.caption("💡 [Get free API key](https://aistudio.google.com/app/apikey)")
        
        if st.button("Login", use_container_width=True):
            if username and password and api_key:
                # Validate credentials
                if username in USERS and USERS[username]["password"] == password:
                    st.session_state.username = username
                    st.session_state.api_key = api_key
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
                st.warning("⚠️ Please enter username, password, and API key")
    else:
        # Display user info
        user_role = USERS[st.session_state.username]["role"]
        role_badge = "👑 Admin" if user_role == "admin" else "👤 User"
        st.success(f"{role_badge}: {st.session_state.username}")
        
        st.divider()
        
        # Department selector - only show accessible departments
        st.subheader("Intelligence Nodes")
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
        st.subheader("🌐 Network Stats")
        st.metric("Neural Requests", st.session_state.message_count)
        st.caption(f"Access: {len(accessible_depts)} department{'s' if len(accessible_depts) > 1 else ''}")
        
        st.divider()
        
        # Logout
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.api_key = ""
            st.session_state.user_permissions = []
            st.session_state.selected_dept = None
            st.rerun()
    
    st.divider()
    


# Main area
if not st.session_state.logged_in:
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="font-size: 3.5rem; margin-bottom: 0px;">⚡ AIBold</h1>
        <p style="font-size: 1.2rem; color: #a29bfe;">Powering the future of AI as a Service</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        ### 🌐 The Internal Hub
        Welcome to the central intelligence hub for AIBold employees. Log in to access specialized neural nodes tailored for your department.
        
        ### 🛠️ Key Capabilities
        - **Proprietary Knowledge Nodes**: Domain-specific AI models.
        - **Cross-Dept Collaboration**: Seamless switching between roles.
        - **Secure Access**: Encrypted session management.
        """)
        
    with col2:
        st.markdown("""
        ### 🚀 Quick Start
        1. Initialize your session via the **Sidebar**.
        2. Input credentials & your valid **Gemini API Key**.
        3. Select your specialized **Department Node**.
        4. Engage with the AIBold Intelligence.
        
        > "Boldly going where no AI has gone before."
        """)
else:
    # Get current department config
    dept = st.session_state.selected_dept
    config = DEPARTMENTS[dept]
    
    # Header
    st.markdown(f"### {config['icon']} AIBold | {dept} Intelligence Node")
    st.caption(f"Authenticated as: {st.session_state.username} • Node active")
    

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
            
    st.divider()
    st.caption("⚡ AIBold Core | Proprietary Intelligence Node • High-Priority Connection")
    
    # Chat input
    prompt = st.chat_input(f"Engage {dept} Intelligence Node...")
    
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