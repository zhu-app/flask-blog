from . import db


class Category(db.Model):
    __tablename__ = 'categories'

    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(50), unique=True, nullable=False)

    posts = db.relationship('Post', backref='category', lazy=True)

    def to_dict(self) -> dict:
        return {'id': self.id, 'name': self.name}
