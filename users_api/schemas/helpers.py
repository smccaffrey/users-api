from users_api.models.orm.posts import PostsORM
from users_api.models.posts import Post
from users_api.models.users import User


def post_response(post: PostsORM) -> Post:
    return Post.model_validate(
        {
            **post.__dict__,
            "user": User.model_validate(post.users[0])
        }
    )