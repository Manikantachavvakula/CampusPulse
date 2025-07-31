from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    roll_number = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='student')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Nullable for anonymous
    facility = db.Column(db.String(50), nullable=False)  # Canteen, Library, etc.
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    review = db.Column(db.Text)  # Optional review comment
    is_anonymous = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('ratings', lazy=True))

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Nullable for anonymous
    category = db.Column(db.String(50), nullable=False)
    days = db.Column(db.String(200))  # For food feedback days
    quality = db.Column(db.String(20))  # For food quality
    rating = db.Column(db.Integer)
    comments = db.Column(db.Text)
    image_path = db.Column(db.String(200))
    status = db.Column(db.String(20), default='pending')
    is_anonymous = db.Column(db.Boolean, default=False)
    admin_response = db.Column(db.Text)  # Admin resolution comment
    resolved_by = db.Column(db.Integer, db.ForeignKey('user.id'))  # Admin who resolved
    resolved_at = db.Column(db.DateTime)  # When it was resolved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('feedbacks', lazy=True))
    resolver = db.relationship('User', foreign_keys=[resolved_by], backref='resolved_feedbacks')