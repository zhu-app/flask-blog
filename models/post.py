from datetime import datetime, timezone
from sqlalchemy import func
from . import db


class Post(db.Model):
    __tablename__ = 'posts'

    id: int = db.Column(db.Integer, primary_key=True)
    title: str = db.Column(db.String(200), nullable=False, index=True)
    content: str = db.Column(db.Text, nullable=False)
    created_at: datetime = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at: datetime = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    user_id: int = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    category_id: int = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True, index=True)
    views: int = db.Column(db.Integer, default=0)
    likes: int = db.Column(db.Integer, default=0)

    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')
    liked_by = db.relationship('Like', backref='post', lazy=True, cascade='all, delete-orphan')

    @property
    def comment_count(self) -> int:
        from .comment import Comment
        return db.session.query(func.count(Comment.id)).filter(Comment.post_id == self.id).scalar() or 0

    @property
    def likes_count(self) -> int:
        from .like import Like
        return db.session.query(func.count(Like.id)).filter(Like.post_id == self.id).scalar() or 0

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'author': self.author.to_dict() if self.author else None,
            'category': self.category.to_dict() if self.category else None,
            'views': self.views,
            'likes': self.likes,
            'likes_count': self.likes_count,
            'comment_count': self.comment_count
        }
