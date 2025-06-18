from flask import Blueprint, render_template, jsonify, request, flash, send_from_directory, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user, unset_jwt_cookies, set_access_cookies, get_jwt_identity

from App.models import User, Driver

from App.controllers.user import get_all_users


from.index import index_views

from App.controllers.auth import (
    login_user as login
)

auth_views = Blueprint('auth_views', __name__, template_folder='../templates')

'''
Page/Action Routes
'''    
@auth_views.route('/users', methods=['GET'])
def get_user_page():
    users = get_all_users()
    return render_template('users.html', users=users)

@auth_views.route('/identify', methods=['GET'])
@jwt_required()
def identify_page():
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    if not user:
        return render_template('message.html', title="Identify", message="User not found")
    return render_template('message.html', title="Identify", message=f"You are logged in as {user.id} - {user.username}")
    
@auth_views.route('/driver/signup', methods=['GET', 'POST'])
def driver_signup():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        license_no = request.form.get('license_no')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate input
        if not all([full_name, license_no, username, password, confirm_password]):
            flash('All fields are required')
            return redirect(url_for('auth_views.driver_signup'))
            
        if password != confirm_password:
            flash('Passwords do not match')
            return redirect(url_for('auth_views.driver_signup'))
            
        # Check if username exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('auth_views.driver_signup'))
            
        # Create new driver
        driver = Driver(username=username, password=password, full_Name=full_name, licenseNo=license_no)
        from App.database import db
        db.session.add(driver)
        db.session.commit()
        
        flash('Driver account created successfully! Please log in.')
        return redirect(url_for('index_views.index_page'))
        
    # GET request - show signup form
    return render_template('driver_signup.html')

@auth_views.route('/login', methods=['POST'])
def login_action():
    data = request.form
    token = login(data['username'], data['password'])
    if not token:
        flash('Bad username or password given'), 401
        response = redirect(request.referrer)
    else:
        flash('Login Successful')
        response = redirect(url_for('journey_views.driver_journeys_page'))
        set_access_cookies(response, token) 
    return response

@auth_views.route('/logout', methods=['GET'])
def logout_action():
    response = redirect(request.referrer) 
    flash("Logged Out!")
    unset_jwt_cookies(response)
    return response

'''
API Routes
'''

@auth_views.route('/api/login', methods=['POST'])
def user_login_api():
  data = request.json
  token = login(data['username'], data['password'])
  if not token:
    return jsonify(message='bad username or password given'), 401
  response = jsonify(access_token=token) 
  set_access_cookies(response, token)
  return response

@auth_views.route('/api/identify', methods=['GET'])
@jwt_required()
def identify_user():
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404
    return jsonify({'message': f"username: {user.username}, id: {user.id}"})

@auth_views.route('/api/logout', methods=['GET'])
def logout_api():
    response = jsonify(message="Logged Out!")
    unset_jwt_cookies(response)
    return response