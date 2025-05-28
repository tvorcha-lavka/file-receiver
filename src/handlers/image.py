from starlette.websockets import WebSocket

from managers import ImageFileManager


class ImageFileHandler:

    __slots__ = ("manager", "ws")

    def __init__(self, ws: WebSocket) -> None:
        self.manager = ImageFileManager(ws)
        self.ws = ws

    async def accept(self) -> None:
        await self.ws.accept()
        await self.manager.handle_action()
