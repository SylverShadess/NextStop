from flask import jsonify, session
from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity, verify_jwt_in_request, current_user

from App.models import User

def jwt_authenticate(username, password):
    """
    Authenticate username and password using JWT
    """
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity=username)
        return access_token
    return None

def authenticate(username, password):
    """
    Check user authentication by comparing username and password
    """
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return user
    return None

def identity(payload):
    """
    Get user identity from JWT payload
    """
    return User.query.filter_by(username=payload['identity']).first()

def login_user(username, password):
    """
    Login a user with username and password
    """
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity=username)
        return access_token
    return None

def setup_jwt(app):
    """
    Setup JWT callbacks
    """
    jwt = JWTManager(app)
    
    @jwt.user_identity_loader
    def user_identity_lookup(identity):
        return identity
    
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return User.query.filter_by(username=identity).first()
    
    @jwt.additional_claims_loader
    def add_claims_to_access_token(identity):
        user = User.query.filter_by(username=identity).first()
        if user:
            return {
                'username': user.username,
                'user_id': user.id
            }
        return {}
        
    return jwt

def get_users():
    """
    Get all users
    """
    return User.query.all()

def get_by_username(username):
    """
    Get user by username
    """
    return User.query.filter_by(username=username).first()

def register_user(username, password, email=None):
    """
    Register a new user
    """
    # Check if username already exists
    if User.query.filter_by(username=username).first():
        return None
    
    # Check if email already exists (if provided)
    if email and User.query.filter_by(email=email).first():
        return None
    
    # Create new user
    user = User(username, password, email)
    from App.database import db
    db.session.add(user)
    db.session.commit()
    return user

def confirm_user_account(username, code):
    """
    Confirm a user account with a verification code
    """
    user = User.query.filter_by(username=username).first()
    if user:
        # In a real app, you'd verify the code
        # For demo, we'll just set verified to True
        user.verified = True
        from App.database import db
        db.session.commit()
        return True
    return False

def delete_user(username):
    """
    Delete a user by username
    """
    user = User.query.filter_by(username=username).first()
    if user:
        from App.database import db
        db.session.delete(user)
        db.session.commit()
        return True
    return False

# Context processor to make 'is_authenticated' available to all templates
def add_auth_context(app):
  @app.context_processor
  def inject_user():
      try:
          verify_jwt_in_request(optional=True)
          username = get_jwt_identity()
          if username:
              current_user = User.query.filter_by(username=username).first()
              is_authenticated = True if current_user else False
          else:
              current_user = None
              is_authenticated = False
      except Exception as e:
          print(f"Auth context error: {e}")
          is_authenticated = False
          current_user = None
      return dict(is_authenticated=is_authenticated, current_user=current_user)