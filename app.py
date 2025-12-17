import streamlit as st
import anthropic
import os
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Department AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# Department configurations
DEPARTMENTS = {
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
    "Engineering": {
        "icon": "⚙️",
        "system": "You are a technical AI assistant. Help with code review, debugging, architecture decisions, and technical documentation. Be precise and technical.",
        "examples": [
            "Review my Python code",
            "Debug this error message",
            "Design a scalable system architecture"
        ]
    },
    "Customer Support": {
        "icon": "💬",
        "system": "You are a customer support AI assistant. Help with response templates, issue resolution, and customer communication. Be empathetic and solution-focused.",
        "examples": [
            "Draft a response to an angry customer",
            "Handle a refund request professionally",
            "Create FAQ answers"
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
    st.session_state.selected_dept = "Marketing"

if "user_email" not in st.session_state:
    st.session_state.user_email = ""

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
        email = st.text_input("Email", placeholder="you@company.com")
        if st.button("Access AI", use_container_width=True):
            if email:
                st.session_state.user_email = email
                st.session_state.logged_in = True
                st.rerun()
    else:
        st.success(f"👤 {st.session_state.user_email}")
        
        st.divider()
        
        # Department selector
        st.subheader("Departments")
        for dept, config in DEPARTMENTS.items():
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
        
        st.divider()
        
        # Logout
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_email = ""
            st.rerun()
    
    st.divider()
    
    # API Key configuration
    with st.expander("⚙️ API Configuration"):
        api_key = st.text_input(
            "Anthropic API Key",
            type="password",
            value=st.session_state.api_key,
            help="Get free key at console.anthropic.com"
        )
        if st.button("Save API Key"):
            st.session_state.api_key = api_key
            st.success("API Key saved!")
        
        st.caption("💡 Get free API key: [console.anthropic.com](https://console.anthropic.com)")

# Main area
if not st.session_state.logged_in:
    st.title("🤖 Welcome to AI Assistant Hub")
    st.markdown("""
    ### Get Started
    1. Login with your email in the sidebar
    2. Add your API key (get free at console.anthropic.com)
    3. Select your department
    4. Start chatting!
    
    ### Features
    - 🎯 Department-specific AI assistants
    - 💬 Context-aware conversations
    - 📊 Usage tracking
    - 🔒 Simple authentication
    """)
else:
    # Get current department config
    dept = st.session_state.selected_dept
    config = DEPARTMENTS[dept]
    
    # Header
    st.title(f"{config['icon']} {dept} AI Assistant")
    st.caption(f"Logged in as: {st.session_state.user_email}")
    
    # Check for API key
    if not st.session_state.api_key:
        st.warning("⚠️ Please add your API key in the sidebar to start chatting")
        st.info("Get a free API key at: https://console.anthropic.com")
        st.stop()
    
    # Display chat messages
    messages = st.session_state.messages[dept]
    
    if len(messages) == 0:
        st.info(f"👋 Welcome! I'm your {dept} AI assistant. Try these examples:")
        cols = st.columns(len(config['examples']))
        for i, example in enumerate(config['examples']):
            with cols[i]:
                if st.button(example, use_container_width=True):
                    # Add example as user message and process
                    messages.append({"role": "user", "content": example})
                    st.rerun()
    
    # Display conversation
    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input(f"Ask {dept} AI anything..."):
        # Add user message
        messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate AI response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("▌")
            
            try:
                # Call Anthropic API
                client = anthropic.Anthropic(api_key=st.session_state.api_key)
                
                # Prepare messages for API
                api_messages = [
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in messages
                ]
                
                # Stream response
                full_response = ""
                with client.messages.stream(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1024,
                    system=config["system"],
                    messages=api_messages,
                ) as stream:
                    for text in stream.text_stream:
                        full_response += text
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