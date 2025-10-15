# module/chatbot.py
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import re
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# --- Modèle embeddings pour recherche locale
embed_model = SentenceTransformer('all-MiniLM-L6-v2')
documents = [
    "Python est un langage de programmation très populaire.",
    "Flask est un framework web léger pour Python.",
    "FAISS est une librairie pour la recherche rapide sur des vecteurs.",
    "Les embeddings permettent de représenter le texte sous forme de vecteurs.",
    "Un chatbot peut utiliser des embeddings pour trouver la réponse la plus pertinente."
]
doc_embeddings = embed_model.encode(documents, convert_to_numpy=True)
dim = doc_embeddings.shape[1]
index = faiss.IndexFlatL2(dim)
index.add(doc_embeddings)

# --- DialoGPT pour génération de texte
model_name = "microsoft/DialoGPT-medium"
tokenizer = AutoTokenizer.from_pretrained(model_name)
gpt_model = AutoModelForCausalLM.from_pretrained(model_name)

# --- Réponses directes
direct_responses = {
    ("bonjour", "salut", "coucou"): "Salut ! 😎",
    ("qui es-tu", "tu es qui", "qui tu es"): "Je suis ton assistant intelligent local.",
    ("comment ça va", "ça va"): "Je vais bien, merci ! Et toi ?"
}

# --- Fonction principale
def get_reply(user_message: str, top_k: int = 2) -> str:
    if not user_message.strip():
        return "Je n'ai rien compris 😅"

    text = user_message.lower().strip()
    text_clean = re.sub(r'[^\w\s\+\-\*\/\=]', '', text)

    # 1️⃣ Réponse directe
    for keys, reply in direct_responses.items():
        for key in keys:
            if key in text:
                return reply

    # 2️⃣ Calcul simple
    try:
        if any(op in text_clean for op in "+-*/"):
            allowed = "0123456789+-*/.() "
            if all(c in allowed for c in text_clean):
                return str(eval(text_clean))
    except Exception:
        pass

    # 3️⃣ FAISS embeddings
    try:
        query_emb = embed_model.encode([user_message], convert_to_numpy=True)
        distances, indices = index.search(query_emb, top_k)
        if distances[0][0] < 0.8:  # seuil pour éviter réponses incohérentes
            reply_docs = [documents[i] for i in indices[0]]
            return " ".join(reply_docs)
    except Exception:
        pass

    # 4️⃣ Génération avec DialoGPT
    try:
        inputs = tokenizer.encode(user_message + tokenizer.eos_token, return_tensors="pt")
        reply_ids = gpt_model.generate(inputs, max_length=100, pad_token_id=tokenizer.eos_token_id)
        reply = tokenizer.decode(reply_ids[:, inputs.shape[-1]:][0], skip_special_tokens=True)
        return reply if reply else "Je n'ai pas compris 😅"
    except Exception:
        return "Désolé, je n'ai pas trouvé de réponse pertinente 😅"
