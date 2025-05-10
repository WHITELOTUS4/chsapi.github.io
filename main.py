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

class ImgLoader(BaseModel):
    img: str
    limit: int
    index: int
    key: str | None

@app.api_route("/load/single", methods=all_methods)
def read_root(data: ImgLoader, request: Request):
    if not Authentication.isValidAccess(data.key):
        return customException.accessException(request.url.path, data.key)
    if request.method not in ["GET", "POST", "SET"]:
        return customException.methodException(request.url.path, request.method)
    if(data.index <= data.limit and data.index > 0):
        single_img_bin.append(data.img)
        return {"ack": data.index, "time": Tools.timeStamp()}
    else:
        print("image index out of range")

class ImgConverter(BaseModel):
    form: str
    img: str
    load: str | None
    key: str | None

@app.api_route("/api/imageConverter", methods=all_methods)
def read_root(data: ImgConverter, request: Request):
    limit = len(single_img_bin)
    if not Authentication.isValidAccess(data.key):
        return customException.accessException(request.url.path, data.key)
    if request.method not in ["GET", "POST"]:
        return customException.methodException(request.url.path, request.method)
    if(data.load=='true' and single_img_bin!=[]):
        src = TaskMaster.convert_img(['load', data.form])
    else:
        img = data.img
        src = TaskMaster.convert_img([img, data.form])
    if src == None or src == 1:
        return customException.unsupportException(request.url.path, data.form)
    if src == 17:
        return customException.convertationException(request.url.path, data.form)
    responce = Responce.model(data.key).update("result", src)
    return responce

class DfdDetector(BaseModel):
    ext: str
    media: str
    heatmap: str | None
    load: str | None
    key: str | None

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
    responce = Responce.model(data.key).update("result", src)
    return responce

class ImgEnhance(BaseModel):
    img: str
    brightness: float | None
    contrast: float | None
    sharpness: float | None
    quality: int | None
    key: str | None

@app.api_route("/api/imageEnhancer", methods=all_methods)
def read_root(data: ImgEnhance, request: Request):
    security_pass = Middleware.security(
        method = request.method,
        allow_method = ["GET", "POST"],
        path = request.url.path,
        key = data.key
    )
    if security_pass != None:
        return security_pass
    src = TaskMaster.enhance_img(['enhance', data.img, data.brightness, data.contrast, data.sharpness])
    if src == 19:
        return customException.processException(request.url.path, data)
    responce = Responce.model(data.key).update("result", src)
    return responce
    # chunk_size = sys.getsizeof(str(responce))/1024
    # chunk_no = round(chunk_size / 900) + 2
    # part_length = int(len(responce) / chunk_no)+1
    # return [limit, chunk_size, chunk_no, part_length]
    # if(limit >= 6 and data.load=='true'):
    #     responce = (Responce.send_parts_with_ack(str(responce), limit))
    # return responce

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
    responce = Responce.model(data.key).update("result", src)
    return responce

class ImgCompress(BaseModel):
    img: str
    height: int | None
    width: int | None
    quality: int | None
    key: str | None

@app.api_route("/api/imageCompressor", methods=all_methods)
def read_root(data: ImgCompress, request: Request):
    security_pass = Middleware.security(
        method = request.method,
        allow_method = ["GET", "POST"],
        path = request.url.path,
        key = data.key
    )
    if security_pass != None:
        return security_pass
    src = TaskMaster.compress_img([data.img, data.width, data.height, data.quality])
    if src == 19:
        return customException.processException(request.url.path, data)
    responce = Responce.model(data.key).update("result", src)
    return responce

@app.get("/test")
def read_root(a, b):
    result = sum(int(a), int(b))
    return {"sum": result, "time": Tools.timeStamp()}

@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"], include_in_schema=False)
async def catch_all(request: Request, full_path: str):
    return customException.notFoundException(full_path, request.method)