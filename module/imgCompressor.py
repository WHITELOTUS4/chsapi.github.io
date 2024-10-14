import sys
import cv2
import Preprocessor
from PIL import Image, ImageEnhance, ImageFilter
import io
import base64
import os

def resizeImage(image_path, width, height):
    img = cv2.imread(image_path)
    (current_height, current_width) = (height, width)
    
    if current_width > 200 or current_height > 200:
        if current_width > current_height:
            new_width = 200
            new_height = int((200 / current_width) * current_height)
        else:
            new_height = 200
            new_width = int((200 / current_height) * current_width)
        
        img = cv2.resize(img, (new_width, new_height))
        
        filename, file_extension = os.path.splitext(image_path)
        temp_image_path = f"D:/.vscode/Vs programmes/Df Detector/server-side/public/temp_image.jpg"
        cv2.imwrite(temp_image_path, img)
        
        return temp_image_path, new_width, new_height
    else:
        return "Image size under conditions", current_width, current_height

def enhance_image(image_data, brightness, contrast, sharpness):
    image_bytes = base64.b64decode(image_data.split(",")[1])
    image = Image.open(io.BytesIO(image_bytes))

    # image = image.convert("RGB")

    sharpness_enhancer = ImageEnhance.Sharpness(image)
    image = sharpness_enhancer.enhance(sharpness)

    image = image.filter(ImageFilter.SMOOTH_MORE)

    brightness_enhancer = ImageEnhance.Brightness(image)
    image = brightness_enhancer.enhance(brightness)

    contrast_enhancer = ImageEnhance.Contrast(image)
    image = contrast_enhancer.enhance(contrast)

    ext = str(Preprocessor.Tools.find_extension(image_data))

    buffer = io.BytesIO()
    image.save(buffer, format=ext)

    enhanced_image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f"data:image/{ext};base64,{enhanced_image_base64}"

def degrade_image(image_data, quality=20):
    image_bytes = base64.b64decode(image_data.split(",")[1])
    image = Image.open(io.BytesIO(image_bytes))

    image = image.convert("RGB")
    
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=quality)

    degraded_image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f"data:image/jpeg;base64,{degraded_image_base64}"


def compress_image(input_list):
    image_path = str(input_list[0])
    brightness = 1.2 if input_list[1] == None else float(input_list[1])
    contrast = 1.3 if input_list[2] == None else float(input_list[2])
    sharpness = 2.0 if input_list[3] == None else float(input_list[3])
    print(brightness, contrast, sharpness)
    return enhance_image(image_path, brightness, contrast, sharpness)