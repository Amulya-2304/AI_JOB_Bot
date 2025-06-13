from app.db import db

class SavedJob(db.Model):
    """Database model to store jobs saved by users."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200))
    link = db.Column(db.String(500))
    description = db.Column(db.Text)

    user = db.relationship('User', backref=db.backref('saved_jobs', lazy=True))