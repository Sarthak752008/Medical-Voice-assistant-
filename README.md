# Medical Voice AI Assistant

A beginner-friendly Streamlit app that records a spoken health question, transcribes it with OpenAI, generates general medical information, and reads the answer aloud.

> This app provides general information only. It is not a diagnosis and does not replace a qualified healthcare professional. For emergencies, contact local emergency services.

## Features

- Record questions with the browser microphone
- Speech-to-text with OpenAI
- Medical-assistant response with an OpenAI model
- Text-to-speech response with OpenAI
- Local `.env` support and Streamlit Community Cloud Secrets support
- Clear error messages without exposing API keys

## Run locally

1. Install Python 3.10 or newer.
2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   ```

   Windows PowerShell:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a file named `.env` in the project root:

   ```env
   OPENAI_API_KEY=your_api_key_here

   # Optional provider settings reserved for future integrations.
   GEMINI_API_KEY=
   GEMINI_MODEL=gemini-1.5-pro
   GROQ_API_KEY=
   GROQ_MODEL=qwen/qwen3.8-27b
   ```

   You can copy `.env.example` as a starting point. The current app uses OpenAI
   for the complete voice pipeline; Gemini and Groq settings are not used yet.

5. Start the app:

   ```bash
   streamlit run app.py
   ```

Your browser should open the local Streamlit app. Allow microphone access when prompted.

## Deploy to Streamlit Community Cloud

1. Push this project to GitHub.
2. Create a new app at [share.streamlit.io](https://share.streamlit.io/).
3. Select the repository, branch, and `app.py` as the main file.
4. In the app settings, open **Secrets** and add:

   ```toml
   OPENAI_API_KEY = "your_api_key_here"
   ```

5. Deploy the app.

Do not commit `.env` or `.streamlit/secrets.toml`. The `.gitignore` file excludes both.
Never paste real API keys into GitHub, documentation, or source files. Any keys
shared in chat or accidentally exposed should be revoked and regenerated.

## Cost and privacy

OpenAI API usage may incur charges. Audio and text are sent to OpenAI to provide the requested transcription, response, and speech generation. Avoid recording highly sensitive personal information.
