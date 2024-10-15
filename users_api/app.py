from fastapi import FastAPI

from users_api.app_factory import get_app

app: FastAPI = get_app()