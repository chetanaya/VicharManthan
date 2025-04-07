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

            # Add or update API key value
            st.divider()
            api_key_value = st.text_input(
                f"API Key Value for {provider.capitalize()}",
                value="",
                type="password",
                key=f"api_key_value_{provider}",
                placeholder="Enter your API key to add/update it",
            )

            if st.button("Save API Key", key=f"save_key_{provider}"):
                if api_key_value:
                    if st.session_state.config_manager.save_api_key(
                        current_key_env, api_key_value
                    ):
                        st.success(
                            f"API key for {provider.capitalize()} saved to .env file!"
                        )
                        st.rerun()
                    else:
                        st.error("Failed to save API key. Check file permissions.")
                else:
                    st.warning("Please enter an API key value")


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

            # Add new model button
            st.divider()
            if st.button("Add New Model", key=f"add_model_{provider}"):
                st.session_state[f"adding_model_{provider}"] = True

            # Form to add a new model
            if st.session_state.get(f"adding_model_{provider}", False):
                with st.form(key=f"new_model_form_{provider}"):
                    st.subheader(f"Add New Model for {provider.capitalize()}")

                    new_model_name = st.text_input(
                        "Model ID/Name", key=f"new_model_name_{provider}"
                    )
                    new_model_display_name = st.text_input(
                        "Display Name", key=f"new_model_display_name_{provider}"
                    )
                    new_model_temperature = st.slider(
                        "Temperature",
                        min_value=0.0,
                        max_value=1.0,
                        value=0.7,
                        step=0.1,
                        key=f"new_model_temp_{provider}",
                    )
                    new_model_max_tokens = st.number_input(
                        "Max Tokens",
                        min_value=100,
                        max_value=8000,
                        value=1024,
                        step=100,
                        key=f"new_model_tokens_{provider}",
                    )

                    col1, col2 = st.columns(2)
                    with col1:
                        submit_button = st.form_submit_button("Add Model")
                    with col2:
                        cancel_button = st.form_submit_button("Cancel")

                    if submit_button:
                        if new_model_name and new_model_display_name:
                            st.session_state.config_manager.add_model(
                                provider,
                                new_model_name,
                                new_model_display_name,
                                new_model_temperature,
                                new_model_max_tokens,
                            )
                            st.success(f"Added new model: {new_model_display_name}")
                            st.session_state[f"adding_model_{provider}"] = False
                            st.rerun()
                        else:
                            st.error("Model ID and Display Name are required")

                    if cancel_button:
                        st.session_state[f"adding_model_{provider}"] = False
                        st.rerun()


def provider_management():
    """Add new providers to the configuration."""
    st.header("Provider Management")

    with st.expander("Add New Provider"):
        with st.form(key="new_provider_form"):
            st.subheader("Add New Provider")

            provider_id = st.text_input(
                "Provider ID (lowercase, no spaces)",
                placeholder="e.g. openai, anthropic, mistral",
            )
            provider_class = st.text_input(
                "Provider Class Name", placeholder="e.g. OpenAIChat, Claude, Mistral"
            )
            provider_module = st.text_input(
                "Provider Module Path", placeholder="e.g. agno.models.openai"
            )
            api_key_env = st.text_input(
                "API Key Environment Variable", placeholder="e.g. OPENAI_API_KEY"
            )

            # Optional first model
            st.subheader("Initial Model (Optional)")
            add_model = st.checkbox("Add initial model", value=True)

            if add_model:
                model_name = st.text_input(
                    "Model ID/Name", placeholder="e.g. gpt-4o, claude-3-opus"
                )
                model_display_name = st.text_input(
                    "Display Name", placeholder="e.g. GPT-4o, Claude 3 Opus"
                )

            submit_button = st.form_submit_button("Add Provider")

            if submit_button:
                if provider_id and provider_class and provider_module and api_key_env:
                    if add_model and (not model_name or not model_display_name):
                        st.error(
                            "Model ID and Display Name are required if adding an initial model"
                        )
                    else:
                        result = st.session_state.config_manager.add_provider(
                            provider_id,
                            provider_class,
                            provider_module,
                            api_key_env,
                            model_name if add_model else None,
                            model_display_name if add_model else None,
                        )
                        if result:
                            st.success(f"Added new provider: {provider_id}")
                            st.rerun()
                else:
                    st.error("All provider fields are required")


def ui_settings():
    """Settings for the UI."""
    st.header("UI Settings")

    config = st.session_state.config_manager.get_config()
    ui_config = config["ui"]

    models_per_row = st.slider(
        "Models per row",
        min_value=1,
        max_value=4,
        value=ui_config.get("models_per_row", 2),
        step=1,
    )

    if st.button("Update UI Settings"):
        st.session_state.config_manager.update_ui_settings(models_per_row)
        st.success("UI settings updated!")


def main():
    st.title("Settings")

    # Verify if config is loaded
    if "config_manager" not in st.session_state:
        st.error("Configuration not loaded. Please restart the application.")
        return

    # Initialize session state for adding models
    for provider in st.session_state.config_manager.get_config()["providers"]:
        if f"adding_model_{provider}" not in st.session_state:
            st.session_state[f"adding_model_{provider}"] = False

    # Sections
    api_key_settings()
    st.divider()
    model_settings()
    st.divider()
    provider_management()
    st.divider()
    ui_settings()

    # Reset chat history button
    st.divider()
    if st.button("Clear All Chat History", type="primary"):
        st.session_state.chat_histories = {}
        st.success("Chat history cleared!")


if __name__ == "__main__":
    main()
