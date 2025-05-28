from imagehash import ImageHash, dhash
from PIL import Image

from core.config.image import image_settings
from validators import ImageFileValidator

from .base import BaseFileManager


class ImageFileManager(BaseFileManager):

    base_dir = image_settings.BASE_DIR
    validator = ImageFileValidator()

    async def generate_image_hash(self) -> ImageHash:
        """Generates a hash for the file."""
        return dhash(Image.open(self.file_path))

    async def validate_file(self) -> None:
        """Checks if the file is valid."""
        # Check if the file is an image_uploader
        await self.validator.validate_image(self.file_path)

        # Check if the file is unique
        self.file_hash = await self.generate_image_hash()
        await self.validator.validate_unique(self.file_path, self.file_idx, self.file_hash)

        # Check upload limits
        self.validator.check_upload_limits(self.file_dir)
