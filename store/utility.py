import tensorflow as tf
print("TensorFlow Version:", tf.__version__)
from tensorflow import keras 
import os
import numpy as np
from tensorflow.python.keras.models import load_model
from PIL import Image
from tensorflow.keras.applications.vgg16 import preprocess_input
print("VGG16 module is available!")
from django.conf import settings


# Define class labels based on the trained model categories
CLASS_LABELS = ["Pencil Drawing", "Thread Art", "Painting"]

# Load the model (using relative path)
MODEL_PATH = os.path.join(settings.BASE_DIR, "store", "ml model", "")

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")

# Compile the model
model = load_model(MODEL_PATH)
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

def classify_image(img_path):
    """Preprocess and classify the image using the trained model"""
    try:
        img = Image.open(img_path).resize((224, 224)).convert('RGB') # convert to RGB
        img_array = np.array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array) # preprocess the image

        # Make prediction
        predictions = model.predict(img_array)
        predicted_index = np.argmax(predictions)
        return CLASS_LABELS[predicted_index]  # Return predicted category name
    except Exception as e:
        print(f"Error processing image: {e}")
        raise