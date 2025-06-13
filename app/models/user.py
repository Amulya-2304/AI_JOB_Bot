from app.db import db

class User(db.Model):
    """User model for storing user information and uploaded CV."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    cv_filename = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        """Return a string representation of the user."""
        return f"<User {self.username}>"