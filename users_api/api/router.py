from fastapi import APIRouter

class UsersRouter(APIRouter):
    """users router"""
    def __init__(self) -> None:
        super().__init__()
