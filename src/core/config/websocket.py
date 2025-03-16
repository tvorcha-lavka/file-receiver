from pydantic.v1 import BaseSettings


class WebsocketSettings(BaseSettings):
    TIMEOUT: int = 30
    DELAY: int = 10


websocket_settings = WebsocketSettings()
