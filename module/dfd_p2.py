import base64
import io
import numpy as np
import Preprocessor
from PIL import Image
import onnxruntime as ort

# Load ONNX model
onnx_model_path = './model/dfd_p2.onnx'
import requests

# Replace with your Google Drive shareable file ID
# https://drive.google.com/file/d/1Xla03DkeP8K0Izyd1wyW6pe-nTis4OpH/view?usp=sharing
print("Drive model export start...\n")
GOOGLE_DRIVE_FILE_ID = "1Xla03DkeP8K0Izyd1wyW6pe-nTis4OpH"
GOOGLE_DRIVE_MODEL_URL = f"https://drive.google.com/uc?export=download&id={GOOGLE_DRIVE_FILE_ID}"

# Load ONNX model directly from Google Drive into memory
def load_onnx_model_from_drive():
    response = requests.get(GOOGLE_DRIVE_MODEL_URL)
    response.raise_for_status()  # Raise error if the download fails

    model_bytes = io.BytesIO(response.content)
    session = ort.InferenceSession(model_bytes.read())
    return session

session = load_onnx_model_from_drive()
input_name = session.get_inputs()[0].name

print("Drive model loading, done\n")

# session = ort.InferenceSession(onnx_model_path)
# input_name = session.get_inputs()[0].name

# Preprocessing base64 image
def preprocess_base64_image(base64_string):
    try:
        if not base64_string.startswith("data:image"):
            return None

        _, base64_data = base64_string.split(",", 1)
        image_data = base64.b64decode(base64_data)
        image = Image.open(io.BytesIO(image_data)).convert("RGB")

        # Resize and normalize
        image = image.resize((224, 224))
        img_array = np.array(image).astype(np.float32) / 255.0
        img_array = np.transpose(img_array, (2, 0, 1))  # To CHW
        img_array = np.expand_dims(img_array, axis=0)   # Add batch dim (1, 3, 224, 224)

        return img_array
    except Exception as e:
        print(f"Error preprocessing base64 image: {e}")
        return None

# Classify base64 image
def classify_base64_image(base64_string):
    try:
        img_array = preprocess_base64_image(base64_string)
        if img_array is None:
            return {"error": "Failed to preprocess image"}

        print("Drive model export start...\n")
        # session = load_onnx_model_from_drive()
        input_name = session.get_inputs()[0].name
        print("Drive model loading, done\n")
        output = session.run(None, {input_name: img_array})[0]
        prediction = float(output[0][0])  # Real confidence score

        label = 'Real' if prediction >= 0.85 else 'Fake'
        accuracy = round(prediction * 100, 2) if label == 'Real' else round(prediction * 100, 2)
        accuracy = 99.98 if accuracy == 100 else accuracy

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
