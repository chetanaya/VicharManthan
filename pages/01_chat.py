import os
import time
from typing import Any, Dict, List, Tuple

import streamlit as st


def main():  # noqa: C901
    st.subheader("Chat with Multiple LLMs")

    # Verify if config is loaded
    if "config_manager" not in st.session_state:
        st.error("Configuration not loaded. Please restart the application.")
        return

    # Check if any models are enabled
    enabled_models = st.session_state.config_manager.get_enabled_models()
    if not enabled_models:
        st.warning(
            "No models are enabled. Please go to the Settings page to enable models."
        )
        if st.button("Go to Settings"):
            st.switch_page("pages/settings.py")
        return

    # Check API keys and providers
    config = st.session_state.config_manager.get_config()
    missing_api_keys = []
    for provider, data in config["providers"].items():
        if data["enabled"] and not os.getenv(data["api_key_env"]):
            missing_api_keys.append(provider)

    if missing_api_keys:
        warning_message = f"API keys not configured for: {', '.join(provider.capitalize() for provider in missing_api_keys)}."
        st.warning(warning_message)

        # Add a convenient button to go to settings
        if st.button("Configure API Keys"):
            st.switch_page("pages/settings.py")

    # Initialize model-specific chat histories
    if "model_messages" not in st.session_state:
        st.session_state.model_messages = {
            model["name"]: [] for model in enabled_models
        }

    # Add any new models that weren't in the previous session
    for model in enabled_models:
        if model["name"] not in st.session_state.model_messages:
            st.session_state.model_messages[model["name"]] = []

    # Store models in session for rendering
    st.session_state.enabled_models = enabled_models

    # Set up layout
    models_per_row = config["ui"].get("models_per_row", 2)

    # Create a container for each model
    model_containers = {}

    # Create rows of model columns
    for i in range(0, len(enabled_models), models_per_row):
        row_models = enabled_models[i : i + models_per_row]
        cols = st.columns(models_per_row, border=True)

        for j, model in enumerate(row_models):
            model_name = model["name"]
            with cols[j]:
                st.markdown(f"##### {model['display_name']}")
                st.caption(f"Provider: {model['provider_name']}")

                # Show model parameters
                with st.expander("Model Parameters", expanded=False):
                    if "parameters" in model:
                        for param, value in model.get("parameters", {}).items():
                            st.text(f"{param}: {value}")
                    else:
                        st.text("No parameters configured")

                model_containers[model_name] = st.container()

    # Display message history for each model
    for model_name, container in model_containers.items():
        with container:
            for message in st.session_state.model_messages[model_name]:
                with st.chat_message(message["role"]):
                    # Handle markdown rendering based on configuration
                    use_markdown = (
                        config.get("agent", {})
                        .get("parameters", {})
                        .get("markdown", True)
                    )
                    if use_markdown:
                        st.markdown(message["content"])
                    else:
                        st.text(message["content"])

    # Handle new user input
    if prompt := st.chat_input("Message all models"):
        # Add user message to all model histories
        for model in enabled_models:
            model_name = model["name"]
            st.session_state.model_messages[model_name].append(
                {"role": "user", "content": prompt}
            )

            # Display the user message
            with model_containers[model_name], st.chat_message("user"):
                st.markdown(prompt)

        # Initialize placeholders for each model
        response_placeholders = {}
        status_indicators = {}
        for model in enabled_models:
            model_name = model["name"]
            with model_containers[model_name]:
                with st.chat_message("assistant"):
                    status_indicators[model_name] = st.empty()
                    response_placeholders[model_name] = st.empty()
                    # Show "Thinking..." indicator
                    status_indicators[model_name].info("Thinking...")

        # Prepare response storage
        if "current_responses" not in st.session_state:
            st.session_state.current_responses = {}

        for model_name in [m["name"] for m in enabled_models]:
            st.session_state.current_responses[model_name] = ""

        # Start streaming responses
        for model in enabled_models:
            model_name = model["name"]

            # Add empty assistant message to history (will update later)
            st.session_state.model_messages[model_name].append(
                {"role": "assistant", "content": ""}
            )

        # Show start time
        start_time = time.time()

        try:
            # Run streaming in main thread (avoiding threading issues)
            responses, timing_info = stream_responses_sync(
                enabled_models, prompt, response_placeholders, status_indicators
            )

            # Update final responses in chat history
            for model_name, response in responses.items():
                # Find the last assistant message and update it
                messages = st.session_state.model_messages[model_name]
                for i in range(len(messages) - 1, -1, -1):
                    if messages[i]["role"] == "assistant":
                        messages[i]["content"] = response
                        break

                # Display timing information
                if model_name in timing_info:
                    with model_containers[model_name]:
                        st.caption(f"Response time: {timing_info[model_name]:.2f}s")

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")


def stream_responses_sync(
    models: List[Dict[str, Any]],
    prompt: str,
    placeholders: Dict[str, Any],
    status_indicators: Dict[str, Any],
) -> Tuple[Dict[str, str], Dict[str, float]]:
    """
    Stream responses from all models, updating placeholders.

    Returns:
        Tuple containing:
        - Dict mapping model names to their final responses
        - Dict mapping model names to their response times
    """
    # Create generators for all models
    generators = {}
    final_responses = {}
    active_generators = set()
    timing_info = {}
    start_times = {}

    for model in models:
        model_name = model["name"]
        try:
            # Clear thinking indicator
            status_indicators[model_name].empty()

            # Record start time
            start_times[model_name] = time.time()

            agent = st.session_state.llm_manager._get_agent_for_model(model)
            generators[model_name] = agent.run(prompt, stream=True)
            active_generators.add(model_name)
            final_responses[model_name] = ""
        except Exception as e:
            error_message = f"Error: {str(e)}"
            final_responses[model_name] = error_message
            placeholders[model_name].error(error_message)
            timing_info[model_name] = time.time() - start_times.get(
                model_name, time.time()
            )

    # Stream responses until all generators are exhausted
    while active_generators:
        for model_name in list(active_generators):
            try:
                # Get next chunk
                generator = generators[model_name]
                chunk = next(generator, None)

                if chunk is None:
                    active_generators.remove(model_name)
                    # Record completion time
                    timing_info[model_name] = time.time() - start_times[model_name]
                    continue

                if chunk.content:
                    # Update response
                    final_responses[model_name] += chunk.content
                    # Update placeholder with cursor
                    placeholders[model_name].markdown(final_responses[model_name] + "▌")

            except StopIteration:
                active_generators.remove(model_name)
                # Record completion time
                timing_info[model_name] = time.time() - start_times[model_name]
            except Exception as e:
                error_msg = f"Error during streaming: {str(e)}"
                final_responses[model_name] += error_msg
                placeholders[model_name].error(error_msg)
                active_generators.remove(model_name)
                # Record completion time
                timing_info[model_name] = time.time() - start_times[model_name]

        # Small delay to avoid UI freezing
        time.sleep(0.05)

    # Final update to remove cursor
    for model_name, response in final_responses.items():
        placeholders[model_name].markdown(response)

    return final_responses, timing_info


if __name__ == "__main__":
    main()
