from datetime import datetime, timezone
from secrets import token_urlsafe
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
from . import db


class User(db.Model):
    __tablename__ = 'users'

    id: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email: str = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash: str = db.Column(db.String(256), nullable=False)
    created_at: datetime = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    role: str = db.Column(db.String(20), default='user', index=True)
    avatar_url: str = db.Column(db.String(255), nullable=True)
    reset_token: str = db.Column(db.String(128), unique=True, nullable=True, index=True)
    reset_token_expires_at: datetime = db.Column(db.DateTime, nullable=True)

    posts = db.relationship('Post', backref='author', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def create_reset_token(self) -> str:
        from datetime import timedelta
        self.reset_token = token_urlsafe(32)
        self.reset_token_expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        return self.reset_token

    def clear_reset_token(self) -> None:
        self.reset_token = None
        self.reset_token_expires_at = None

    def reset_token_is_valid(self, token: str) -> bool:
        if not self.reset_token or self.reset_token != token or not self.reset_token_expires_at:
            return False
        expires_at = self.reset_token_expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        return expires_at > datetime.now(timezone.utc)

    @property
    def post_count(self) -> int:
        from .post import Post
        return db.session.query(func.count(Post.id)).filter(Post.user_id == self.id).scalar() or 0

    @property
    def comment_count(self) -> int:
        from .comment import Comment
        return db.session.query(func.count(Comment.id)).filter(Comment.user_id == self.id).scalar() or 0

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'avatar_url': self.avatar_url,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'post_count': self.post_count
        }
