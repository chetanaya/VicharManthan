# Vichar Manthan (Multi-LLM Interface)
Vichar meaning "thought" and Manthan meaning "churning" – symbolizing the process of extracting wisdom from multiple models. A Streamlit application that allows users to interact with multiple LLM models simultaneously using Agno, comparing responses side by side.

## Features
- Chat with multiple LLM models in parallel
- Stream responses in real-time
- Configure which models are active
- Secure API key management via environment variables
- Customizable layout and appearance

## Supported Providers
- OpenAI
- Anthropic
- Cohere
- DeepSeek
- Fireworks
- Google Gemini
- Groq
- Hugging Face
- Mistral
- NVIDIA
- Ollama
- OpenRouter
- Perplexity
- Sambanova
- Together
- LiteLLM
- Check the Complete List here: https://docs.agno.com/models/introduction

## Setup and Installation
1. Clone the repository:
   ```
   git clone https://github.com/chetanaya/VicharManthan.git
   cd VicharManthan
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your environment variables:
   ```
   cp .env.example .env
   ```

   Edit the `.env` file and add your API keys for the services you want to use.

4. Run the application:
   ```
   streamlit run main.py
   ```

5. Open your browser and navigate to the URL shown in the terminal (typically http://localhost:8501)

## Configuration
The application uses a YAML configuration file located at `config/models_config.yaml`. You can modify this file directly or use the Settings page in the application. Follow Agno Docs for more details: https://docs.agno.com/models

### API Keys
This application securely stores API keys in the `.env` file. In the configuration, you only need to specify which environment variable contains each API key.

You'll need to obtain API keys for the LLM providers you want to use:
- OpenAI: https://platform.openai.com/account/api-keys
- Anthropic: https://console.anthropic.com/settings/keys
- Google: https://aistudio.google.com/app/apikey
- and More...

## Usage
1. Navigate to the Chat page
2. Type your message in the input field at the bottom
3. Press Enter to send the message to all enabled models
4. View the responses side by side in real-time

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
