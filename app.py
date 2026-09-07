import io
import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError


load_dotenv()

st.set_page_config(
    page_title="Medical Voice AI Assistant",
    page_icon="🩺",
    layout="centered",
)


SYSTEM_PROMPT = """You are a careful medical information assistant.
Provide clear, calm, general health information in plain language. You may explain
common symptoms, conditions, medications, and questions to discuss with a clinician.
Do not diagnose, prescribe, or replace an in-person medical professional. Ask a
clarifying question when needed. For emergencies or potentially life-threatening
symptoms, tell the user to call local emergency services immediately.
Keep answers concise and easy to understand because they will be read aloud."""


def get_api_key() -> str | None:
    """Read the API key from Streamlit Secrets or a local .env file."""
    try:
        secret_key = st.secrets.get("OPENAI_API_KEY")
    except (FileNotFoundError, KeyError):
        secret_key = None

    return secret_key or os.getenv("OPENAI_API_KEY")


def transcribe_audio(client: OpenAI, audio_bytes: bytes) -> str:
    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = "recording.wav"
    transcript = client.audio.transcriptions.create(
        model="gpt-4o-mini-transcribe",
        file=audio_file,
    )
    return transcript.text.strip()


def get_medical_response(client: OpenAI, transcript: str) -> str:
    response = client.responses.create(
        model="gpt-4o-mini",
        instructions=SYSTEM_PROMPT,
        input=transcript,
    )
    return response.output_text.strip()


def synthesize_speech(client: OpenAI, text: str) -> bytes:
    speech = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="coral",
        input=text,
        response_format="mp3",
    )
    return speech.content


st.title("Medical Voice AI Assistant")
st.write("Ask a general health question by voice and receive a spoken response.")
st.caption("For general information only. This assistant is not a substitute for professional medical care.")

api_key = get_api_key()
if not api_key:
    st.error("OPENAI_API_KEY is missing. Add it to your local .env file or Streamlit Secrets.")
    st.stop()

client = OpenAI(api_key=api_key)
audio = st.audio_input("Record your question", key="medical_question")

if audio is not None:
    st.audio(audio)

    if st.button("Get medical response", type="primary", use_container_width=True):
        try:
            with st.spinner("Listening and preparing a response..."):
                transcript = transcribe_audio(client, audio.getvalue())

                if not transcript:
                    st.warning("I could not hear a question. Please record again.")
                    st.stop()

                answer = get_medical_response(client, transcript)
                spoken_answer = synthesize_speech(client, answer)

            st.subheader("You asked")
            st.write(transcript)
            st.subheader("Assistant response")
            st.write(answer)
            st.audio(spoken_answer, format="audio/mpeg")
        except OpenAIError:
            st.error("OpenAI could not process that request. Check your API key, account access, and try again.")
        except Exception:
            st.error("Something went wrong while processing the recording. Please try again.")
