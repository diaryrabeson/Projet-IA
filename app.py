from flask import Flask, render_template, request
from module.text_to_speech import text_to_speech  # module que tu as créé

app = Flask(__name__)

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
            audio_file = text_to_speech(text)  # le nom sera unique
    return render_template('text_to_speech.html', audio_file=audio_file)

# ------------------- Autres pages (placeholders) -------------------
@app.route('/speech-to-text')
def speech_to_text():
    return render_template('speech_to_text.html')

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
