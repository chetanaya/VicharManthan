import os

import streamlit as st

from utils.config_manager import ConfigManager
from utils.llm_manager import LLMManager


def initialize_session_state():
    """Initialize the session state variables."""
    if "chat_histories" not in st.session_state:
        st.session_state.chat_histories = {}

    if "config_manager" not in st.session_state:
        st.session_state.config_manager = ConfigManager()

    if "llm_manager" not in st.session_state:
        st.session_state.llm_manager = LLMManager(st.session_state.config_manager)


def main():
    """Main function for the Streamlit app."""
    st.set_page_config(
        page_title="Vichar Manthan",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Initialize session state
    initialize_session_state()

    # Set theme based on config
    config = st.session_state.config_manager.get_config()
    theme = config["ui"].get("theme", "light")

    # Display title
    st.title("Vichar Manthan (Multi-LLM Interface)")
    st.markdown(
        'Vichar meaning "thought" and Manthan meaning "churning" – symbolizing the process of extracting wisdom from multiple models. Interact with multiple LLM models simultaneously.'
    )

    # Sidebar with information
    with st.sidebar:
        # Display API key status
        st.header("API Key Status")
        for provider, data in config["providers"].items():
            if data["enabled"]:
                api_key = os.getenv(data["api_key_env"], "")
                if api_key:
                    st.success(f"{provider.capitalize()}: ✓ Configured")
                else:
                    st.error(f"{provider.capitalize()}: ⚠ Not configured")


if __name__ == "__main__":
    main()
