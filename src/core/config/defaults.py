from pathlib import Path

from pydantic.v1 import BaseSettings


class DefaultSettings(BaseSettings):
    ALLOWED_FORMATS: tuple | str = "*"

    BASE_DIR: Path = Path("/") / "mnt" / "efs"
    BYTES: int = 1024 * 1024

    MAX_FILE_COUNT: int = 0
    MAX_FILE_SIZE: int = 0


DEFAULTS = DefaultSettings()
