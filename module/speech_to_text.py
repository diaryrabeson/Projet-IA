# module/speech_to_text.py
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def audio_to_text(file_path):
    try:
        with open(file_path, "rb") as audio_file:
            result = openai.Audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return result.text
    except Exception as e:
        return f"Erreur : {str(e)}"
