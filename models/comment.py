from datetime import datetime
from . import db


class Comment(db.Model):
    __tablename__ = 'comments'

    id: int = db.Column(db.Integer, primary_key=True)
    content: str = db.Column(db.Text, nullable=False)
    created_at: datetime = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    post_id: int = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False, index=True)
    user_id: int = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'content': self.content,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'user': self.author.to_dict() if self.author else None
        }
