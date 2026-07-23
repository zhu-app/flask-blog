from datetime import datetime, timezone
from sqlalchemy import func
from . import db


post_tags = db.Table(
    'post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True),
)


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
    status: str = db.Column(db.String(20), default='published', nullable=False, index=True)
    cover_image: str = db.Column(db.String(255), nullable=True)
    seo_description: str = db.Column(db.String(255), nullable=True)

    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')
    liked_by = db.relationship('Like', backref='post', lazy=True, cascade='all, delete-orphan')
    tags = db.relationship('Tag', secondary=post_tags, back_populates='posts', lazy='selectin')

    @property
    def comment_count(self) -> int:
        from .comment import Comment
        return db.session.query(func.count(Comment.id)).filter(
            Comment.post_id == self.id,
            Comment.status == 'approved'
        ).scalar() or 0

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
            'status': self.status,
            'cover_image': self.cover_image,
            'seo_description': self.seo_description,
            'tags': [tag.to_dict() for tag in self.tags],
            'views': self.views,
            'likes': self.likes,
            'likes_count': self.likes_count,
            'comment_count': self.comment_count
        }
