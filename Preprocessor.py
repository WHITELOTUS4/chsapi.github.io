from PIL import Image
from datetime import datetime
import logging
import json
from module import imgCompressor, imgConverter, imgToPdf
import random
import base64
import io

assumption = random.choice([0,1])
img_extensions = ['.jpg', '.jpeg', '.png', '.peng', '.bmp', '.gif', '.webp', '.svg', '.jpe', '.jfif', '.tar', '.tiff', '.tga']
vdo_extensions = ['.mp4','.mov', '.wmv', '.avi', '.avchd', '.flv', '.f4v', '.swf', '.mkv', '.webm', '.html5']
manifest = None

def sum(a, b):
    return a+b

def sub(a, b):
    return a-b

with open('./assets/manifest.json') as data:
    manifest = json.load(data)

class Tools:
    def json_log(message):
        logging.basicConfig(filename='json_data.log',level=logging.DEBUG)
        logging.debug(json.dumps({"result": message}))

    def timeStamp():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def find_extension(media_data):
        header, _ = media_data.split(",", 1)
        ext = header.split(";")[0].split("/")[1].lower()
        return ext
    
    def is_image(image_data):
        valid_extensions = img_extensions
        if not image_data.startswith("data:image/"):
            return False
        try:
            header, encoded_data = image_data.split(",", 1)
            ext = header.split(";")[0].split("/")[1].lower()
            if ("."+ext) not in valid_extensions:
                return False
        except Exception as e:
            print(f"Error parsing image data URL: {e}")
            return False
        try:
            image_bytes = base64.b64decode(encoded_data)
            image = Image.open(io.BytesIO(image_bytes))
            image.verify()  
            return True
        except Exception as e:
            print(f"Error to reading image: {e}")
            return False
    
    # import moviepy.editor as mp   # install it at first using pip
    # def is_video(video_data):
    #     valid_extensions = vdo_extensions
    #     if not video_data.startswith("data:video/"):
    #         return False
    #     try:
    #         header, encoded_data = video_data.split(",", 1)
    #         ext = header.split(";")[0].split("/")[1].lower()
    #         if ("."+ext) not in valid_extensions:
    #             return False
    #     except Exception as e:
    #         print(f"Error parsing video data URL: {e}")
    #         return False
    #     try:
    #         video_bytes = base64.b64decode(encoded_data)
    #         video_stream = io.BytesIO(video_bytes)
    #         video = mp.VideoFileClip(video_stream)
    #         video_duration = video.duration
    #         return True if video_duration > 0 else False
    #     except Exception as e:
    #         print(f"Error to reading video: {e}")
    #         return False

class MutableDict(dict):
    def update(self, key_path, new_value):
        key_list = key_path.split('.')
        current_dict = self
        if len(key_list) == 1:
            if key_list[0] not in current_dict:
                raise KeyError(f"Key '{key_list[0]}' not found in object")
            current_dict[key_list[0]] = new_value
            return self
        
        for key in key_list[:-1]:
            if key not in current_dict:
                raise KeyError(f"Key '{key}' not found in object")
            current_dict = current_dict[key]
            if not isinstance(current_dict, dict):
                raise ValueError(f"{key} is not a object")
            if key_list[-1] not in current_dict:
                raise KeyError(f"Key '{key_list[-1]}' not found in object")
            current_dict[key_list[-1]] = new_value
            return self
        
    def insert(self, key_path, value):
        key_list = key_path.split('.')
        current_dict = self
        if len(key_list) == 1:
            if key_list[0] in current_dict:
                print(f"\tInsert Key '{key_list[0]}' already exist")
            current_dict[key_list[0]] = value
            return self
        
        for key in key_list[:-1]:
            if key not in current_dict:
                current_dict[key] = {}
            current_dict = current_dict[key]
            if not isinstance(current_dict, dict):
                raise ValueError(f"{key} is not a object")
            if key_list[-1] in current_dict:
                print(f"\tInsert Key '{key_list[-1]}' already exist")
            current_dict[key_list[-1]] = value
            return self

class Responce:
    def model(key):
        type = Authentication.keyType(key)
        if type == False:
            return customException.accessException("/",key)
        if key == '' or key == None:
            key = 'Public Key'
        result = MutableDict(manifest['result_schema']).update("metadata.request_id", key)
        result = result.update("metadata.timestamp", Tools.timeStamp())
        return result
    
class Authentication:
    auth_file = './assets/auth.json'

    def isValidAccess(key):
        try:
            if key == '' or key == None:
                return True
            with open(Authentication.auth_file) as data:
                auth_data = json.load(data)
                for i in range (0, len(auth_data['valid_key'])):
                    if key == auth_data['valid_key'][i]:
                        return True
                return False    # Invalid access
        except:
            return False
        
    def keyType(key):
        try:
            if key == '' or key == None:
                return 'Public'
            with open(Authentication.auth_file) as data:
                auth_data = json.load(data)
                for i in range (0, len(auth_data['valid_key'])):
                    if key == auth_data['valid_key'][i]:
                        return 'Private'
                return False    # Fake key
        except:
            return False
        
    def userDetails(key):
        try:
            if key == '' or key == None:
                return 'Public user'
            with open(Authentication.auth_file) as data:
                auth_data = json.load(data)
                for i in range (0, len(auth_data['valid_key'])):
                    if key == auth_data['valid_key'][i]:
                        try:
                            return MutableDict(auth_data['key_holder'][i]).insert("id", i)
                        except:
                            return "Non Reserved Private Key"
                return False
        except:
            return False

class customException:
    def methodException(path, method):
        error = MutableDict(manifest['error_schema']).update("error", "Method Exception")
        error = error.update("detail.desc", manifest['error_log'][19]['desc'])
        error = error.update("detail.path", path)
        error = error.insert("detail.method", method)
        error = error.update("status.code", 405)
        error = error.update("status.message", "Task Faild due to invaild method access")
        return error

    def notFoundException(path, method):
        error = MutableDict(manifest['error_schema']).update("error", "Path Exception")
        error = error.update("detail.desc", manifest['error_log'][19]['desc'])
        error = error.update("detail.path", path)
        error = error.insert("detail.method", method)
        error = error.update("status.code", 404)
        error = error.update("status.message", "Task Faild due to invaild hit point")
        return error

    def accessException(path, key):
        error = MutableDict(manifest['error_schema']).update("error", "Access Exception")
        error = error.update("detail.desc", manifest['error_log'][18]['desc'])
        error = error.update("detail.path", path)
        error = error.insert("detail.key", key)
        error = error.update("status.code", 401)
        error = error.update("status.message", "Task Faild due to unauthorized access")
        return error
    
    def unsupportException(path, extension):
        error = MutableDict(manifest['error_schema']).update("error", "Unsupport Media Exception")
        error = error.update("detail.desc", manifest['error_log'][1]['desc'])
        error = error.update("detail.path", path)
        error = error.insert("detail.extension", extension)
        error = error.update("network.url", "https://chsapi.vercel.app/api/")
        error = error.update("status.code", 415)
        error = error.update("status.message", "Task Faild due to invaild extension")
        return error
    
    def convertationException(path, extension):
        error = MutableDict(manifest['error_schema']).update("error", "Unsupport Convertation Exception")
        error = error.update("detail.desc", manifest['error_log'][17]['desc'])
        error = error.update("detail.path", path)
        error = error.insert("detail.extension", extension)
        error = error.update("network.url", "https://chsapi.vercel.app/api/")
        error = error.update("status.code", 422)
        error = error.update("status.message", "Task Faild due to unsupported convertation")
        return error
    
class TaskMaster:
    def convert_img(input_list):
        src = imgConverter.convert_image(input_list)
        return src
    def resize_img(image_path, width, height):
        src = imgCompressor.resizeImage(image_path, width, height)
        return src
    def enhance_img(input_list):
        src = imgCompressor.compress_image(input_list)
        return src