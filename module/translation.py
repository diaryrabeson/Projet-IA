from deep_translator import GoogleTranslator

def translate_text(text, source_lang='fr', target_lang='en'):
    try:
        # Utiliser GoogleTranslator
        translated = GoogleTranslator(source=source_lang, target=target_lang).translate(text)
        return translated
    except Exception as e:
        return f"Erreur de traduction : {str(e)}"
