from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from Preprocessor import Authentication, customException, Responce, TaskMaster, Tools, sum, Middleware
from fastapi.responses import HTMLResponse

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
def read_root(number: list[str] = Query(...)):
    return {"result": number, "time": Tools.timeStamp()}

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
