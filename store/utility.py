import tensorflow as tf
import keras
import os
import numpy as np
from tensorflow.python.keras.models import load_model
from PIL import Image
import keras as  apps
from tensorflow.keras.applications.vgg16 import preprocess_input  # type: ignore


from django.conf import settings

# Define class labels based on the trained model categories
CLASS_LABELS = ["Pencil Drawing", "Thread Art", "Painting"]

# Load the model
MODEL_PATH = os.path.join(settings.BASE_DIR, "static/ml model/art_classifier.keras")
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")

model = load_model(MODEL_PATH)

def classify_image(img_path):
    """Preprocess and classify the image using the trained model"""
    try:
        img = Image.open(img_path).resize((224, 224))  # ✅ Replaces `image.load_img()`
        img_array = np.array(img)  # ✅ Replaces `image.img_to_array()`
        img_array = np.expand_dims(img_array, axis=0)

        # Make prediction
        predictions = model.predict(img_array)
        predicted_index = np.argmax(predictions)
        return CLASS_LABELS[predicted_index]  # Return predicted category name
    except Exception as e:
        print(f"Error processing image: {e}")
        raise