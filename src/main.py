import logging.config

from fastapi import FastAPI

from api.routers import main_router
from core.config.log import LOGGING

logging.config.dictConfig(LOGGING)

app = FastAPI()
app.include_router(main_router)
