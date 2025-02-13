import numpy as np
from tensorflow.keras.models import load_model
from django.core.files.uploadedfile import UploadedFile
from PIL import Image

# Load your pre-trained model
model = load_model('path/to/your/model.h5')

def preprocess_image(image: UploadedFile) -> np.ndarray:
    # Open the image file
    img = Image.open(image)
    # Resize the image to the input size expected by your model
    img = img.resize((224, 224))  # Example size, adjust as needed
    # Convert the image to a numpy array
    img_array = np.array(img)
    # Normalize the image data
    img_array = img_array / 255.0
    # Add a batch dimension
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

def predict_category(image: UploadedFile) -> str:
    # Preprocess the image
    img_array = preprocess_image(image)
    # Make a prediction
    predictions = model.predict(img_array)
    # Get the predicted category
    predicted_category = np.argmax(predictions, axis=1)[0]
    # Map the predicted category to the actual category name
    category_mapping = {0: 'pencil', 1: 'thread art', 2: 'paintings'}
    return category_mapping[predicted_category]