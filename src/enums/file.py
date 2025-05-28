from enum import StrEnum


class FileAction(StrEnum):
    UPLOAD = "upload"
    DELETE = "delete"


class FileStatusMessage(StrEnum):
    FILE_CORRUPTED = "File is corrupted"
    UNIQUE_FILE = "Duplicate file detected"
    UPLOAD_LIMIT_EXCEEDED = "Upload limit exceeded"
    FILE_SIZE_EXCEEDED = "File size exceeded"
    INVALID_FILE_FORMAT = "Invalid file format"
