from . import db
from .post import post_tags


class Tag(db.Model):
    __tablename__ = 'tags'

    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(40), unique=True, nullable=False, index=True)

    posts = db.relationship('Post', secondary=post_tags, back_populates='tags', lazy='selectin')

    def to_dict(self) -> dict:
        return {'id': self.id, 'name': self.name}
