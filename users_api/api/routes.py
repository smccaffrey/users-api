from users_api.api.router import UsersRouter

from users_api.api.users import users_router
from users_api.api.posts import posts_router


root_router = UsersRouter()


@root_router.get("/health")
@root_router.get("/")
def health_check() -> int:
    return 200


root_router.include_router(users_router, prefix="/users")
root_router.include_router(posts_router, prefix="/posts")
