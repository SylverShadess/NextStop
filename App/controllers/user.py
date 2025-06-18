from App.models import User
from App.database import db
from flask_jwt_extended import create_access_token
from flask import session

def create_user(username, password):
    newuser = User(username=username, password=password)
    db.session.add(newuser)
    db.session.commit()
    return newuser

def get_user_by_username(username):
    return User.query.filter_by(username=username).first()

def get_user(id):
    return User.query.filter_by(id=id).first()

def get_all_users():
    return User.query.all()

def get_all_users_json():
    users = User.query.all()
    if not users:
        return []
    users = [user.get_json() for user in users]
    return users

def update_user(id, username):
    user = get_user(id)
    if user:
        user.username = username
        db.session.add(user)
        db.session.commit()
        return user
    return None

def authenticate(username, password):
    """
    Check user authentication by comparing username and password
    """
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        # Store authenticated user info in session
        session['is_authenticated'] = True
        session['username'] = user.username
        session['user_id'] = user.id
        return user
    return None

def login(username, password):
    """
    Generate JWT token for authenticated user
    """
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        # Create access token with username as identity
        access_token = create_access_token(identity=username)
        return access_token
    return None
    