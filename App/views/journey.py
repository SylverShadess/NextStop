from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_jwt_extended import jwt_required, current_user, get_jwt_identity
from datetime import datetime
import math

from App.controllers.journey import (
    get_journey_stats, 
    create_journey_board_event, 
    complete_journey,
    cancel_journey,
    move_to_next_stop,
    move_to_previous_stop,
    get_journey_progress
)
from App.controllers.route import get_all_routes
from App.models import Journey, Bus, Route, RouteStop, User, Driver
from App.database import db

journey_views = Blueprint('journey_views', __name__, template_folder='../templates')

@journey_views.route('/driver/journeys', methods=['GET'])
@jwt_required()
def driver_journeys_page():
    try:
        # Get all journeys for the current driver
        username = get_jwt_identity()
        user = User.query.filter_by(username=username).first()
        if not user:
            flash('User not found')
            return redirect(url_for('index_views.index_page'))
        
        journeys = Journey.get_journeys_for_driver(user.id)
        return render_template('driver_journeys.html', journeys=journeys)
    except Exception as e:
        print(f"Error in driver_journeys_page: {str(e)}")
        flash('An error occurred while loading journeys')
        return render_template('driver_journeys.html', journeys=[])

@journey_views.route('/driver/journeys/new', methods=['GET'])
@jwt_required()
def new_journey_page():
    # Get all available routes
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('User not found')
        return redirect(url_for('index_views.index_page'))
    
    routes = get_all_routes()
    return render_template('new_journey.html', routes=routes)

@journey_views.route('/driver/journeys/create', methods=['POST'])
@jwt_required()
def create_journey():
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('User not found')
        return redirect(url_for('index_views.index_page'))
    
    route_id = request.form.get('route_id')
    if not route_id:
        flash('Route is required')
        return redirect(url_for('journey_views.new_journey_page'))
    
    route = Route.query.get(route_id)
    if not route:
        flash('Selected route not found')
        return redirect(url_for('journey_views.new_journey_page'))
    
    # Get or create a bus for the driver
    bus = Bus.query.filter_by(driver_id=user.id).first()
    if not bus:
        # Create a new bus for the driver with a default plate number
        plate_num = f"BUS-{user.id}-{datetime.now().strftime('%Y%m%d')}"
        bus = Bus(plate_num=plate_num, driver=user, route=route)
        db.session.add(bus)
    else:
        # Update the bus's route
        bus.selectRoute(route)
    
    # Create a new journey
    journey = Journey(driver=user, route=route, bus=bus)
    journey.startJourney()
    
    flash(f'Journey on route {route.name} has been started')
    return redirect(url_for('journey_views.journey_progress_page', journey_id=journey.id))

@journey_views.route('/driver/journeys/<int:journey_id>/progress', methods=['GET'])
@jwt_required()
def journey_progress_page(journey_id):
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('User not found')
        return redirect(url_for('index_views.index_page'))
    
    # Get the journey
    journey = Journey.query.get(journey_id)
    
    if not journey:
        flash('Journey not found')
        return redirect(url_for('journey_views.driver_journeys_page'))
    
    if journey.driver_id != user.id:
        flash('You do not have permission to view this journey')
        return redirect(url_for('journey_views.driver_journeys_page'))
    
    if journey.endTime:
        flash('This journey has already been completed')
        return redirect(url_for('journey_views.journey_stats_page', journey_id=journey_id))
    
    # Calculate progress percentage
    progress = journey.calculateProgress()
    
    # Get the current stop
    current_stop = journey.getCurrentStop()
    next_stop = journey.getNextStop()
    prev_stop = journey.getPreviousStop()
    
    # Calculate seats available
    seats_available = journey.bus.get_available_seats()
    
    # Get current location name
    current_location = current_stop.location.name if current_stop else "Starting point"
    
    # Calculate ETA based on the next stop
    eta_time = "End of route"
    eta_distance = "0"
    
    if next_stop:
        # In a real app, this would use a mapping service
        # For demo purposes, we'll generate some mock data
        import random
        eta_minutes = random.randint(5, 20)
        eta_time = f"{eta_minutes} minutes"
        eta_distance = f"{random.randint(1, 10)}.{random.randint(1, 9)}"
    
    return render_template('journey_progress.html', 
                          journey=journey,
                          progress=progress,
                          seats_available=seats_available,
                          eta_time=eta_time,
                          eta_distance=eta_distance,
                          current_location=current_location,
                          current_stop=current_stop,
                          next_stop=next_stop,
                          prev_stop=prev_stop)

@journey_views.route('/driver/journeys/board', methods=['POST'])
@jwt_required()
def create_board_event():
    try:
        username = get_jwt_identity()
        user = User.query.filter_by(username=username).first()
        if not user:
            flash('User not found')
            return redirect(url_for('index_views.index_page'))
        
        journey_id = request.form.get('journey_id')
        event_type = request.form.get('type')
        qty = request.form.get('qty', 1, type=int)
        
        if not all([journey_id, event_type]):
            flash('Missing required fields')
            return redirect(url_for('journey_views.journey_progress_page', journey_id=journey_id))
        
        # Get the journey
        journey = Journey.query.get(journey_id)
        if not journey:
            flash('Journey not found')
            return redirect(url_for('journey_views.driver_journeys_page'))
        
        # Get the current stop
        current_stop = journey.getCurrentStop()
        if not current_stop:
            flash('No current stop found. Please move to a stop first.')
            return redirect(url_for('journey_views.journey_progress_page', journey_id=journey_id))
        
        try:
            # Create board event using the current stop
            result = create_journey_board_event(journey_id, event_type, qty, current_stop.id)
            
            if result:
                action = "boarded" if event_type == "Enter" else "unboarded"
                flash(f'{qty} passenger(s) {action} successfully at {current_stop.location.name}')
            else:
                flash('Failed to create boarding event')
        except ValueError as e:
            flash(str(e))
        
        return redirect(url_for('journey_views.journey_progress_page', journey_id=journey_id))
    except Exception as e:
        print(f"Error in create_board_event: {str(e)}")
        flash('An error occurred while processing the boarding event')
        return redirect(url_for('journey_views.driver_journeys_page'))

@journey_views.route('/driver/journeys/complete', methods=['POST'])
@jwt_required()
def complete_journey_route():
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('User not found')
        return redirect(url_for('index_views.index_page'))
    
    journey_id = request.form.get('journey_id')
    
    if not journey_id:
        flash('Journey ID is required')
        return redirect(url_for('journey_views.driver_journeys_page'))
    
    # Complete the journey
    result = complete_journey(journey_id)
    
    if result:
        flash('Journey completed successfully')
        return redirect(url_for('journey_views.journey_stats_page', journey_id=journey_id))
    else:
        flash('Failed to complete journey')
        return redirect(url_for('journey_views.journey_progress_page', journey_id=journey_id))

@journey_views.route('/driver/journeys/<int:journey_id>/next-stop', methods=['POST'])
@jwt_required()
def move_to_next_stop_route(journey_id):
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('User not found')
        return redirect(url_for('index_views.index_page'))
    
    # Get the journey
    journey = Journey.query.get(journey_id)
    
    if not journey:
        flash('Journey not found')
        return redirect(url_for('journey_views.driver_journeys_page'))
    
    if journey.driver_id != user.id:
        flash('You do not have permission to modify this journey')
        return redirect(url_for('journey_views.driver_journeys_page'))
    
    if journey.endTime:
        flash('This journey has already been completed')
        return redirect(url_for('journey_views.journey_stats_page', journey_id=journey_id))
    
    # Move to next stop
    next_stop = move_to_next_stop(journey_id)
    
    if next_stop:
        flash(f'Moved to next stop: {next_stop.location.name}')
    else:
        flash('Could not move to next stop. You may have reached the end of the route.')
    
    return redirect(url_for('journey_views.journey_progress_page', journey_id=journey_id))

@journey_views.route('/driver/journeys/<int:journey_id>/previous-stop', methods=['POST'])
@jwt_required()
def move_to_previous_stop_route(journey_id):
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('User not found')
        return redirect(url_for('index_views.index_page'))
    
    # Get the journey
    journey = Journey.query.get(journey_id)
    
    if not journey:
        flash('Journey not found')
        return redirect(url_for('journey_views.driver_journeys_page'))
    
    if journey.driver_id != user.id:
        flash('You do not have permission to modify this journey')
        return redirect(url_for('journey_views.driver_journeys_page'))
    
    if journey.endTime:
        flash('This journey has already been completed')
        return redirect(url_for('journey_views.journey_stats_page', journey_id=journey_id))
    
    # Move to previous stop
    prev_stop = move_to_previous_stop(journey_id)
    
    if prev_stop:
        flash(f'Moved to previous stop: {prev_stop.location.name}')
    else:
        flash('Could not move to previous stop. You may be at the first stop.')
    
    return redirect(url_for('journey_views.journey_progress_page', journey_id=journey_id))

@journey_views.route('/driver/journeys/cancel', methods=['POST'])
@jwt_required()
def cancel_journey_route():
    username = get_jwt_identity()
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('User not found')
        return redirect(url_for('index_views.index_page'))
    
    journey_id = request.form.get('journey_id')
    
    if not journey_id:
        flash('Journey ID is required')
        return redirect(url_for('journey_views.driver_journeys_page'))
    
    # Get the journey
    journey = Journey.query.get(journey_id)
    
    if not journey:
        flash('Journey not found')
        return redirect(url_for('journey_views.driver_journeys_page'))
    
    if journey.driver_id != user.id:
        flash('You do not have permission to cancel this journey')
        return redirect(url_for('journey_views.driver_journeys_page'))
    
    # Cancel the journey
    result = cancel_journey(journey_id)
    
    if result:
        flash('Journey cancelled')
    else:
        flash('Failed to cancel journey')
    
    return redirect(url_for('journey_views.new_journey_page'))

@journey_views.route('/driver/journeys/<int:journey_id>/stats', methods=['GET'])
@jwt_required()
def journey_stats_page(journey_id):
    try:
        username = get_jwt_identity()
        user = User.query.filter_by(username=username).first()
        if not user:
            flash('User not found')
            return redirect(url_for('index_views.index_page'))
        
        # Get the journey first to check permissions
        journey = Journey.query.get(journey_id)
        if not journey:
            flash('Journey not found')
            return redirect(url_for('journey_views.driver_journeys_page'))
        
        if journey.driver_id != user.id and not user.is_admin:
            flash('You do not have permission to view this journey')
            return redirect(url_for('journey_views.driver_journeys_page'))
        
        # Get journey stats
        stats = get_journey_stats(journey_id)
        
        if not stats:
            flash('Journey stats not found')
            return redirect(url_for('journey_views.driver_journeys_page'))
        
        return render_template('journey_stats.html', stats=stats, journey=journey)
    except Exception as e:
        print(f"Error in journey_stats_page: {str(e)}")
        flash('An error occurred while loading journey stats')
        return redirect(url_for('journey_views.driver_journeys_page')) 