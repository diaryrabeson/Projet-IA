from flask import Flask, render_template, request, jsonify
from module.text_to_speech import text_to_speech
from module.speech_to_text import audio_to_text
from module.chatbot import get_reply
from module.translation import translate_text
from werkzeug.utils import secure_filename
from module.image_recognition import recognize_image
import os
import wikipedia


app = Flask(__name__)
ALLOWED_EXTENSIONS = {'txt'}
# --- Configuration dossiers
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

AUDIO_FOLDER = os.path.join("static", "audio")
os.makedirs(AUDIO_FOLDER, exist_ok=True)

# --- Wikipedia en français
wikipedia.set_lang("fr")
LLOWED_EXTENSIONS = {'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
# ------------------- Pages -------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/text-to-speech', methods=['GET', 'POST'])
def text_to_speech_page():
    audio_file = None
    error = None

    if request.method == "POST":
        # 1) récupère le texte du textarea
        text = request.form.get("text", "").strip()

        # 2) récupère le fichier uploadé (si présent)
        file = request.files.get("file")

        if file and file.filename != '':
            # vérifier l'extension
            if not allowed_file(file.filename):
                error = "Type de fichier non supporté. Seuls les .txt sont acceptés."
                return render_template("text_to_speech.html", audio_file=None, error=error)

            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # sauvegarder temporairement
            file.save(filepath)

            # lire le contenu (détection d'encodage simplifiée, tolérer erreurs)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    text_from_file = f.read().strip()
            except UnicodeDecodeError:
                # fallback si encodage différent
                with open(filepath, "r", encoding="latin-1", errors="ignore") as f:
                    text_from_file = f.read().strip()
            except Exception as e:
                text_from_file = ""
                error = f"Impossible de lire le fichier: {e}"

            # supprimer le fichier uploadé (on a lu son contenu)
            try:
                os.remove(filepath)
            except Exception:
                pass

            # si le fichier contient du texte, priorise le fichier sur le textarea
            if text_from_file:
                text = text_from_file

        # 3) si on a du texte, génère l'audio
        if text:
            try:
                audio_file = text_to_speech(text)
            except Exception as e:
                error = f"Erreur lors de la génération audio : {e}"

    return render_template("text_to_speech.html", audio_file=audio_file, error=error)

@app.route('/speech-to-text', methods=['GET', 'POST'])
def speech_to_text_page():
    recognized_text = None
    if request.method == 'POST':
        file = request.files.get('recorded_audio') or request.files.get('audio_file')
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            path = os.path.join(AUDIO_FOLDER, filename)
            file.save(path)
            recognized_text = audio_to_text(path)
            os.remove(path)
    return render_template('speech_to_text.html', recognized_text=recognized_text)

@app.route('/search-from-voice', methods=['POST'])
def search_from_voice():
    data = request.get_json()
    query = data.get('query', '').strip()
    if not query:
        return jsonify({'results': 'Aucun mot détecté.'})
    try:
        summary = wikipedia.summary(query, sentences=2, auto_suggest=True, redirect=True)
        result_html = f"<b>{query} :</b> {summary}"
    except wikipedia.exceptions.DisambiguationError as e:
        result_html = f"{query} : Plusieurs résultats possibles : {', '.join(e.options[:5])}"
    except wikipedia.exceptions.PageError:
        result_html = f"Aucune définition trouvée pour '{query}'"
    except Exception as e:
        result_html = f"Erreur : {str(e)}"
    return jsonify({'results': result_html})

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/chatbot-message', methods=['POST'])
def chatbot_message():
    data = request.get_json()
    user_message = data.get('message', '').strip()
    reply = get_reply(user_message) if user_message else "Je n'ai rien compris 😅"
    return jsonify({'reply': reply})

@app.route('/translation')
def translation_page():
    return render_template('translation.html')

@app.route('/translate', methods=['POST'])
def translate_route():
    data = request.get_json()
    text = data.get('text', '')
    source_lang = data.get('source_lang', 'auto')
    target_lang = data.get('target_lang', 'fr')
    translated = translate_text(text, source_lang, target_lang)
    return jsonify({'translated': translated})


# Lecture audio de la traduction
@app.route('/speak', methods=['POST'])
def speak():
    data = request.get_json()
    text = data.get('text', '')
    target_lang = data.get('lang', 'fr')
    audio_file = text_to_speech(text, lang=target_lang)
    return jsonify({'audio_file': audio_file})



@app.route('/image-recognition')
def image_recognition():
    return render_template('image_recognition.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)

# Route pour upload et analyser l'image
@app.route('/image-recognition', methods=['GET', 'POST'])
def image_recognition_page():
    if request.method == 'POST':
        file = request.files.get('image')
        if not file:
            return jsonify({'error': 'Aucun fichier téléchargé.'}), 400

        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            results = recognize_image(filepath)
        except Exception as e:
            print("Erreur analyse image:", e)
            return jsonify({'error': str(e)}), 500

        os.remove(filepath)
        return jsonify({'results': results})

    return render_template('image_recognition.html')




@app.route('/speech-to-text', methods=['POST'])
def speech_to_text_route():
    file = request.files.get('recorded_audio') or request.files.get('audio_file')
    if not file:
        return jsonify({'recognized_text': ''})
    filename = secure_filename(file.filename)
    path = os.path.join(AUDIO_FOLDER, filename)
    file.save(path)
    recognized_text = audio_to_text(path)
    os.remove(path)
    return jsonify({'recognized_text': recognized_text})


@app.route('/image-comparaison')
def image_comparaisoon():
    return render_template('image_comparaison.html')