from flask import Blueprint, request, jsonify, redirect, url_for
from app.db import db
from app.models.user import User

"""Blueprint for user-related routes"""
user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/', methods=['POST'])
def create_user():
    """Create a new user"""
    name = request.form.get('name') or request.json.get('name')
    email = request.form.get('email') or request.json.get('email')

    user = User(name=name, email=email)
    db.session.add(user)
    db.session.commit()

    if request.form:
        return redirect(url_for('user_page'))
    return jsonify({'id': user.id, 'name': user.name, 'email': user.email}), 201


@user_bp.route('/<int:user_id>', methods=['POST'])
def modify_user(user_id):
    """Handle edit or delete from HTML form"""

    method = request.form.get('_method', '').upper()

    user = User.query.get_or_404(user_id)

    if method == 'PUT':
        user.name = request.form['name']
        user.email = request.form['email']
        db.session.commit()
        return redirect(url_for('user_page'))

    elif method == 'DELETE':
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('user_page'))

    return jsonify({'error': 'Unsupported method'}), 405


@user_bp.route('/', methods=['GET'])
def get_all_users():
    """Retrieve all users"""
    users = User.query.all()
    return jsonify([
        {'id': u.id, 'name': u.username, 'email': u.email} for u in users
    ])