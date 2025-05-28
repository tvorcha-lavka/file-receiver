from typing import TypedDict
from uuid import UUID

from pydantic import BaseModel

from enums import FileAction


class UploadData(BaseModel):
    action: FileAction
    file_idx: int
    file_name: str
    user_id: UUID
    session_id: UUID


class ProgressStatus(TypedDict, total=False):
    status: str
    progress: int
    message: str
    file_name: str
