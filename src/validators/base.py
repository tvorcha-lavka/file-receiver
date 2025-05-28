from pathlib import Path

from core.config.defaults import DEFAULTS
from enums import FileStatusMessage


class BaseFileValidator:

    allowed_formats = DEFAULTS.ALLOWED_FORMATS
    max_files = DEFAULTS.MAX_FILE_COUNT
    max_size = DEFAULTS.MAX_FILE_SIZE

    status_msg = FileStatusMessage

    @property
    def max_size_bytes(self) -> int:
        """Returns the maximum file size in bytes."""
        return self.max_size * DEFAULTS.BYTES

    def validate_header(self, data: bytes) -> None:
        """Checks if the first bytes of the file are valid."""
        if self.allowed_formats == "*":
            return

        if not any(getattr(self, f"is_{fmt}")(data) for fmt in self.allowed_formats):
            raise ValueError(self.status_msg.INVALID_FILE_FORMAT)

    def check_size_limits(self, current_size: int) -> None:
        """Checks if the file size has been exceeded."""
        if self.max_size_bytes != 0 and current_size > self.max_size_bytes:
            raise ValueError(self.status_msg.FILE_SIZE_EXCEEDED)

    def check_upload_limits(self, file_dir: Path) -> None:
        """Checks if the upload file limits have been exceeded."""
        if self.max_files != 0 and len(list(file_dir.iterdir())) > self.max_files:
            raise ValueError(self.status_msg.UPLOAD_LIMIT_EXCEEDED)
