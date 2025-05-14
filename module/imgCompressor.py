import Preprocessor
from PIL import Image, ImageEnhance, ImageFilter
import io
import base64
import os

def resize_base64_image(base64_str, width, height):
    try:
        _, encoded = base64_str.split(",", 1)
        ext = str(Preprocessor.Tools.find_extension(base64_str)).upper()

        image_data = base64.b64decode(encoded)
        image = Image.open(io.BytesIO(image_data))

        current_width, current_height = (width, height)

        if current_width > 200 or current_height > 200:
            if current_width > current_height:
                new_width = 200
                new_height = int((200 / current_width) * current_height)
            else:
                new_height = 200
                new_width = int((200 / current_height) * current_width)

            image = image.resize((new_width, new_height), Image.LANCZOS)

            buffer = io.BytesIO()
            image.save(buffer, format=ext)
            resized_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

            return f"data:image/{ext.lower()};base64,{resized_base64}", new_width, new_height
        else:
            return "Image size under conditions", current_width, current_height

    except Exception as e:
        print(f"New Error from resizer: {e}")
        return None

def enhance_base64_image(image_data, brightness, contrast, sharpness):
    try:
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
    except:
        # print("Unprocessable information gain on enhance")
        return 20   # error code

def enhance_image(input_list):
    image_path = str(input_list[0])
    brightness = 1.2 if input_list[1] == None else float(input_list[1])
    contrast = 1.3 if input_list[2] == None else float(input_list[2])
    sharpness = 2.0 if input_list[3] == None else float(input_list[3])
    new_image_path = None

    if(image_path=='load'):
        image_path = Preprocessor.Tools.merge_list_to_string(Preprocessor.single_img_bin)
        Preprocessor.single_img_bin.clear()

    if Preprocessor.Tools.is_image(image_path) == True:
        new_image_path = enhance_base64_image(image_path, brightness, contrast, sharpness)
        return new_image_path
    else:
        # print("Unsupported image format. Only PNG and JPG are supported.")
        return 1    #custome error code

def degrade_image(image_data, quality):
    image_bytes = base64.b64decode(image_data.split(",")[1])
    image = Image.open(io.BytesIO(image_bytes))
    
    ext = str(Preprocessor.Tools.find_extension(image_data))

    buffer = io.BytesIO()
    image.save(buffer, format=ext, quality=quality)

    degraded_image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f"data:image/{ext};base64,{degraded_image_base64}"

def fix_base64_padding(encoded_str):
    missing_padding = len(encoded_str) % 4
    if missing_padding:
        encoded_str += "=" * (4 - missing_padding)
    return encoded_str

def compress_base64_image(base64_str, quality=70):
    try:
        if "," in base64_str:
            _, encoded = base64_str.split(",", 1)
        
        encoded = fix_base64_padding(encoded)

        if "," in base64_str:
            ext = str(Preprocessor.Tools.find_extension(base64_str)).upper()
        else:
            ext = "JPEG"  
        
        image_data = base64.b64decode(encoded)
        image = Image.open(io.BytesIO(image_data))

        buffer = io.BytesIO()
        if ext in ["JPEG", "JPG", "JPE", "JFIF", "WEBP", "TIFF"]:
            image.save(buffer, format=ext, quality=quality, progressive=True)
        else:
            image.save(buffer, format=ext, optimize=True)
        
        compress_image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return f"data:image/{ext.lower()};base64,{compress_image_base64}"
    except Exception as e:
        print("New Error from compressor: ",e)
        return 3

def compress_image(input_list):
    image_path = str(input_list[0])
    quality = int(input_list[1])
    new_image_path = None

    # print(image_path)
    if(image_path=='load'):
        image_path = Preprocessor.Tools.merge_list_to_string(Preprocessor.single_img_bin)
        # Preprocessor.single_img_bin.clear()

    if Preprocessor.Tools.is_image(image_path) == True:
        new_image_path = compress_base64_image(image_path, quality)
        return new_image_path
    else:
        # print("Unsupported image format. Only PNG and JPG are supported.")
        return 1    #custome error code
    
    # if input_list[0] == 'enhance':
    #     image_path = str(input_list[1])
    #     brightness = 1.2 if input_list[2] == None else float(input_list[2])
    #     contrast = 1.3 if input_list[3] == None else float(input_list[3])
    #     sharpness = 2.0 if input_list[4] == None else float(input_list[4])
    #     return enhance_image(image_path, brightness, contrast, sharpness)
    # elif input_list[0] == 'degrade':
    #     image_path = str(input_list[1])
    #     quality = 20 if input_list[2] == None else int(input_list[2])
    #     return degrade_image(image_path, quality)
    # elif input_list[0] == 'resize':
    #     image_path = str(input_list[1])
    #     height = 200 if input_list[2] == None else int(input_list[2])
    #     width = 200 if input_list[2] == None else int(input_list[3])
        # return resize_image(image_path, width, height)
    # else:
    #     print("Unidentify function name call, please check name space id")