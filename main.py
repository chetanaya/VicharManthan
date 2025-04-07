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


def load_readme():
    """Load and display the README.md file."""
    try:
        with open("README.md", "r") as file:
            readme_content = file.read()
        return readme_content
    except FileNotFoundError:
        return "README.md file not found. Please make sure it exists in the project root directory."


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

    # Get config
    config = st.session_state.config_manager.get_config()

    # Sidebar with information and menu
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

    # Display README.md content on the main page
    readme_content = load_readme()
    st.markdown(readme_content)


if __name__ == "__main__":
    main()
