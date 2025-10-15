# from deep_translator import GoogleTranslator

# def translate_text(text, source_lang='fr', target_lang='en'):
#     try:
#         # Utiliser GoogleTranslator
#         translated = GoogleTranslator(source=source_lang, target=target_lang).translate(text)
#         return translated
#     except Exception as e:
#         return f"Erreur de traduction : {str(e)}"


from deep_translator import GoogleTranslator
import speech_recognition as sr
from gtts import gTTS
import os

def translate_text(text: str, source_lang='auto', target_lang='fr') -> str:
    try:
        return GoogleTranslator(source=source_lang, target=target_lang).translate(text)
    except Exception as e:
        return f"Erreur traduction : {str(e)}"


def text_to_speech(text: str, filename: str = "static/audio/tts.mp3", lang='fr'):
    tts = gTTS(text=text, lang=lang)
    tts.save(filename)
    return filename  # retourne le chemin pour le front-end



def speech_to_text_from_mic() -> str:
    """Récupère un texte depuis le micro"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Parlez maintenant...")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio, language='fr-FR')
        print(f"Vous avez dit : {text}")
        return text
    except sr.UnknownValueError:
        return "Désolé, je n'ai pas compris."
    except sr.RequestError as e:
        return f"Erreur du service : {e}"
