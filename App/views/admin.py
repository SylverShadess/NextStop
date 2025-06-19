from flask import flash, redirect, request, url_for, Blueprint, render_template, jsonify
from flask_admin.contrib.sqla import ModelView
from flask_jwt_extended import jwt_required, current_user, unset_jwt_cookies, set_access_cookies, get_jwt_identity
from flask_admin import Admin
from App.models import db, User, Bus
from App.database import db as app_db
from flask_jwt_extended.exceptions import NoAuthorizationError, InvalidHeaderError, JWTExtendedException
from datetime import datetime

class AdminView(ModelView):

    @jwt_required()
    def is_accessible(self):
        return current_user is not None

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        flash("Login to access admin")
        return redirect(url_for('index_page', next=request.url))

def setup_admin(app):
    admin = Admin(app, name='FlaskMVC', template_mode='bootstrap3')
    admin.add_view(AdminView(User, db.session))

admin_views = Blueprint('admin_views', __name__, template_folder='../templates')

@admin_views.route('/admin')
@jwt_required()
def admin_index():
    # Check if the user is an admin
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    
    if not user or not user.is_admin:
        return render_template('401.html', error_message="Unauthorized"), 401
    
    return render_template('admin/index.html')

@admin_views.route('/admin/create-bus', methods=['GET', 'POST'])
@jwt_required()
def create_bus():
    # Check if the user is an admin
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    
    if not user or not user.is_admin:
        return render_template('401.html', error_message="Unauthorized"), 401
    
    if request.method == 'POST':
        plate_num = request.form.get('plate_num')
        max_passenger_count = request.form.get('max_passenger_count', 50, type=int)
        
        if not plate_num:
            flash('Plate number is required')
            return redirect(url_for('admin_views.create_bus'))
        
        # Check if a bus with this plate number already exists
        existing_bus = Bus.query.filter_by(plate_num=plate_num).first()
        if existing_bus:
            flash('A bus with this plate number already exists')
            return redirect(url_for('admin_views.create_bus'))
        
        # Create a new bus
        bus = Bus(plate_num=plate_num, max_passenger_count=max_passenger_count)
        app_db.session.add(bus)
        app_db.session.commit()
        
        flash(f'Bus {plate_num} created successfully')
        return redirect(url_for('admin_views.admin_index'))
    
    # GET request - show the form
    return render_template('admin/create_bus.html')