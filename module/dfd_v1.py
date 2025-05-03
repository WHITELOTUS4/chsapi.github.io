import io
import base64
import numpy as np
from PIL import Image
import Preprocessor
import onnxruntime as ort
import av 

# Load model
session = ort.InferenceSession("./model/dfd_p3.onnx")
input_name = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name
TARGET_SIZE = (128, 128)

def analyze_classification_sequence(predictions):
    if not predictions:
        return {"error": "Empty prediction list"}

    result_class = "Real"
    fake_sequences = []
    current_sequence = []
    fake_acc_total = 0

    for i, item in enumerate(predictions):
        label = item.get("class", "").lower()

        if label == "fake":
            current_sequence.append(item)
            if len(current_sequence) >= 2:
                fake_sequences = current_sequence.copy()
        else:
            current_sequence = []

    if fake_sequences:
        result_class = "Fake"
        total_accuracy = sum([f["accuracy"] for f in fake_sequences])
        avg_accuracy = round(total_accuracy / len(fake_sequences), 2)
        start_time = fake_sequences[0]["second"]
        end_time = fake_sequences[-1]["second"]

        return {
            "class": result_class,
            "accuracy": avg_accuracy,
            "period": [start_time, end_time]
        }

    # If no serial "Fake" detected, calculate average accuracy of all "Real" labels
    real_preds = [p for p in predictions if p.get("class", "").lower() == "real"]
    if real_preds:
        total_accuracy = sum([p["accuracy"] for p in real_preds])
        avg_accuracy = round(total_accuracy / len(real_preds), 2)
        return {
            "class": "Real",
            "accuracy": avg_accuracy,
            "period": [real_preds[0]["second"], real_preds[-1]["second"]]
        }

    return {"error": "No valid classification data"}


# Preprocess PIL image
def preprocess_image(image):
    image = image.resize(TARGET_SIZE)
    img_array = np.array(image).astype(np.float32) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

# Classify frame
def classify_frame(image):
    img_array = preprocess_image(image)
    prediction = session.run([output_name], {input_name: img_array})[0]
    confidence = float(np.max(prediction))
    label = "Real" if confidence >= 0.83 else "Fake"
    accuracy = round(confidence * 100, 2)
    if accuracy == 100:
        accuracy = 99.98
    return {"class": label, "accuracy": accuracy}

# Main function to process video (base64 string)
def classify_video_base64(base64_video_str):
    try:
        if not base64_video_str.startswith("data:video"):
            return {"error": "Invalid video base64 input"}

        header, base64_data = base64_video_str.split(",", 1)
        video_bytes = base64.b64decode(base64_data)

        container = av.open(io.BytesIO(video_bytes))
        predictions = []
        seconds_seen = set()

        for frame in container.decode(video=0):
            sec = int(frame.time)
            if sec not in seconds_seen:
                seconds_seen.add(sec)
                img = frame.to_image()  # Convert to PIL Image
                result = classify_frame(img)
                predictions.append({
                    "second": sec,
                    **result
                })

        if not predictions:
            return {"error": "No frames processed"}
        result = analyze_classification_sequence(predictions)
        return result

    except Exception as e:
        return {"error": str(e)}

def detect_video(input_list):
    video_path = str(input_list[0])
    extension = str(input_list[1])
    new_video_path = None

    # print(f"video load: {video_path}")
    if(video_path=='load'):
        video_path = Preprocessor.Tools.merge_list_to_string(Preprocessor.single_img_bin)
    
    if Preprocessor.Tools.is_video(video_path) == True:
        new_video_path = classify_video_base64(video_path)
        if "error" in new_video_path:
            print(f"Error: {new_video_path['error']}")
            return 19
        else:
            return new_video_path
    else:
        # print("Unsupported video format. Only PNG and JPG are supported.")
        return 1    #custome error code
