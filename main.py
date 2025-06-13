from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from Preprocessor import Authentication, customException, Responce, TaskMaster, Tools, sum, Middleware, single_img_bin
from fastapi.responses import HTMLResponse
import asyncio
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

all_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]

@app.get("/", response_class=HTMLResponse)
def read_root():
    html_content = Responce.initial_responce()
    # return {"Ahoy hoy": "Universe"}
    return HTMLResponse(content=html_content)

@app.get("/api/")
def read_root():
    return {"result": "List of service is not loaded..", "time": Tools.timeStamp()}

class SingleImgLoader(BaseModel):
    img: str
    limit: int
    index: int
    key: str | None

@app.api_route("/load/single", methods=all_methods)
async def read_root(data: SingleImgLoader, request: Request):
    data.key = await Authentication.normalizeKey(data.key)
    if not Authentication.isValidAccess(data.key):
        return customException.accessException(request.url.path, data.key)
    if request.method not in ["GET", "POST", "SET"]:
        return customException.methodException(request.url.path, request.method)
    if(data.index <= data.limit and data.index > 0):
        if data.img.startswith("encrypted::"):
            _, body = data.img.split("encrypted::", 1)
            single_img_bin.append(body)
        else:
            single_img_bin.append(data.img)
        return {"ack": data.index, "part": len(single_img_bin[len(single_img_bin)-1]), "time": Tools.timeStamp()}
    else:
        print("image index out of range")

class ImgConverter(BaseModel):
    form: str
    img: str
    load: str | None
    key: str | None

@app.api_route("/api/imageConverter", methods=all_methods)
async def read_root(data: ImgConverter, request: Request):
    data.key = await Authentication.normalizeKey(data.key)
    if not Authentication.isValidAccess(data.key):
        return customException.accessException(request.url.path, data.key)
    if request.method not in ["GET", "POST"]:
        return customException.methodException(request.url.path, request.method)
    if(data.load=='true' and single_img_bin!=[]):
        src = await TaskMaster.convert_img(['load', data.form], data.key)
    else:
        img = data.img
        if img.startswith("encrypted::"):
            _, body = img.split("encrypted::", 1)
            decoded_data = await Middleware.substitution_decoder(body, data.key)
            img = decoded_data
        src = await TaskMaster.convert_img([img, data.form], data.key)
    if src == None or src == 1:
        return customException.unsupportException(request.url.path, data.form)
    if src == 17:
        return customException.convertationException(request.url.path, data.form)
    single_img_bin.clear()
    src = Responce.compress_reponce(src)
    src = await Middleware.substitution_encoder(src, data.key)
    responce = Responce.model(data.key).update("result", src)
    return responce

class DfdDetector(BaseModel):
    ext: str
    media: str
    load: str | None
    key: str | None
    heatmap: str | None

@app.api_route("/api/dfdScanner", methods=all_methods)
def read_root(data: DfdDetector, request: Request):
    if not Authentication.isValidAccess(data.key):
        return customException.accessException(request.url.path, data.key)
    if request.method not in ["GET", "POST"]:
        return customException.methodException(request.url.path, request.method)
    if(data.load=='true' and single_img_bin!=[]):
        if Tools.base64_type(single_img_bin[0]) == 'image':
            src = TaskMaster.dfd_img(['load', data.ext], data.key, data.heatmap)
        else:
            src = TaskMaster.dfd_vdo(['load', data.ext], data.key, data.heatmap)
    else:
        media = data.media
        if Tools.base64_type(media) == 'image':
            src = TaskMaster.dfd_img([media, data.ext], data.key, data.heatmap)
        else:
            src = TaskMaster.dfd_vdo([media, data.ext], data.key, data.heatmap)
    if src == None or src == 1:
        return customException.unsupportException(request.url.path, data.ext)
    if src == 19:
        return customException.convertationException(request.url.path, data.ext)
    single_img_bin.clear()
    responce = Responce.model(data.key).update("result", src)
    return responce

class ImgEnhance(BaseModel):
    img: str
    brightness: float | None
    contrast: float | None
    sharpness: float | None
    quality: int | None
    load: str | None
    key: str | None

@app.api_route("/api/imageEnhancer", methods=all_methods)
def read_root(data: ImgEnhance, request: Request):
    if not Authentication.isValidAccess(data.key):
        return customException.accessException(request.url.path, data.key)
    if request.method not in ["GET", "POST"]:
        return customException.methodException(request.url.path, request.method)
    if(data.load=='true' and single_img_bin!=[]):
        src = TaskMaster.enhance_img(['load', data.brightness, data.contrast, data.sharpness], data.key)
    else:
        media = data.img
        src = TaskMaster.enhance_img([media, data.brightness, data.contrast, data.sharpness], data.key)
    if src == None or src*0 == 0:
        ext = Tools.find_extension(media if data.load!='true' else Tools.merge_list_to_string(single_img_bin))
        if src == None or src == 1:
            return customException.unsupportException(request.url.path, ext)
        if src == 19:
            return customException.convertationException(request.url.path, ext)
    single_img_bin.clear()
    responce = Responce.model(data.key).update("result", src)
    return responce

@app.api_route("/api/imageDegrader", methods=all_methods)
def read_root(data: ImgEnhance, request: Request):
    security_pass = Middleware.security(
        method = request.method,
        allow_method = ["GET", "POST"],
        path = request.url.path,
        key = data.key
    )
    if security_pass != None:
        return security_pass
    src = TaskMaster.enhance_img(['degrade', data.img, data.quality])
    if src == 19:
        return customException.processException(request.url.path, data)
    single_img_bin.clear()
    responce = Responce.model(data.key).update("result", src)
    return responce

class ImgCompress(BaseModel):
    img: str
    height: int | None
    width: int | None
    quality: int | None
    load: str | None
    key: str | None

@app.api_route("/api/imageCompressor", methods=all_methods)
def read_root(data: ImgCompress, request: Request):
    if not Authentication.isValidAccess(data.key):
        return customException.accessException(request.url.path, data.key)
    if request.method not in ["GET", "POST"]:
        return customException.methodException(request.url.path, request.method)
    if(data.load=='true' and single_img_bin!=[]):
        src = TaskMaster.compress_img(['load', data.quality, data.width, data.height], data.key)
    else:
        media = data.img
        src = TaskMaster.compress_img([media, data.quality, data.width, data.height], data.key)
    if src == None or src*0 == 0:
        ext = Tools.find_extension(media if data.load!='true' else Tools.merge_list_to_string(single_img_bin))
        if src == None or src == 1:
            return customException.unsupportException(request.url.path, ext)
        if src == 19:
            return customException.convertationException(request.url.path, ext)
    single_img_bin.clear()
    src = Responce.compress_reponce(src)
    responce = Responce.model(data.key).update("result", src)
    return responce

@app.get("/key_exchange")
def read_root():
    prime = Middleware.generateSmallPrime()
    return prime

@app.get("/set_key")
def read_root(token):
    Middleware.key = token
    return {"ack": 0, "time": Tools.timeStamp()}

@app.get("/test")
def read_root(a, b):
    result = sum(int(a), int(b))
    return {"sum": result, "time": Tools.timeStamp()}

@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"], include_in_schema=False)
async def catch_all(request: Request, full_path: str):
    return customException.notFoundException(full_path, request.method)