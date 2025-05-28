from fastapi import APIRouter

from .routes import receiver

main_router = APIRouter()

main_router.include_router(receiver.router, prefix="/image", tags=["Image Receiver"])
