import re
from pathlib import Path

from imagehash import ImageHash, hex_to_hash
from PIL import Image, UnidentifiedImageError
from pillow_heif import register_heif_opener  # type: ignore

from core.config.image import image_settings

from .base import BaseFileValidator

register_heif_opener()


class ImageFileValidator(BaseFileValidator):

    allowed_formats = image_settings.ALLOWED_FORMATS
    max_files = image_settings.MAX_FILE_COUNT
    max_size = image_settings.MAX_FILE_SIZE

    @staticmethod
    def is_heic(chunk: bytes) -> bool:
        sequence = (b"heic", b"heix", b"heim", b"heis", b"hevc", b"hevx", b"hevm", b"hevs")
        return chunk[4:8] == b"ftyp" and chunk[8:12] in sequence

    @staticmethod
    def is_heif(chunk: bytes) -> bool:
        sequence = (b"mif1", b"msf1")
        return chunk[4:8] == b"ftyp" and chunk[8:12] in sequence

    @staticmethod
    def is_jpeg(chunk: bytes) -> bool:
        return chunk.startswith(b"\xff\xd8") or chunk[6:10] in (b"JFIF", b"Exif")

    @staticmethod
    def is_png(chunk: bytes) -> bool:
        return chunk.startswith(b"\x89PNG\r\n\x1a\n")

    @staticmethod
    def is_webp(chunk: bytes) -> bool:
        return chunk.startswith(b"RIFF") and chunk[8:12] == b"WEBP"

    async def validate_image(self, file_path: Path | str) -> None:
        """Checks if the file is an image_uploader."""
        try:
            with Image.open(file_path) as img:
                img.verify()
        except (UnidentifiedImageError, OSError):
            raise ValueError(self.status_msg.INVALID_FILE_FORMAT)

    async def validate_unique(self, file_path: Path, file_idx: int, file_hash: ImageHash) -> None:
        """Checks if the file is unique."""
        data = [
            (int(match.group(1)), match.group(2))
            for file in file_path.parent.iterdir()
            if (match := re.match(r"^(\d+)_([^.]+)", file.name)) and file != file_path
        ]

        if not all(i == file_idx or file_hash - hex_to_hash(h) >= 10 for i, h in data):
            raise ValueError(self.status_msg.UNIQUE_FILE)
