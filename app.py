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

    return (secret_key or os.getenv("OPENAI_API_KEY") or "").strip() or None


def transcribe_audio(client: OpenAI, audio_bytes: bytes) -> str:
    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = "recording.wav"
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
    )
    return transcript.text.strip()


def get_medical_response(client: OpenAI, transcript: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": transcript},
        ],
    )
    return response.choices[0].message.content.strip()


def synthesize_speech(client: OpenAI, text: str) -> bytes:
    speech = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
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
        except OpenAIError as error:
            error_message = str(error)
            if "401" in error_message or "Incorrect API key" in error_message:
                detail = "The OpenAI API key is invalid or expired. Create a new key and update your Secret."
            elif "429" in error_message or "quota" in error_message.lower():
                detail = "The OpenAI account has no available quota. Check billing and usage limits."
            elif "model" in error_message.lower():
                detail = "The selected OpenAI model is unavailable for this account."
            else:
                detail = "OpenAI rejected the request. Check the app logs for the full error."
            st.error(detail)
            st.caption(f"OpenAI error: {error_message[:300]}")
        except Exception:
            st.error("Something went wrong while processing the recording. Please try again.")
