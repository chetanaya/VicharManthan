import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import streamlit as st
import yaml
from dotenv import find_dotenv, load_dotenv, set_key

# Load environment variables
load_dotenv()


class ConfigManager:
    def __init__(self, config_path: str = "config/models_config.yaml"):
        self.config_path = config_path
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, "r") as file:
                self.config = yaml.safe_load(file)
        except Exception as e:
            st.error(f"Error loading configuration: {str(e)}")
            self.config = self._get_default_config()

    def _save_config(self) -> None:
        """Save configuration to YAML file."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, "w") as file:
                yaml.dump(self.config, file, default_flow_style=False)
        except Exception as e:
            st.error(f"Error saving configuration: {str(e)}")

    def get_config(self) -> Dict[str, Any]:
        """Get the current configuration."""
        return self.config

    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Update the configuration and save it."""
        self.config = new_config
        self._save_config()

    def get_provider_config(self, provider_id: str) -> Dict[str, Any]:
        """Get configuration for a specific provider."""
        if provider_id in self.config["providers"]:
            return self.config["providers"][provider_id]
        return None

    def get_enabled_models(self) -> List[Dict[str, Any]]:
        """Get a list of all enabled models with their provider details."""
        enabled_models = []

        for provider_id, provider_data in self.config["providers"].items():
            if not provider_data["enabled"]:
                continue

            for model in provider_data["models"]:
                if model["enabled"]:
                    model_info = {
                        "provider": provider_id,
                        "provider_name": provider_id.capitalize(),
                        "api_key_env": provider_data["api_key_env"],
                        **model,
                    }
                    enabled_models.append(model_info)

        return enabled_models

    def update_api_key_env(self, provider: str, api_key_env: str) -> None:
        """Update API key environment variable name for a specific provider."""
        if provider in self.config["providers"]:
            self.config["providers"][provider]["api_key_env"] = api_key_env
            self._save_config()

    def toggle_model(self, provider: str, model_name: str, enabled: bool) -> None:
        """Toggle a model's enabled status."""
        if provider in self.config["providers"]:
            for model in self.config["providers"][provider]["models"]:
                if model["name"] == model_name:
                    model["enabled"] = enabled
                    self._save_config()
                    break

    def toggle_provider(self, provider: str, enabled: bool) -> None:
        """Toggle a provider's enabled status."""
        if provider in self.config["providers"]:
            self.config["providers"][provider]["enabled"] = enabled
            self._save_config()

    def update_ui_settings(self, models_per_row: int, theme: str) -> None:
        """Update UI settings."""
        self.config["ui"]["models_per_row"] = models_per_row
        self.config["ui"]["theme"] = theme
        self._save_config()

    def update_model_parameters(
        self, provider: str, model_name: str, temperature: float, max_tokens: int
    ) -> None:
        """Update model parameters."""
        if provider in self.config["providers"]:
            for model in self.config["providers"][provider]["models"]:
                if model["name"] == model_name:
                    # Initialize parameters dict if it doesn't exist
                    if "parameters" not in model:
                        model["parameters"] = {}

                    # Update temperature
                    model["parameters"]["temperature"] = temperature

                    # Update max tokens (using the right parameter name)
                    if provider == "google":
                        model["parameters"]["max_output_tokens"] = max_tokens
                    else:
                        model["parameters"]["max_tokens"] = max_tokens

                    self._save_config()
                    break

    def add_model(
        self,
        provider: str,
        model_name: str,
        display_name: str,
        temperature: float,
        max_tokens: int,
    ) -> bool:
        """
        Add a new model to an existing provider.

        Args:
            provider: Provider ID
            model_name: Model ID/name
            display_name: Display name for the model
            temperature: Default temperature value
            max_tokens: Default max tokens value

        Returns:
            bool: Success or failure
        """
        if provider not in self.config["providers"]:
            return False

        # Check if model already exists
        for model in self.config["providers"][provider]["models"]:
            if model["name"] == model_name:
                return False

        # Create new model configuration
        new_model = {
            "name": model_name,
            "display_name": display_name,
            "enabled": True,
            "parameters": {},
        }

        # Add the right parameter names based on provider
        if provider == "google":
            new_model["parameters"]["max_output_tokens"] = max_tokens
        else:
            new_model["parameters"]["max_tokens"] = max_tokens

        new_model["parameters"]["temperature"] = temperature

        # Add the model to the provider
        self.config["providers"][provider]["models"].append(new_model)
        self._save_config()

        return True

    def add_provider(
        self,
        provider_id: str,
        provider_class: str,
        module_path: str,
        api_key_env: str,
        initial_model_name: Optional[str] = None,
        initial_model_display_name: Optional[str] = None,
    ) -> bool:
        """
        Add a new provider to the configuration.

        Args:
            provider_id: Unique ID for the provider (lowercase)
            provider_class: Class name for the provider
            module_path: Python module path
            api_key_env: Environment variable name for API key
            initial_model_name: Optional name for initial model
            initial_model_display_name: Optional display name for initial model

        Returns:
            bool: Success or failure
        """
        # Check if provider already exists
        if provider_id in self.config["providers"]:
            return False

        # Create provider configuration
        new_provider = {
            "api_key_env": api_key_env,
            "class": provider_class,
            "enabled": False,  # Disabled by default until API key is verified
            "module": module_path,
            "models": [],
        }

        # Add initial model if provided
        if initial_model_name and initial_model_display_name:
            new_provider["models"].append(
                {
                    "display_name": initial_model_display_name,
                    "enabled": True,
                    "name": initial_model_name,
                    "parameters": {"max_tokens": 1024, "temperature": 0.7},
                }
            )

        # Add the provider to the configuration
        self.config["providers"][provider_id] = new_provider
        self._save_config()

        return True

    def save_api_key(self, env_var_name: str, api_key_value: str) -> bool:
        """
        Save API key to .env file

        Args:
            env_var_name: Environment variable name
            api_key_value: API key value

        Returns:
            bool: Success or failure
        """
        try:
            # Find .env file in project root or create one if it doesn't exist
            dotenv_path = find_dotenv()
            if not dotenv_path:
                dotenv_path = os.path.join(
                    os.path.dirname(self.config_path), "..", ".env"
                )
                Path(dotenv_path).touch(exist_ok=True)

            # Update or add the environment variable
            set_key(dotenv_path, env_var_name, api_key_value)

            # Reload environment variables
            load_dotenv(dotenv_path, override=True)

            return True
        except Exception as e:
            st.error(f"Error saving API key: {str(e)}")
            return False

    def _get_default_config(self) -> Dict[str, Any]:
        """Return a default configuration if the config file doesn't exist."""
        return {
            "providers": {
                "openai": {
                    "enabled": True,
                    "api_key_env": "OPENAI_API_KEY",
                    "class": "OpenAIChat",
                    "module": "agno.models.openai",
                    "models": [
                        {
                            "name": "gpt-4o",
                            "display_name": "GPT-4o",
                            "enabled": True,
                            "parameters": {
                                "temperature": 0.7,
                                "max_tokens": 1000,
                            },
                        }
                    ],
                }
            },
            "ui": {"models_per_row": 2, "theme": "light", "max_chat_history": 10},
            "agent": {"parameters": {"markdown": False}},
        }
