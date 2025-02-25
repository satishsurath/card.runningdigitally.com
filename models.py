from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    # VCF card metadata
    full_name = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    title = db.Column(db.String(200))
    company = db.Column(db.String(200))
    website = db.Column(db.String(200))
    address = db.Column(db.Text)
    notes = db.Column(db.Text)

    def __repr__(self):
        return f'<User {self.email}>'

    def to_dict(self):
        return {
            'email': self.email,
            'full_name': self.full_name,
            'phone': self.phone,
            'title': self.title,
            'company': self.company,
            'website': self.website,
            'address': self.address,
            'notes': self.notes
        }

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