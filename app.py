from flask import Flask, render_template, request, jsonify
from module.text_to_speech import text_to_speech
from module.speech_to_text import audio_to_text
from werkzeug.utils import secure_filename
import os
import wikipedia

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# dossier pour stocker temporairement les fichiers audio
AUDIO_FOLDER = os.path.join("static", "audio")
os.makedirs(AUDIO_FOLDER, exist_ok=True)

# ------------------- Page d'accueil -------------------
@app.route('/')
def index():
    return render_template('index.html')

# ------------------- Text → Speech -------------------
@app.route('/text-to-speech', methods=['GET', 'POST'])
def text_to_speech_page():
    audio_file = None
    if request.method == 'POST':
        text = request.form.get('text')
        if text and text.strip():
            audio_file = text_to_speech(text)
    return render_template('text_to_speech.html', audio_file=audio_file)

# ------------------- Speech → Text -------------------
@app.route('/speech-to-text', methods=['GET', 'POST'])
def speech_to_text_page():
    recognized_text = None
    if request.method == 'POST':
        # Récupérer le fichier audio depuis le formulaire
        file = request.files.get('recorded_audio') or request.files.get('audio_file')
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            path = os.path.join(AUDIO_FOLDER, filename)

            # Sauvegarder temporairement
            file.save(path)

            # Conversion audio → texte
            recognized_text = audio_to_text(path)

            # Supprimer le fichier après traitement
            os.remove(path)
    return render_template('speech_to_text.html', recognized_text=recognized_text)

# ------------------- Recherche en temps réel depuis la voix -------------------
@app.route('/search-from-voice', methods=['POST'])
def search_from_voice():
    data = request.get_json()
    query = data.get('query', '').strip()

    if not query:
        return jsonify({'results': 'Aucun mot détecté.'})

    try:
        # Récupère le résumé du mot (1-2 phrases)
        summary = wikipedia.summary(query, sentences=2, auto_suggest=True, redirect=True)
        result_html = f"<b>{query} :</b> {summary}"
    except wikipedia.exceptions.DisambiguationError as e:
        result_html = f"{query} : Plusieurs résultats possibles. Exemple : {', '.join(e.options[:5])}"
    except wikipedia.exceptions.PageError:
        result_html = f"Aucune définition trouvée pour '{query}'"
    except Exception as e:
        result_html = f"Erreur : {str(e)}"

    return jsonify({'results': result_html})

# ------------------- Autres pages -------------------
@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/translation')
def translation():
    return render_template('translation.html')

@app.route('/image-recognition')
def image_recognition():
    return render_template('image_recognition.html')


if __name__ == '__main__':
    app.run(debug=True)
