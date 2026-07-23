from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .category import Category
from .post import Post
from .tag import Tag
from .comment import Comment
from .like import Like

__all__ = ['db', 'User', 'Category', 'Post', 'Tag', 'Comment', 'Like']
