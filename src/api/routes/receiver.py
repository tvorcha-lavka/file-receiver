from fastapi import APIRouter, WebSocket

from handlers import ImageFileHandler

router = APIRouter()


@router.websocket("/upload")
async def image_upload_handler(ws: WebSocket) -> None:
    """WebSocket image upload handler."""
    handler = ImageFileHandler(ws)
    await handler.accept()
