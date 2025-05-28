from fastapi import APIRouter, WebSocket

router = APIRouter()


@router.websocket("/upload")
async def image_upload_handler(ws: WebSocket) -> None:
    """WebSocket image upload handler."""
    pass
