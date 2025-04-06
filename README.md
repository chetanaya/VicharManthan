# VicharManthan
Vichar meaning "thought" and Manthan meaning "churning" – symbolizing the process of extracting wisdom from multiple models. A Streamlit application that allows users to interact with multiple LLM models simultaneously using Agno, comparing responses side by side.

## Features

- Chat with multiple LLM models in parallel
- Stream responses in real-time
- Configure which models are active
- Secure API key management via environment variables
- Customizable layout and appearance

## Supported Providers

- OpenAI
- OpenAI Like
- Anthropic
- AWS Bedrock
- Claude via AWS Bedrock
- Azure AI Foundry
- OpenAI via Azure
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
- and Many More...

## Usage

1. Navigate to the Chat page
2. Type your message in the input field at the bottom
3. Press Enter to send the message to all enabled models
4. View the responses side by side in real-time

## Project Structure

```
multi_llm_interface/
├── .env.example        # Template for environment variables
├── config/
│   └── models_config.yaml  # Configuration for models and UI
├── utils/
│   ├── __init__.py
│   ├── config_manager.py   # Manages configuration loading/saving
│   └── llm_manager.py      # Handles LLM integration via Agno
├── pages/
│   ├── __init__.py
│   ├── 01_chat.py          # Main chat interface
│   └── 02_settings.py      # Settings and configuration UI
├── main.py                 # Application entry point
├── requirements.txt
└── README.md
```
