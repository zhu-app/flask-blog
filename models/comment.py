from datetime import datetime, timezone
from . import db


class Comment(db.Model):
    __tablename__ = 'comments'

    id: int = db.Column(db.Integer, primary_key=True)
    content: str = db.Column(db.Text, nullable=False)
    created_at: datetime = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    post_id: int = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False, index=True)
    user_id: int = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status: str = db.Column(db.String(20), default='approved', nullable=False, index=True)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'content': self.content,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'status': self.status,
            'user': self.author.to_dict() if self.author else None
        }
