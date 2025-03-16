import logging.config

from fastapi import FastAPI

from core.config.log import LOGGING

logging.config.dictConfig(LOGGING)

app = FastAPI()
