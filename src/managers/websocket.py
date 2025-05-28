from asyncio import create_task, sleep
from contextlib import suppress
from functools import wraps
from time import time
from typing import Any, Callable, TypeVar

from starlette.exceptions import WebSocketException
from starlette.websockets import WebSocket

from api.schemas import ProgressStatus
from core.config.websocket import websocket_settings
from enums import WebSocketStatus, WebSocketStatusMessage

T = TypeVar("T", bound=Callable[..., Any])


class WebSocketManager:

    status = WebSocketStatus
    status_msg = WebSocketStatusMessage
    settings = websocket_settings

    __slots__ = (
        "_ws",
        "state",
        "last_activity_time",
        "timeout_task",
    )

    def __init__(self, websocket: WebSocket):
        self._ws = websocket
        self.state = self.status.READY
        self.last_activity_time = time()
        self.timeout_task = create_task(self._set_timeout())

    @staticmethod
    def last_activity(func: T) -> T:
        @wraps(func)
        async def wrapper(self: "WebSocketManager", *args: Any, **kwargs: Any) -> Any:
            self.last_activity_time = time()
            return await func(self, *args, **kwargs)

        return wrapper  # type: ignore

    @last_activity
    async def send_ready(self) -> None:
        """Sending a ready message."""
        data = ProgressStatus(
            status=self.status.READY,
            message=self.status_msg.READY,
            progress=0,
        )
        await self._ws.send_json(data)
        self.state = self.status.READY

    @last_activity
    async def send_progress(self, current_size: int, max_size: int) -> None:
        """Sending the progress of the file upload."""
        data = ProgressStatus(
            status=self.status.UPLOADING,
            message=self.status_msg.UPLOADING,
            progress=min(100, round(current_size / max_size * 100)),
        )
        await self._ws.send_json(data)
        self.state = self.status.UPLOADING

    @last_activity
    async def send_success_upload(self, file_name: str) -> None:
        """Sending a success upload file message."""
        data = ProgressStatus(
            status=self.status.SUCCESS,
            message=self.status_msg.SUCCESS_UPLOAD,
            file_name=file_name,
            progress=100,
        )
        await self._ws.send_json(data)
        self.state = self.status.SUCCESS

    @last_activity
    async def send_success_delete(self, file_name: str) -> None:
        """Sending a success delete file message."""
        data = ProgressStatus(
            status=self.status.SUCCESS,
            message=self.status_msg.SUCCESS_DELETE,
            file_name=file_name,
        )
        await self._ws.send_json(data)
        self.state = self.status.SUCCESS

    @last_activity
    async def send_error(self, reason: str | None = None) -> None:
        """Sending an error message."""
        data = ProgressStatus(
            status=self.status.ERROR,
            message=reason if reason else self.status_msg.ERROR,
        )
        await self._ws.send_json(data)
        self.state = self.status.ERROR

    @last_activity
    async def send_abort(self, reason: str | None = None) -> None:
        """Aborts the file upload with deletion."""
        data = ProgressStatus(
            status=self.status.ABORT,
            message=reason if reason else self.status_msg.ABORT,
        )
        await self._ws.send_json(data)
        self.state = self.status.ABORT

    async def disconnect_by_timeout(self) -> None:
        """Disconnects the client by timeout."""
        self.timeout_task.cancel()
        with suppress(WebSocketException, RuntimeError):
            data = ProgressStatus(
                status=self.status.TIMEOUT,
                message=self.status_msg.TIMEOUT,
            )
            await self._ws.send_json(data)
            await self._ws.close()

    async def _set_timeout(self) -> None:
        """Check for inactivity and close the connection after a timeout"""
        while True:
            await sleep(self.settings.DELAY)
            elapsed_time = round(time() - self.last_activity_time)

            if elapsed_time >= self.settings.TIMEOUT:
                await self.disconnect_by_timeout()
                break
