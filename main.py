from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import Preprocessor
from Preprocessor import Authentication, customException, Responce, TaskMaster
import json
import logging

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

def timeStamp():
   return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

all_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]

@app.get("/")
def read_root():
    return {"Ahoy hoy": "Universe"}

@app.get("/api/")
def read_root(number: list[str] = Query(...)):
    return {"result": number, "time": timeStamp()}

class ImgConverter(BaseModel):
    form: str
    img: str
    key: str | None

@app.api_route("/api/imageConverter", methods=all_methods)
def read_root(data: ImgConverter, request: Request):
    if not Authentication.isValidAccess(data.key):
        return customException.accessException(request.url.path, data.key)
    if request.method not in ["GET", "POST"]:
        return customException.methodException(request.url.path, request.method)
    src = TaskMaster.convert_img([data.img, data.form])
    if src == None or src == 1:
        return customException.unsupportException(request.url.path, data.form)
    if src == 17:
        return customException.convertationException(request.url.path, data.form)
    responce = Responce.model(data.key).update("result", src)
    return responce

class ImgEnhance(BaseModel):
    img: str
    brightness: float | None
    contrast: float | None
    sharpness: float | None
    key: str | None

@app.api_route("/api/imageEnhancer", methods=all_methods)
def read_root(data: ImgEnhance, request: Request):
    if not Authentication.isValidAccess(data.key):
        return customException.accessException(request.url.path, data.key)
    if request.method not in ["GET", "POST"]:
        return customException.methodException(request.url.path, request.method)
    src = TaskMaster.enhance_img([data.img, data.brightness, data.contrast, data.sharpness])
    if src == 20:
        return customException.processException(request.url.path, data)
    responce = Responce.model(data.key).update("result", src)
    return responce

@app.get("/test")
def read_root(a, b):
    result = Preprocessor.sum(int(a), int(b))
    return {"sum": result, "time": timeStamp()}

@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"], include_in_schema=False)
async def catch_all(request: Request, full_path: str):
    return customException.notFoundException(full_path, request.method)
