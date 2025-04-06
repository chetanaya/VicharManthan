import asyncio
from typing import Any, Callable, Dict

# Import Agno components
from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.models.google import Gemini
from agno.models.openai import OpenAIChat

from utils.config_manager import ConfigManager


class LLMManager:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager

    def _get_agent_for_model(self, model: Dict[str, Any]) -> Agent:
        """Create an Agno Agent for the specified model."""
        provider = model["provider"]
        model_id = model["name"]
        temperature = model["temperature"]
        max_tokens = model["max_tokens"]
        api_key_env = model["api_key_env"]

        # Use os.environ to get API keys
        import os

        # Check if API key exists in environment
        api_key = os.getenv(api_key_env)
        if not api_key:
            raise ValueError(
                f"API key not found in environment variable '{api_key_env}'"
            )

        if provider == "openai":
            agent = Agent(
                model=OpenAIChat(
                    id=model_id,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    api_key=api_key,
                ),
                markdown=True,
            )
        elif provider == "anthropic":
            agent = Agent(
                model=Claude(
                    id=model_id,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    api_key=api_key,
                ),
                markdown=True,
            )
        elif provider == "google":
            agent = Agent(
                model=Gemini(
                    id=model_id,
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                    api_key=api_key,
                ),
                markdown=True,
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")

        return agent

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
