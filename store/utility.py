import cv2
import numpy as np
from django.core.files.uploadedfile import InMemoryUploadedFile

def extract_features(image):
    """Extracts features from an image file (uploaded file or path)."""
    
    # ✅ Handle both uploaded files & saved image paths
    if isinstance(image, InMemoryUploadedFile):
        image_array = np.asarray(bytearray(image.read()), dtype=np.uint8)
        img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    else:
        img = cv2.imread(image)  # If image is saved as a file

    if img is None:
        raise ValueError(f"Error: Could not read image {image}")

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
