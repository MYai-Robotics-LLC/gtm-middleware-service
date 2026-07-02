from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from .routes.hello import router as hello_router
from .routes.livekit import router as livekit_router
from starlette.responses import JSONResponse
from .services.logging  import build_logger

import os

load_dotenv()

logger = build_logger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, skip = None, dispatch = None):
        super().__init__(app, dispatch)
        self._skip = skip
        
    def _should_skip(self, url: str):
        if self._skip is None:
            return False
        if isinstance(self._skip, list) or isinstance(self._skip, set):
            return url in self._skip
        if callable(self._skip):
            return self._skip(url)


        return self._skip == url

    async def dispatch(self, request, call_next):
        if "OPTIONS" == request.method.upper() or self._should_skip(request.url.path):
            return await call_next(request)

        expected_key = os.getenv('SERVICE_API_KEY')
        if not expected_key:
            logger.error('SERVICE_API_KEY is not configured')
            return JSONResponse({'error': 'Invalid request'}, status_code=401)

        key = request.query_params.get('key')
        if key == expected_key:
            return await call_next(request)

        key = request.headers.get('x-api-key', request.headers.get('x-api-token', 'x'))
        if key == expected_key:
            return await call_next(request)


        key = (request.headers.get('authorization') or 'x y').split(' ')[-1]
        if key == expected_key:
            return await call_next(request)


        logger.error('Invalid api key')

        return JSONResponse({'error': 'Invalid request'}, status_code=401)


app = FastAPI()

app.add_middleware(
    AuthMiddleware,
    skip=["/", "/docs", "/redoc", "/openapi.json"],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=False,
    allow_methods=["GET", "PUT", "POST", "PATCH", "OPTIONS", "HEAD"],
    allow_headers=["Authorization", "Content-Type", "X-Api-Key", "X-Api-Token", "Accept", "X-Requested-With","Access-Control-Allow-Origin"],
)

app.include_router(hello_router)
app.include_router(livekit_router)

