# import sys
# import Preprocessor
# from PIL import Image, ImageEnhance, ImageFilter
# import io
# import base64
# import os

# def resizeImage(image_path, width, height):
#     img = cv2.imread(image_path)
#     (current_height, current_width) = (height, width)
    
#     if current_width > 200 or current_height > 200:
#         if current_width > current_height:
#             new_width = 200
#             new_height = int((200 / current_width) * current_height)
#         else:
#             new_height = 200
#             new_width = int((200 / current_height) * current_width)
        
#         img = cv2.resize(img, (new_width, new_height))
        
#         filename, file_extension = os.path.splitext(image_path)
#         temp_image_path = f"D:/.vscode/Vs programmes/Df Detector/server-side/public/temp_image.jpg"
#         cv2.imwrite(temp_image_path, img)
        
#         return temp_image_path, new_width, new_height
#     else:
#         return "Image size under conditions", current_width, current_height

# def enhance_image(image_data, brightness, contrast, sharpness):
#     try:
#         image_bytes = base64.b64decode(image_data.split(",")[1])
#         image = Image.open(io.BytesIO(image_bytes))

#         # image = image.convert("RGB")

#         sharpness_enhancer = ImageEnhance.Sharpness(image)
#         image = sharpness_enhancer.enhance(sharpness)

#         image = image.filter(ImageFilter.SMOOTH_MORE)

#         brightness_enhancer = ImageEnhance.Brightness(image)
#         image = brightness_enhancer.enhance(brightness)

#         contrast_enhancer = ImageEnhance.Contrast(image)
#         image = contrast_enhancer.enhance(contrast)

#         ext = str(Preprocessor.Tools.find_extension(image_data))

#         buffer = io.BytesIO()
#         image.save(buffer, format=ext)

#         enhanced_image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
#         return f"data:image/{ext};base64,{enhanced_image_base64}"
#     except:
#         # print("Unprocessable information gain on enhance")
#         return 20   # error code

# def degrade_image(image_data, quality=20):
#     image_bytes = base64.b64decode(image_data.split(",")[1])
#     image = Image.open(io.BytesIO(image_bytes))
    
#     ext = str(Preprocessor.Tools.find_extension(image_data))

#     buffer = io.BytesIO()
#     image.save(buffer, format=ext, quality=quality)

#     degraded_image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
#     return f"data:image/{ext};base64,{degraded_image_base64}"


# def compress_image(input_list):
#     image_path = str(input_list[0])
#     brightness = 1.2 if input_list[1] == None else float(input_list[1])
#     contrast = 1.3 if input_list[2] == None else float(input_list[2])
#     sharpness = 2.0 if input_list[3] == None else float(input_list[3])
#     print(brightness, contrast, sharpness)
#     return enhance_image(image_path, brightness, contrast, sharpness)


import base64
from io import BytesIO
from PIL import Image

def compress_base64_image(base64_str, quality=70):
    try:
        if "," in base64_str:
            header, base64_str = base64_str.split(",", 1)
            format_hint = header.split("/")[1].split(";")[0].upper()
        else:
            format_hint = "JPEG"  
        
        
        image_data = base64.b64decode(base64_str)
        image = Image.open(BytesIO(image_data))

    
        if format_hint == "JPEG" and image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        
        buffer = BytesIO()
        save_kwargs = {"format": format_hint}
        
        if format_hint == "JPEG":
            save_kwargs.update({"quality": quality, "optimize": True})
        elif format_hint == "PNG":
            save_kwargs.update({"optimize": True, "compress_level": 9})

        image.save(buffer, **save_kwargs)
        buffer.seek(0)

        
        compressed_base64 = base64.b64encode(buffer.read()).decode("utf-8")

    
        return f"data:image/{format_hint.lower()};base64,{compressed_base64}"
    except Exception as e:
        print("New Error from compressor: ",e)
        return 3
    
    

def compress_image(input_list):
    image_path = str(input_list[0])
    quality = int(input_list[1])
    new_image_path = None

  
    if(image_path=='load'):
        image_path = Preprocessor.Tools.merge_list_to_string(Preprocessor.single_img_bin)
        Preprocessor.single_img_bin.clear()

    new_image_path=compress_base64_image(base64_str=image_path, quality=quality)
    return new_image_path