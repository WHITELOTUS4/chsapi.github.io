import numpy as np
import Preprocessor
import svgwrite
import base64
from PIL import Image, ImageOps
import io

# def convert_png(image_path):
#     image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
#     if image is None:
#         raise ValueError("Image not loaded properly. Check the file path.")
#     if len(image.shape) == 3 and image.shape[2] == 4:
#         filename, _ = image_path.rsplit('.', 1)
#         new_image_path = f"{filename}.png"
#         cv2.imwrite(new_image_path, image, [int(cv2.IMWRITE_PNG_COMPRESSION), 0])
#     else:
#         if len(image.shape) == 2 or image.shape[2] == 1:
#             image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGRA)
#         else:
#             image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
#         if image.shape[2] == 3:
#             alpha_channel = np.ones((image.shape[0], image.shape[1]), dtype=np.uint8) * 255
#             image = np.dstack((image, alpha_channel))
#         filename, _ = image_path.rsplit('.', 1)
#         new_image_path = f"{filename}.png"
#         cv2.imwrite(new_image_path, image, [int(cv2.IMWRITE_PNG_COMPRESSION), 0])
#     return new_image_path

def convert_png(base64_image_path):
    if not base64_image_path.startswith("data:image"):
        return 1
    _, base64_data = base64_image_path.split(',', 1)
    image_data = base64.b64decode(base64_data)
    image = Image.open(io.BytesIO(image_data)).convert("RGBA")
    if image.mode != "RGBA":
        image = ImageOps.alpha_composite(
            Image.new("RGBA", image.size, (255, 255, 255, 255)), image.convert("RGBA")
        )
    buffered = io.BytesIO()
    image.save(buffered, format="PNG", compress_level=0)
    new_base64_image = "data:image/png;base64," + base64.b64encode(buffered.getvalue()).decode()
    return new_base64_image


def convert_jpg(image_data):
    if not image_data.startswith("data:image"):
        return 1
    image_bytes = base64.b64decode(image_data.split(",")[1])
    image = Image.open(io.BytesIO(image_bytes))
    image = image.convert("RGB")
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    jpg_image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f"data:image/jpg;base64,{jpg_image_base64}"

def convert_jpeg(image_data):
    if not image_data.startswith("data:image"):
        return 1
    image_bytes = base64.b64decode(image_data.split(",")[1])
    image = Image.open(io.BytesIO(image_bytes))
    if image.mode not in ["RGB", "L"]:
        image = image.convert("RGB")
    elif image.mode == "L":
        image = image.convert("RGB")
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=100)
    jpeg_image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f"data:image/jpeg;base64,{jpeg_image_base64}"

def convert_gif(image_path):
    return image_path

def convert_bmp(image_data):
    if not image_data.startswith("data:image"):
        return 1
    image_bytes = base64.b64decode(image_data.split(",")[1])
    image = Image.open(io.BytesIO(image_bytes))
    image = image.convert("RGBA")
    r, g, b, a = image.split()
    b = ImageOps.autocontrast(Image.composite(b, Image.new("L", b.size, 0), a))
    g = ImageOps.autocontrast(Image.composite(g, Image.new("L", g.size, 0), a))
    r = ImageOps.autocontrast(Image.composite(r, Image.new("L", r.size, 0), a))
    image = Image.merge("RGB", (r, g, b))
    buffer = io.BytesIO()
    image.save(buffer, format="BMP")
    jpeg_image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f"data:image/bmp;base64,{jpeg_image_base64}"

def convert_svg(image_data):
    if not image_data.startswith("data:image"):
        return 1
    image_bytes = base64.b64decode(image_data.split(",")[1])
    image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    image_np = np.array(image)
    height, width, _ = image_np.shape
    dwg = svgwrite.Drawing(size=(width, height))
    for y in range(height):
        for x in range(width):
            r, g, b, a = image_np[y, x]
            if a > 0:
                fill = svgwrite.rgb(r, g, b, '%')
                dwg.add(dwg.rect(insert=(x, y), size=(1, 1), fill=fill, fill_opacity=a / 255.0))
    buffer = io.StringIO()
    dwg.write(buffer)
    svg_content = buffer.getvalue()
    buffer.close()
    svg_base64 = base64.b64encode(svg_content.encode("utf-8")).decode("utf-8")
    return f"data:image/svg+xml;base64,{svg_base64}"

def convert_tga(image_path):
    return image_path

def convert_tiff(image_path):
    return image_path

def convert_image(input_list):
    image_path = str(input_list[0])
    extension = str(input_list[1])
    new_image_path = None

    # print(image_path)
    if(image_path=='load'):
        image_path = Preprocessor.Tools.merge_list_to_string(Preprocessor.single_img_bin)
        Preprocessor.single_img_bin.clear()

    if Preprocessor.Tools.is_image(image_path) == True:
        if extension == 'png':
            new_image_path = convert_png(image_path)
        elif extension == 'jpg':
            new_image_path = convert_jpg(image_path)
        elif extension == 'jpeg':
            new_image_path = convert_jpeg(image_path)
        elif extension == 'gif':
            new_image_path = convert_gif(image_path)
        elif extension == 'bmp':
            new_image_path = convert_bmp(image_path)
        elif extension == 'svg':
            new_image_path = convert_svg(image_path)
        else:
            # print("Unwanted media convertion try.")
            return 17   #custome error code
        return new_image_path
    else:
        # print("Unsupported image format. Only PNG and JPG are supported.")
        return 1    #custome error code
