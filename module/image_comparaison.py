import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim

def get_image_details(img_path):
    """Analyse une image et renvoie ses caractéristiques principales."""
    img = cv2.imread(img_path)
    if img is None:
        raise ValueError(f"Impossible de lire l'image : {img_path}")

    # Dimensions
    height, width, channels = img.shape

    # Taille du fichier (en Ko)
    import os
    file_size = round(os.path.getsize(img_path) / 1024, 2)

    # Moyenne des couleurs (R, G, B)
    mean_color = cv2.mean(img)[:3]  # (B, G, R)
    mean_color = tuple(map(lambda x: round(x, 2), mean_color[::-1]))  # Convertir en (R, G, B)

    # Histogramme global (intensité)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    hist_mean = round(np.mean(hist), 2)
    hist_std = round(np.std(hist), 2)

    return {
        "path": img_path,
        "width": width,
        "height": height,
        "channels": channels,
        "file_size_kb": file_size,
        "mean_color": mean_color,
        "hist_mean": hist_mean,
        "hist_std": hist_std
    }

def compare_images(img1_path, img2_path):
    """Compare deux images et renvoie leur score de similarité + détails."""
    img1 = cv2.imread(img1_path)
    img2 = cv2.imread(img2_path)

    if img1 is None or img2 is None:
        raise ValueError("Impossible de lire une des images.")

    # Redimensionner pour comparaison
    img1 = cv2.resize(img1, (500, 500))
    img2 = cv2.resize(img2, (500, 500))

    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    score, diff = ssim(gray1, gray2, full=True)
    diff = (diff * 255).astype("uint8")

    return score, diff
