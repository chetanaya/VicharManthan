import os

import streamlit as st


def api_key_settings():
    """Settings for API keys environment variables."""
    st.header("API Key Settings")

    config = st.session_state.config_manager.get_config()

    # Display instructions
    st.info(
        """
    API keys should be stored in a .env file at the root of your project.
    Here you can specify which environment variable name to use for each provider.
    """
    )

    for provider, data in config["providers"].items():
        with st.expander(f"{provider.capitalize()} API Key"):
            current_key_env = data["api_key_env"]
            actual_key_value = os.getenv(current_key_env, "")

            # Show status
            if actual_key_value:
                st.success(
                    f"✓ Found API key in environment variable '{current_key_env}'"
                )
            else:
                st.error(
                    f"✗ No API key found in environment variable '{current_key_env}'"
                )

            # Edit environment variable name
            new_key_env = st.text_input(
                f"Environment variable name for {provider.capitalize()} API key",
                value=current_key_env,
                key=f"api_key_env_{provider}",
            )

            if st.button("Update", key=f"update_env_{provider}"):
                if new_key_env and new_key_env != current_key_env:
                    st.session_state.config_manager.update_api_key_env(
                        provider, new_key_env
                    )
                    st.success(
                        f"Updated environment variable for {provider.capitalize()} API key!"
                    )
                    st.rerun()


def model_settings():
    """Settings for models and providers."""
    st.header("Models Configuration")

    config = st.session_state.config_manager.get_config()

    for provider, data in config["providers"].items():
        with st.expander(f"{provider.capitalize()} Models"):
            # Provider toggle
            provider_enabled = st.checkbox(
                f"Enable {provider.capitalize()}",
                value=data["enabled"],
                key=f"provider_{provider}",
            )

            if provider_enabled != data["enabled"]:
                st.session_state.config_manager.toggle_provider(
                    provider, provider_enabled
                )
                st.rerun()

            if not provider_enabled:
                continue

            # Model toggles and settings
            for i, model in enumerate(data["models"]):
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

                with col1:
                    model_enabled = st.checkbox(
                        model["display_name"],
                        value=model["enabled"],
                        key=f"model_{provider}_{model['name']}",
                    )

                    if model_enabled != model["enabled"]:
                        st.session_state.config_manager.toggle_model(
                            provider, model["name"], model_enabled
                        )

                if model_enabled:
                    with col2:
                        temperature = st.slider(
                            "Temperature",
                            min_value=0.0,
                            max_value=1.0,
                            value=model.get("parameters", {}).get("temperature", 0.7),
                            step=0.1,
                            key=f"temp_{provider}_{model['name']}",
                        )

                    with col3:
                        max_tokens = st.number_input(
                            "Max Tokens",
                            min_value=100,
                            max_value=8000,
                            value=model.get("parameters", {}).get(
                                "max_tokens",
                                model.get("parameters", {}).get(
                                    "max_output_tokens", 1000
                                ),
                            ),
                            step=100,
                            key=f"tokens_{provider}_{model['name']}",
                        )

                    with col4:
                        if st.button(
                            "Update", key=f"update_{provider}_{model['name']}"
                        ):
                            st.session_state.config_manager.update_model_parameters(
                                provider, model["name"], temperature, max_tokens
                            )
                            st.success(f"{model['display_name']} settings updated!")


def ui_settings():
    """Settings for the UI."""
    st.header("UI Settings")

    config = st.session_state.config_manager.get_config()
    ui_config = config["ui"]

    col1, col2 = st.columns(2)

    with col1:
        models_per_row = st.slider(
            "Models per row",
            min_value=1,
            max_value=4,
            value=ui_config.get("models_per_row", 2),
            step=1,
        )

    with col2:
        theme = st.selectbox(
            "Theme",
            options=["light", "dark"],
            index=0 if ui_config.get("theme", "light") == "light" else 1,
        )

    if st.button("Update UI Settings"):
        st.session_state.config_manager.update_ui_settings(models_per_row, theme)
        st.success("UI settings updated!")


def main():
    st.title("Settings")

    # Verify if config is loaded
    if "config_manager" not in st.session_state:
        st.error("Configuration not loaded. Please restart the application.")
        return

    # Sections
    api_key_settings()
    st.divider()
    model_settings()
    st.divider()
    ui_settings()

    # Reset chat history button
    st.divider()
    if st.button("Clear All Chat History", type="primary"):
        st.session_state.chat_histories = {}
        st.success("Chat history cleared!")


if __name__ == "__main__":
    main()
