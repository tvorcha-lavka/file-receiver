from typing import Any

from .defaults import DefaultSettings


class ImageSettings(DefaultSettings):
    ALLOWED_FORMATS: tuple | str = ("jpeg", "png", "webp", "heic", "heif")

    MAX_FILE_COUNT: int = 10
    MAX_FILE_SIZE: int = 5

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.BASE_DIR = self.BASE_DIR / "images"


image_settings = ImageSettings()
