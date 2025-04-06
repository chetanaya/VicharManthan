import asyncio
import importlib
import os
from typing import Any, Callable, Dict

from agno.agent import Agent

from utils.config_manager import ConfigManager


class LLMManager:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager

    def _get_agent_for_model(self, model: Dict[str, Any]) -> Agent:
        """Create an Agno Agent for the specified model dynamically."""
        provider = model["provider"]
        model_id = model["name"]
        api_key_env = model["api_key_env"]

        # Get provider configuration
        provider_config = self.config_manager.get_provider_config(provider)
        if not provider_config:
            raise ValueError(f"Provider configuration not found: {provider}")

        # Get agent parameters from config
        agent_params = (
            self.config_manager.get_config().get("agent", {}).get("parameters", {})
        )

        # Get API key from environment
        api_key = os.getenv(api_key_env)
        if not api_key:
            raise ValueError(
                f"API key not found in environment variable '{api_key_env}'"
            )

        # Import the module and class dynamically
        try:
            module_name = provider_config.get("module")
            class_name = provider_config.get("class")

            if not module_name or not class_name:
                raise ValueError(
                    f"Missing module or class configuration for provider: {provider}"
                )

            # Import the module
            module = importlib.import_module(module_name)

            # Get the class
            model_class = getattr(module, class_name)

            # Prepare parameters
            model_params = model.get("parameters", {}).copy()

            # Add model id and API key
            model_params["id"] = model_id
            model_params["api_key"] = api_key

            # Create model instance
            model_instance = model_class(**model_params)

            # Create agent with the model
            agent = Agent(model=model_instance, **agent_params)

            return agent
        except (ImportError, AttributeError) as e:
            raise ValueError(f"Failed to load model class for {provider}: {str(e)}")

    async def stream_model(
        self, model: Dict[str, Any], prompt: str, callback: Callable[[str, str], None]
    ) -> None:
        """Stream responses from a specific model using Agno."""
        model_name = model["name"]

        try:
            agent = self._get_agent_for_model(model)
            run_response = agent.run(prompt, stream=True)

            for chunk in run_response:
                if chunk.content:
                    callback(model_name, chunk.content)
                    # Small sleep to allow UI updates
                    await asyncio.sleep(0.01)
        except Exception as e:
            callback(model_name, f"Error: {str(e)}")

    async def stream_all_models(
        self, prompt: str, callbacks: Dict[str, Callable[[str], None]]
    ) -> None:
        """Stream responses from all enabled models concurrently using Agno."""
        enabled_models = self.config_manager.get_enabled_models()
        tasks = []

        for model in enabled_models:
            model_name = model["name"]

            # Skip if we don't have a callback for this model
            if model_name not in callbacks:
                continue

            # Create a task for streaming from this model
            tasks.append(
                self.stream_model(
                    model, prompt, lambda name, text: callbacks[name](text)
                )
            )

        # Run all streaming tasks concurrently
        await asyncio.gather(*tasks)
