# Adding New LLM Models

This application is designed to be highly configurable, allowing you to add new LLM models without modifying any code. All model configurations are managed through the `config/models_config.yaml` file.

## How to Add a New Provider

To add a new LLM provider supported by Agno (https://docs.agno.com/models), follow these steps:

1. Edit `config/models_config.yaml` and add a new provider section:

```yaml
your_provider_name:
  enabled: true
  api_key_env: "YOUR_PROVIDER_API_KEY"
  module: "agno.models.your_provider_module"
  class: "YourProviderClass"
  models:
    - name: "model-name"
      enabled: true
      display_name: "User-Friendly Name"
      parameters:
        temperature: 0.7
        # Add other parameters supported by the model class
```

2. Add the environment variable to your `.env` file:

```
YOUR_PROVIDER_API_KEY=your_api_key_here
```

3. Make sure you have the required Agno integration installed

## Provider Configuration Fields

| Field | Description |
|-------|-------------|
| `enabled` | Whether this provider is active |
| `api_key_env` | Environment variable name containing the API key |
| `module` | Python module path for the Agno integration |
| `class` | Class name to instantiate from the module |

## Model Configuration Fields

| Field | Description |
|-------|-------------|
| `name` | Model identifier used by the provider's API |
| `enabled` | Whether this model is active |
| `display_name` | Human-readable name shown in the UI |
| `parameters` | Model-specific parameters passed to the class constructor |

## UI Agent Configuration

You can also configure the Agno agent parameters in the config:

```yaml
agent:
  parameters:
    markdown: true
    # other agent parameters as needed
```
