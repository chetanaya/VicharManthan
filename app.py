import streamlit as st

from utils.config_manager import ConfigManager
from utils.knowledge_manager import KnowledgeManager
from utils.llm_manager import LLMManager

# Set page configuration
st.set_page_config(
    page_title="Vichar Manthan",
    page_icon="🧠",
    layout="wide",
)

# Initialize session state variables
if "knowledge_manager" not in st.session_state:
    st.session_state.knowledge_manager = KnowledgeManager()

# Initialize config manager
if "config_manager" not in st.session_state:
    st.session_state.config_manager = ConfigManager()

# Initialize LLM manager with the config
if "llm_manager" not in st.session_state:
    st.session_state.llm_manager = LLMManager(st.session_state.config_manager)

# Initialize knowledge manager
if "knowledge_manager" not in st.session_state:
    st.session_state.knowledge_manager = KnowledgeManager(
        st.session_state.config_manager
    )


# Main application logic
def main():
    st.title("Vichar Manthan")
    st.write("Welcome to the Vichar Manthan application!")

    # Navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Chat", "Settings", "Knowledge Base"])

    if page == "Chat":
        st.switch_page("pages/01_chat.py")
    elif page == "Settings":
        st.switch_page("pages/02_settings.py")
    elif page == "Knowledge Base":
        st.switch_page("pages/03_knowledge_base.py")


if __name__ == "__main__":
    main()
