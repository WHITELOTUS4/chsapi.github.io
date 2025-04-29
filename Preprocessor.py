from PIL import Image
from datetime import datetime
import logging
import json
from module import imgCompressor, imgConverter, imgToPdf, deepfakeDetector
import random
import base64
import io
import aiohttp
import asyncio
import requests
import sys

assumption = random.choice([0,1])
img_extensions = ['.jpg', '.jpeg', '.png', '.peng', '.bmp', '.gif', '.webp', '.svg', '.jpe', '.jfif', '.tar', '.tiff', '.tga']
vdo_extensions = ['.mp4','.mov', '.wmv', '.avi', '.avchd', '.flv', '.f4v', '.swf', '.mkv', '.webm', '.html5']
manifest = None
single_img_bin = []

def sum(a, b):
    return a+b

def sub(a, b):
    return a-b

import os
script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, 'assets', 'manifest.json')
with open(json_path, 'r') as data:
    manifest = json.load(data)
# module_dir = os.path.dirname(__file__)
# if os.path.exists(os.path.join(module_dir, 'module', 'temp.py')):
#     from module import temp as deepfakeDetector
# with open('./assets/manifest.json') as data:
#     manifest = json.load(data)

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
    
    def base64_type(media_data):
        if not media_data.startswith("data:"):
            return False
        try:
            header, encoded_data = media_data.split(",", 1)
            type = header.split(":")[1].split("/")[0].lower()
            return type
        except Exception as e:
            print(f"Error to reading media: {e}")
            return False
        
    def base64_ext(media_data):
        if not media_data.startswith("data:"):
            return False
        try:
            header, encoded_data = media_data.split(",", 1)
            ext = header.split(";")[0].split("/")[1].lower()
            return ext
        except Exception as e:
            print(f"Error to reading media: {e}")
            return False
        
    def merge_list_to_string(array, delimiter=''):
        return delimiter.join(array)
    
    def represent(value):
        print(f"value: {str(value)}, Type: {type(value)}")

class MutableDict(dict):
    def update(self, key_path, new_value):
        key_list = key_path.split('.')
        current_dict = self
        # print(current_dict)
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
    
    def initial_responce():
        schema = MutableDict(manifest['root_schema'])
        return schema['html_content']
    
    def send_parts_with_ack(main_string, limit):
        print("define ",limit)
        chunk_size = sys.getsizeof(str(main_string))/1024
        chunk_no = round(chunk_size / 900) + 2
        part_length = int(len(main_string) / chunk_no)+1
        print("Custome limit ", chunk_size, chunk_no, part_length)
        # return [limit, chunk_size, chunk_no, part_length]
        # parts = []
        # for i in range(chunk_no):
        #     parts.append(main_string[i * part_length : (i + 1) * part_length])
        #     # print(f"{i} part value {(parts[i])[0:50]}\t{(parts[i])[-50:]}\n")
        # print(len(parts))
    
        # async def send_part(part, index, limit):
        #     attempts = 0
        #     while attempts < 3:
        #         attempts += 1
        #         try:
                    # async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
                    #     async with session.post('http://127.0.0.1:5000/load/response',
                    #         headers={
                    #             'Content-Type': 'application/json',
                    #         },
                    #         json = {
                    #             "img": part,
                    #             "limit": limit,
                    #             "index": index,
                    #         }
                    #     ) as response:
                    #         if response.status != 200:
                    #             raise ValueError(f"HTTP error! Status: {response.status}")
                    #         data = await response.json()
                    #         print(f"Attempt {attempts}:", data)
                    #         if data.get("ack") == index:
                    #             return True
        #             url = 'http://127.0.0.1:5000/load/response'
        #             headers = {"Content-Type": "application/json"}
        #             response = requests.post(url, headers=headers, data=json.dumps({"img": part,"limit": limit,"index": index}))
        #             response.raise_for_status()  # Raise an exception for bad status codes

        #             return {"message": "Data sent successfully"}
        #         except Exception as e:
        #             print(f"Error on attempt {attempts} for part {index}: {e}")
        #     return False
        # # parts.reverse()
        # for i in range(len(parts)):
        #     is_success = await send_part(parts[i], i + 1, chunk_no)
        #     print(f"{i} part value {(parts[i])[0:50]}\t{(parts[i])[-50:]}\n")
        #     if not is_success:
        #         return False
        # return True

    
class Authentication:
    auth_file = './assets/auth.json'

    def isValidAccess(key):
        try:
            if key == '' or key == None:
                return True
            json_path = os.path.join(script_dir, 'assets', 'auth.json')
            with open(json_path, 'r') as data:
                auth_data = json.load(data)
                # with open(Authentication.auth_file) as data:
                #     auth_data = json.load(data)
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
            json_path = os.path.join(script_dir, 'assets', 'auth.json')
            with open(json_path, 'r') as data:
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
            json_path = os.path.join(script_dir, 'assets', 'auth.json')
            with open(json_path, 'r') as data:
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
    def error_schema():
        script_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(script_dir, 'assets', 'manifest.json')
        with open(json_path, 'r') as data:
            manifest = json.load(data)
            return MutableDict(manifest['error_schema'])
    
    def methodException(path, method):
        error = (customException.error_schema()).update("error", "Method Exception")
        error = error.update("detail.desc", manifest['error_log'][20]['desc'])
        error = error.update("detail.path", path)
        error = error.insert("detail.method", method)
        error = error.update("status.code", 405)
        error = error.update("status.message", "Task Faild due to invaild method access")
        return error

    def notFoundException(path, method):
        error = (customException.error_schema()).update("error", "Path Exception")
        error = error.update("detail.desc", manifest['error_log'][20]['desc'])
        error = error.update("detail.path", path)
        error = error.insert("detail.method", method)
        error = error.update("status.code", 404)
        error = error.update("status.message", "Task Faild due to invaild hit point")
        return error

    def accessException(path, key):
        error = (customException.error_schema()).update("error", "Access Exception")
        error = error.update("detail.desc", manifest['error_log'][18]['desc'])
        error = error.update("detail.path", path)
        error = error.insert("detail.key", key)
        error = error.update("status.code", 401)
        error = error.update("status.message", "Task Faild due to unauthorized access")
        return error
    
    def unsupportException(path, extension):
        error = (customException.error_schema()).update("error", "Unsupport Media Exception")
        error = error.update("detail.desc", manifest['error_log'][1]['desc'])
        error = error.update("detail.path", path)
        error = error.insert("detail.extension", extension)
        error = error.update("network.url", "https://chsapi.vercel.app/api/")
        error = error.update("status.code", 415)
        error = error.update("status.message", "Task Faild due to invaild extension")
        return error
    
    def convertationException(path, extension):
        error = (customException.error_schema()).update("error", "Unsupport Convertation Exception")
        error = error.update("detail.desc", manifest['error_log'][17]['desc'])
        error = error.update("detail.path", path)
        error = error.insert("detail.extension", extension)
        error = error.update("network.url", "https://chsapi.vercel.app/api/")
        error = error.update("status.code", 422)
        error = error.update("status.message", "Task Faild due to unsupported convertation")
        return error
    
    def processException(path, data):
        error = (customException.error_schema()).update("error", "Unprocessable Exception")
        error = error.update("detail.desc", manifest['error_log'][19]['desc'])
        error = error.update("detail.path", path)
        error = error.insert("detail.input", data)
        error = error.update("network.url", "https://chsapi.vercel.app/api/")
        error = error.update("status.code", 422)
        error = error.update("status.message", "Task Faild due to unprocessable information")
        return error

class TaskMaster:
    def convert_img(input_list):
        src = imgConverter.convert_image(input_list)
        return src
    def resize_img(image_path, width, height):
        src = imgCompressor.resize_image(image_path, width, height)
        return src
    def dfd_img(input_list, key):
        key_type = Authentication.keyType(key)
        if key_type == 'Private':
            src = deepfakeDetector.detect_image(input_list, 'all')
        elif key_type == 'Public':
            src = deepfakeDetector.detect_image(input_list, 'single')
        else:
            src = 18
        return src
    def dfd_vdo(input_list, key):
        src = deepfakeDetector.detect_video(input_list)
        return src
    def enhance_img(input_list):
        src = imgCompressor.compress_image(input_list)
        return src
    def compress_img(input_list):
        if input_list[3] != None:
            return imgCompressor.compress_image(['degrade', input_list[0], input_list[3]])
        else:
            return TaskMaster.resize_img(input_list[0], input_list[1], input_list[2])
    
class Middleware:
    def security(method, allow_method, path, key):
        if not Authentication.isValidAccess(key):
            return customException.accessException(path, key)
        if method not in allow_method:
            return customException.methodException(path, method)
        