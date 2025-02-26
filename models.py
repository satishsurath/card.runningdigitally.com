from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    linkedin_id = db.Column(db.String(120), unique=True, nullable=True)
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    profile_picture = db.Column(db.String(500), nullable=True)
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
            'full_name': self.full_name or f"{self.first_name} {self.last_name}".strip(),
            'phone': self.phone,
            'title': self.title,
            'company': self.company,
            'website': self.website,
            'address': self.address,
            'notes': self.notes,
            'profile_picture': self.profile_picture
        }

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()

def get_or_create_user(email, linkedin_id=None, first_name=None, last_name=None, profile_picture=None):
    user = User.query.filter_by(email=email).first()
    if user:
        user.last_login = datetime.utcnow()
        # Update LinkedIn info if provided
        if linkedin_id:
            user.linkedin_id = linkedin_id
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if profile_picture:
            user.profile_picture = profile_picture
    else:
        user = User(
            email=email,
            linkedin_id=linkedin_id,
            first_name=first_name,
            last_name=last_name,
            profile_picture=profile_picture
        )
        db.session.add(user)
    db.session.commit()
    return user