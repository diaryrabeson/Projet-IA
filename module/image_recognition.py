# module/image_recognition.py
import numpy as np
from tensorflow.keras.applications.mobilenet_v2 import MobileNetV2, decode_predictions, preprocess_input
from tensorflow.keras.preprocessing import image
from deep_translator import GoogleTranslator

# Charger le modèle une seule fois
model = MobileNetV2(weights='imagenet')

def recognize_image(img_path, top_n=10):
    """
    Analyse une image et retourne les top_n objets détectés avec description en français.
    """
    img = image.load_img(img_path, target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)

    preds = model.predict(x)
    decoded = decode_predictions(preds, top=top_n)[0]

    results = []
    for (_, desc, prob) in decoded:
        try:
            desc_fr = GoogleTranslator(source='en', target='fr').translate(desc)
        except Exception:
            desc_fr = desc
        results.append({
            "description": desc_fr,
            "probability": round(float(prob) * 100, 2)
        })
    return results
