from enum import StrEnum


class WebSocketStatus(StrEnum):
    READY = "ready"
    UPLOADING = "uploading"
    SUCCESS = "success"
    TIMEOUT = "timeout"
    ABORT = "abort"
    ERROR = "error"


class WebSocketStatusMessage(StrEnum):
    READY = "Ready to upload"
    UPLOADING = "Uploading..."
    SUCCESS_UPLOAD = "Upload successful"
    SUCCESS_DELETE = "File deleted"
    TIMEOUT = "Connection timed out"
    ERROR = "Something went wrong"
    ABORT = "File upload aborted"
