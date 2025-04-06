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
        page_title="Multi-LLM Interface",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Initialize session state
    initialize_session_state()

    # Set theme based on config
    config = st.session_state.config_manager.get_config()

    # Display title
    st.title("Multi-LLM Interface")
    st.markdown("Interact with multiple LLM models simultaneously")

    # Sidebar with information
    with st.sidebar:
        st.header("About")
        st.markdown(
            """
        This application allows you to:
        - Chat with multiple LLM models simultaneously
        - Compare responses side by side
        - Configure which models are active
        - Update API keys and model parameters
        """
        )

        # Display API key status
        st.header("API Key Status")
        for provider, data in config["providers"].items():
            if data["enabled"]:
                api_key = st.session_state.config_manager.get_env_var(
                    data["api_key_env"]
                )
                if api_key:
                    st.success(f"{provider.capitalize()}: ✓ Configured")
                else:
                    st.error(f"{provider.capitalize()}: ⚠ Not configured")


if __name__ == "__main__":
    main()
