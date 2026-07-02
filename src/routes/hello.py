from fastapi import APIRouter
from fastapi.responses import JSONResponse


router = APIRouter()

@router.get('/')
async def say_hello():
    return JSONResponse({'message': 'Hello!'})