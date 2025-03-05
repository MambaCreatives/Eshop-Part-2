import cv2
import numpy as np
from PIL import Image

def extract_features(image_path):
    """Extracts features from the uploaded image (color histogram + edges)."""
    img = cv2.imread(image_path)
    img = cv2.resize(img, (128, 128))

    # Convert to grayscale and extract edges
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)

    # Extract color histogram
    hist = cv2.calcHist([img], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    hist = cv2.normalize(hist, hist).flatten()

    # Combine features
    features = np.hstack((hist, edges.flatten()))
    return features
