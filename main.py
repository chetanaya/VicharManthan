import os

import streamlit as st

from utils.config_manager import ConfigManager
from utils.llm_manager import LLMManager
from utils.pgvector_utils import check_pgvector_status


def initialize_session_state():
    """Initialize the session state variables."""
    if "chat_histories" not in st.session_state:
        st.session_state.chat_histories = {}

    if "config_manager" not in st.session_state:
        st.session_state.config_manager = ConfigManager()

    if "llm_manager" not in st.session_state:
        st.session_state.llm_manager = LLMManager(st.session_state.config_manager)

    # Initialize pgvector status
    if "pgvector_status" not in st.session_state:
        config = st.session_state.config_manager.get_config()
        pgvector_config = config.get("pgvector", {})
        st.session_state.pgvector_status = check_pgvector_status(pgvector_config)


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

        # Display pgvector status
        st.header("pgVector Status")
        pgvector_status = st.session_state.pgvector_status

        if pgvector_status["docker_running"]:
            st.success("Docker container: ✓ Running")
        else:
            st.error("Docker container: ⚠ Not running")

        if pgvector_status["db_connectable"]:
            st.success("Database connection: ✓ Connected")
        else:
            st.error("Database connection: ⚠ Not connected")

        if pgvector_status["extension_enabled"]:
            st.success("pgVector extension: ✓ Enabled")
        else:
            st.error("pgVector extension: ⚠ Not enabled")

        if not all(pgvector_status.values()):
            st.info("Configure pgVector in the Settings page")

    # Display README.md content on the main page
    readme_content = load_readme()
    st.markdown(readme_content)


if __name__ == "__main__":
    main()
