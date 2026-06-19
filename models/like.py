from datetime import datetime
from . import db


class Like(db.Model):
    __tablename__ = 'likes'

    id: int = db.Column(db.Integer, primary_key=True)
    user_id: int = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    post_id: int = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    created_at: datetime = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='uq_user_post_like'),)

    user = db.relationship('User', backref='likes')
