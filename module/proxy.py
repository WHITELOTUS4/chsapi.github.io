from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.datastructures import MutableHeaders
from starlette.middleware.gzip import GZipMiddleware
import time, secrets, base64

ip_hits = {}
temp_blocked_ips = {}
blocked_ips = set([
    '100.110.116.83',
    '100.91.56.124',
    '100.117.194.70',
    '185.177.72.22'
])

MAX_USERS = 10000
TEMP_BLOCK_DURATION = 60
PERM_BLOCK_DURATION = 24 * 60 * 60

def set_block_cookie(response: Response, block_type: str):
    timestamp = str(int(time.time()))
    value = f"{block_type}{timestamp}"
    encoded = base64.b64encode(value.encode()).decode()
    max_age = PERM_BLOCK_DURATION if block_type == "blocked" else TEMP_BLOCK_DURATION
    response.set_cookie(
        key="blockState",
        value=encoded,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=max_age
    )

def is_client_blocked_by_cookie(cookie_value: str):
    if not cookie_value:
        return None
    try:
        decoded = base64.b64decode(cookie_value).decode()
        if decoded.startswith("blocked"):
            ts = int(decoded.replace("blocked", ""))
            if time.time() - ts < PERM_BLOCK_DURATION:
                return "blocked"
        elif decoded.startswith("temp"):
            ts = int(decoded.replace("temp", ""))
            if time.time() - ts < TEMP_BLOCK_DURATION:
                return "temp"
    except:
        return None
    return None

class SecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_ip = (
            request.headers.get("x-forwarded-for", "").split(",")[0].strip()
            or request.client.host
        )
        block_cookie = request.cookies.get("blockState")
        cookie_status = is_client_blocked_by_cookie(block_cookie)

        if client_ip in blocked_ips or cookie_status == "blocked":
            return Response(status_code=444)
        
        if client_ip in temp_blocked_ips or cookie_status == "temp":
            if time.time() - temp_blocked_ips.get(client_ip, 0) < TEMP_BLOCK_DURATION:
                response = JSONResponse(status_code=403, content={"detail": "Your IP is temporarily blocked due to excessive requests. Try again later."})
                set_block_cookie(response, "temp")
                return response
            else:
                temp_blocked_ips.pop(client_ip, None)
                ip_hits[client_ip] = 0

        if len(ip_hits) >= MAX_USERS and client_ip not in ip_hits:
            return JSONResponse(status_code=429, content={"detail": "Server is too busy now, Because to many user is present in the lobby. Please try again some time later or report us"})

        ip_hits[client_ip] = ip_hits.get(client_ip, 0) + 1
        if 100 < ip_hits[client_ip] < 200:
            temp_blocked_ips[client_ip] = time.time()
            ip_hits.pop(client_ip, None)
            response = JSONResponse(status_code=403, content={"detail": "Your IP has been temporarily blocked due to exceed the request limit. Please check our fair use policy."})
            set_block_cookie(response, "temp")
            return response
        elif ip_hits[client_ip] >= 200:
            blocked_ips.add(client_ip)
            temp_blocked_ips.pop(client_ip, None)
            ip_hits.pop(client_ip, None)
            response = JSONResponse(status_code=403, content={"detail": "Access denied, client ip is blocked due to past history of mal-practices!"})
            set_block_cookie(response, "blocked")
            return response

        nonce = secrets.token_urlsafe(16)
        request.state.nonce = nonce

        response = await call_next(request)
        headers = MutableHeaders(response.headers)
        headers["Content-Security-Policy"] = (
            f"default-src 'self'; "
            f"script-src 'self' https://cdnjs.cloudflare.com https://vercel.live https://vercel.com 'nonce-{nonce}'; "
            f"style-src 'self' 'unsafe-inline'; "
            f"font-src 'self' data:; "
            f"img-src 'self' data: https://avatars.githubusercontent.com https://vercel.com; "
            f"connect-src 'self' http://127.0.0.1:8000 http://127.0.0.1:5000 http://127.0.0.1:8080 https://chsweb.vercel.app https://chsapi.vercel.app https://chscdn.vercel.app wss://ws-us3.pusher.com https://ws-us3.pusher.com; "
            f"frame-src 'self' https://vercel.live;"
        )
        return response
    