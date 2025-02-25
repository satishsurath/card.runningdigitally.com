from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<User {self.email}>'

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()

def get_or_create_user(email):
    user = User.query.filter_by(email=email).first()
    if user:
        user.last_login = datetime.utcnow()
    else:
        user = User(email=email)
        db.session.add(user)
    db.session.commit()
    return user