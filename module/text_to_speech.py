from gtts import gTTS
import os
import uuid

def text_to_speech(text, lang='fr'):
    if not text.strip():
        return None
    
    # générer un nom de fichier unique
    filename = f"{uuid.uuid4()}.mp3"
    path = os.path.join("static", "audio", filename)
    
    tts = gTTS(text=text, lang=lang)
    tts.save(path)
    
    return filename  # retourne le nom unique
