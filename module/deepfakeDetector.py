import os
import numpy as np
import Preprocessor
# import tensorflow as tf
from tensorflow import keras
import base64
from PIL import Image, ImageOps
import io

# Suppress TensorFlow warnings and informational messages
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

# Ensure the working directory is the script's location
os.chdir(os.path.dirname(__file__))

# Load the saved Keras model
model_path = './cnn2.keras'
if not os.path.exists(model_path):
    raise FileNotFoundError(f"Model file not found at {model_path}")
model = keras.models.load_model(model_path)

# Preprocessing function for base64 image
def preprocess_base64_image(base64_string):
    try:
        if not base64_string.startswith("data:image"):
            return None
        
        _, base64_data = base64_string.split(',', 1)
        image_data = base64.b64decode(base64_data)
        image = Image.open(io.BytesIO(image_data)).convert("RGB")
        
        image = image.resize((128, 128))
        img_array = np.array(image) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        return img_array
    except Exception as e:
        print(f"Error preprocessing image: {e}")
        return None
    
# Classification function for base64 image
def classify_base64_image(base64_string):
    try:
        img_array = preprocess_base64_image(base64_string)
        if img_array is None:
            return {"error": "Failed to preprocess image"}

        prediction = model.predict(img_array)[0][0]
        label = 'Fake' if prediction > 0.5 else 'Real'
        accuracy = round(prediction * 100, 2) if label == 'Fake' else round((1 - prediction) * 100, 2)

        return {"class": label, "accuracy": accuracy}
    except Exception as e:
        return {"error": str(e)}


def detect_image(input_list):
    image_path = str(input_list[0])
    extension = str(input_list[1])
    new_image_path = None

    # print(f"image load: {image_path}")
    if(image_path=='load'):
        image_path = Preprocessor.Tools.merge_list_to_string(Preprocessor.single_img_bin)
        Preprocessor.single_img_bin.clear()

    if Preprocessor.Tools.is_image(image_path) == True:
        new_image_path = classify_base64_image(image_path)
        if "error" in new_image_path:
            print(f"Error: {new_image_path['error']}")
            return 19
        else:
            return new_image_path
    else:
        # print("Unsupported image format. Only PNG and JPG are supported.")
        return 1    #custome error code