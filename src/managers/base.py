from abc import abstractmethod
from contextlib import suppress
from logging import getLogger
from pathlib import Path
from typing import Any
from uuid import UUID

import aiofiles
from aiofiles.threadpool.binary import AsyncBufferedIOBase
from pydantic import ValidationError
from starlette.websockets import WebSocket, WebSocketDisconnect

from api.schemas import UploadData
from core.config.defaults import DEFAULTS
from enums import FileAction, WebSocketStatus
from validators import BaseFileValidator

from .websocket import WebSocketManager

logger = getLogger("uvicorn.error")


class BaseFileManager:

    base_dir = DEFAULTS.BASE_DIR
    validator = BaseFileValidator()

    __slots__ = (
        "ws",
        "ws_manager",
        "action",
        "user_id",
        "session_id",
        "file_idx",
        "file_name",
        "file_hash",
        "file_dir",
        "file_path",
    )

    def __init__(self, websocket: WebSocket) -> None:
        self.ws_manager = WebSocketManager(websocket)
        self.ws = websocket

        self.file_dir: Path = Path()
        self.file_path: Path = Path()

        self.file_idx: int = 0
        self.file_name: str = "default"
        self.file_hash: Any | None = None

        self.user_id: UUID | None = None
        self.session_id: UUID | None = None

        self.action: FileAction | str = FileAction.UPLOAD

    async def handle_action(self) -> None:
        """Processes received actions (upload/delete)."""
        while True:
            try:
                data = await self.ws.receive_json()
                validated_data = UploadData(**data)

                for key, value in validated_data:
                    setattr(self, key, value)

                await self.generate_file_path()
                await getattr(self, f"perform_{self.action}")()

            except (ValidationError, ValueError) as e:
                logger.debug(f"Validation error: {e}")
                await self.ws_manager.send_abort(str(e))
                await self.delete_file()

            except WebSocketDisconnect:
                self.ws_manager.timeout_task.cancel()
                if self.ws_manager.state == WebSocketStatus.UPLOADING:
                    logger.debug("Websocket disconnected. File state: uploading. Deleting the file...")
                    await self.delete_file()
                break

            except Exception as e:
                logger.exception(
                    f"[Action: '{self.action}'] | "
                    f"[file_name: {self.file_name}] | "
                    f"[user_id: {self.user_id}] | "
                    f"[session_id: {self.session_id}]"
                )
                self.ws_manager.timeout_task.cancel()
                with suppress(RuntimeError):
                    await self.ws.close(reason=str(e))
                break

    async def generate_file_path(self) -> Path:
        """Generate a path to save files based on user and session."""
        self.file_dir = self.base_dir / str(self.user_id) / str(self.session_id) / "original"
        self.file_dir.mkdir(parents=True, exist_ok=True)
        self.file_path = self.file_dir / self.file_name
        return self.file_path

    async def perform_upload(self) -> None:
        """Processes file upload."""
        await self.ws_manager.send_ready()

        if not await self.save_file():
            return

        await self.validate_file()
        await self.rename_file()

        await self.ws_manager.send_success_upload(self.file_path.name)

    async def perform_delete(self) -> None:
        """Processes file deletion."""
        await self.delete_file()
        await self.ws_manager.send_success_delete(self.file_path.name)

    async def save_file(self) -> AsyncBufferedIOBase | None:
        """Saves file, checks format and size, sends progress."""
        current_file_size = 0

        async with aiofiles.open(self.file_path, "wb") as output_file:
            while True:
                # Receiving chunk from a client
                chunk = await self.ws.receive_bytes()

                if chunk == b"EOF":
                    break

                # Check a first chunk format
                if current_file_size == 0:
                    self.validator.validate_header(chunk[:12])

                # Check file size
                current_file_size += len(chunk)
                self.validator.check_size_limits(current_file_size)

                # Sending upload progress
                await self.ws_manager.send_progress(current_file_size, self.validator.max_size_bytes)

                # Saving chunk
                await output_file.write(chunk)

        return output_file

    async def delete_file(self) -> None:
        """Deletes the file"""
        if not self.file_path.is_file():
            return

        self.file_path.unlink(missing_ok=True)
        await self.cleanup_dirs()

    @abstractmethod
    async def validate_file(self) -> None:
        """Checks if the file is valid."""
        raise NotImplementedError("Subclasses must implement this method.")

    async def rename_file(self) -> Path:
        """Renames the file."""
        self.file_name = f"{self.file_idx}_{self.file_hash}{self.file_path.suffix}"
        new_path = self.file_path.with_name(self.file_name)

        self.file_path.rename(new_path)
        self.file_path = new_path

        return new_path

    async def cleanup_dirs(self) -> None:
        """Cleans up the directories if they are empty."""
        if not any(self.file_dir.iterdir()):  # files dir
            self.file_dir.rmdir()

        if not any(self.file_dir.parent.iterdir()):  # session dir
            self.file_dir.parent.rmdir()

        if not any(self.file_dir.parent.parent.iterdir()):  # user dir
            self.file_dir.parent.parent.rmdir()
