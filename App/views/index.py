from flask import Blueprint, redirect, render_template, request, send_from_directory, jsonify, url_for, Response
from App.controllers import create_user, initialize, get_all_routes
from App.models import Route, RouteStop, Location
import openrouteservice
from App.config import config
import requests
from sqlalchemy import or_

index_views = Blueprint('index_views', __name__, template_folder='../templates')

@index_views.route('/', methods=['GET'])
def index_page():
    routes = get_all_routes()
    stops = Location.query.all()
    # No URL generation here - just pass the basic data
    return render_template('index.html', routes=routes, stops=stops)

@index_views.route('/preview/<int:route_id>', methods=['GET'])
def preview_route_page(route_id):
    """Redirect to index with route_id and scroll_to_map parameters"""
    return redirect(url_for('index_views.index_page', route_id=route_id, scroll_to_map=True))

@index_views.route('/init', methods=['GET'])
def init():
    initialize()
    return jsonify(message='db initialized!')

@index_views.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status':'healthy'})

@index_views.route('/api/routes/<int:route_id>', methods=['GET'])
def get_route_api(route_id):
    route = Route.query.get(route_id)
    
    if not route:
        return jsonify({'error': 'Route not found'}), 404
    
    # Get all stops for this route
    stops = RouteStop.query.filter_by(route_id=route_id).order_by(RouteStop.stop_index).all()
    
    # Format the response
    response = {
        'id': route.id,
        'name': route.name,
        'start_area': {
            'id': route.start_area.id,
            'name': route.start_area.name
        },
        'end_area': {
            'id': route.end_area.id,
            'name': route.end_area.name
        },
        'cost': route.cost,
        'stops': []
    }
    
    # Add stop details
    for stop in stops:
        stop_data = {
            'id': stop.id,
            'stop_index': stop.stop_index,
            'location': {
                'id': stop.location.id,
                'name': stop.location.name,
                'lat': stop.location.lat,
                'lng': stop.location.lng,
                'type': stop.location.type
            }
        }
        response['stops'].append(stop_data)
    
    return jsonify(response)

@index_views.route('/api/route-directions/<int:route_id>', methods=['GET'])
def get_route_directions(route_id):
    """Get realistic driving directions for a route using OpenRouteService"""
    try:
        # Get the route and its stops
        route = Route.query.get(route_id)
        if not route:
            return jsonify({'error': 'Route not found'}), 404
        
        stops = RouteStop.query.filter_by(route_id=route_id).order_by(RouteStop.stop_index).all()
        if not stops or len(stops) < 2:
            return jsonify({'error': 'Route has insufficient stops'}), 400
        
        # Extract coordinates for OpenRouteService (format: [[lng, lat], [lng, lat], ...])
        coordinates = []
        for stop in stops:
            coordinates.append([stop.location.lng, stop.location.lat])
        
        # Get API key
        ors_api_key = config.get('OPENROUTE_SERVICE_KEY', '')
        
        # Check if API key is valid
        if not ors_api_key:
            return jsonify({'error': 'OpenRouteService API key not configured'}), 500
        
        # Initialize client
        client = openrouteservice.Client(key=ors_api_key)
        
        # Get directions
        try:
            directions = client.directions(
                coordinates=coordinates,
                profile='driving-car',
                format='geojson',
                optimize_waypoints=False,
                preference='recommended'
            )
            
            # Return the GeoJSON response
            return jsonify(directions)
            
        except openrouteservice.exceptions.ApiError as e:
            print(f"OpenRouteService API error: {str(e)}")
            # Fallback to direct lines if API fails
            return jsonify({'error': 'Failed to get directions from OpenRouteService', 'fallback': True}), 200
            
    except Exception as e:
        print(f"Error getting route directions: {str(e)}")
        return jsonify({'error': str(e)}), 500

@index_views.route('/api/stops/search', methods=['GET'])
def search_stops():
    """Search for stops by name and get their associated routes"""
    query = request.args.get('q', '')
    route_id = request.args.get('route_id', type=int)  # Optional route filter
    
    if not query or len(query) < 2:
        return jsonify([])
    
    # Base query for stops with names containing the query string
    if route_id:
        # If route_id is provided, only return stops on that route
        stops = Location.query.join(RouteStop).filter(
            Location.name.ilike(f'%{query}%'),
            RouteStop.route_id == route_id
        ).distinct().all()
    else:
        # Otherwise return all matching stops
        stops = Location.query.filter(Location.name.ilike(f'%{query}%')).all()
    
    # Format the response with route information
    result = []
    for stop in stops:
        # Get all routes that use this stop
        route_stops = RouteStop.query.filter_by(location_id=stop.id).all()
        routes = []
        
        for route_stop in route_stops:
            route = Route.query.get(route_stop.route_id)
            if route:
                routes.append({
                    'id': route.id,
                    'name': route.name,
                    'stop_index': route_stop.stop_index
                })
        
        result.append({
            'id': stop.id,
            'name': stop.name,
            'lat': stop.lat,
            'lng': stop.lng,
            'type': stop.type,
            'routes': routes  # Include routes that use this stop
        })
    
    return jsonify(result)

@index_views.route('/api/stop/<int:stop_id>/buses', methods=['GET'])
def get_stop_buses(stop_id):
    """Get buses approaching a stop"""
    from App.controllers.stop import get_buses
    
    route_id = request.args.get('route_id', type=int)
    if not route_id:
        return jsonify({'error': 'Route ID is required'}), 400
    
    try:
        buses = get_buses(stop_id, route_id)
        
        # Format the response
        result = []
        for bus_info in buses:
            result.append({
                'journey_id': bus_info['journey'].id,
                'bus_id': bus_info['bus'].id,
                'plate_num': bus_info['bus'].plate_num,
                'distance': bus_info['distance'],
                'duration_seconds': bus_info['duration_seconds'],
                'estimated_arrival': bus_info['estimated_arrival'],
                'available_seats': bus_info['bus'].get_available_seats()
            })
        
        return jsonify(result)
    except Exception as e:
        print(f"Error getting buses for stop: {str(e)}")
        return jsonify({'error': str(e)}), 500

@index_views.route('/api/ors-status', methods=['GET'])
def check_ors_status():
    """Check the status of the OpenRouteService API key"""
    from App.controllers.location import validate_ors_api_key
    
    result = validate_ors_api_key()
    return jsonify(result)

@index_views.route('/api/routes/<int:route_id>/preview', methods=['GET'])
def preview_route_api(route_id):
    """Get route preview data with stop information"""
    route = Route.query.get(route_id)
    
    if not route:
        return jsonify({'error': 'Route not found'}), 404
    
    # Get all stops for this route
    stops = RouteStop.query.filter_by(route_id=route_id).order_by(RouteStop.stop_index).all()
    
    # Format the response
    response = {
        'id': route.id,
        'name': route.name,
        'start_area': {
            'id': route.start_area.id,
            'name': route.start_area.name
        },
        'end_area': {
            'id': route.end_area.id,
            'name': route.end_area.name
        },
        'cost': route.cost,
        'stops': []
    }
    
    # Add stop details with additional information
    for stop in stops:
        # Get all routes that pass through this stop
        crossing_routes = Route.query.join(RouteStop).filter(
            RouteStop.location_id == stop.location.id,
            Route.id != route_id
        ).all()
        
        stop_data = {
            'id': stop.id,
            'stop_index': stop.stop_index,
            'location': {
                'id': stop.location.id,
                'name': stop.location.name,
                'lat': stop.location.lat,
                'lng': stop.location.lng,
                'type': stop.location.type
            },
            'crossing_routes': [{
                'id': r.id,
                'name': r.name
            } for r in crossing_routes]
        }
        response['stops'].append(stop_data)
    
    return jsonify(response)

@index_views.route('/api/route-preview/<int:route_id>', methods=['GET'])
def get_route_preview(route_id):
    """Get route preview data and trigger client-side scrolling"""
    route = Route.query.get(route_id)
    
    if not route:
        return jsonify({'error': 'Route not found'}), 404
    
    # Get all stops for this route
    stops = RouteStop.query.filter_by(route_id=route_id).order_by(RouteStop.stop_index).all()
    
    # Format the response
    response = {
        'id': route.id,
        'name': route.name,
        'start_area': {
            'id': route.start_area.id,
            'name': route.start_area.name
        },
        'end_area': {
            'id': route.end_area.id,
            'name': route.end_area.name
        },
        'cost': route.cost,
        'stops': [],
        'scroll_to_map': True  # Signal to client to scroll
    }
    
    # Add stop details with additional information
    for stop in stops:
        stop_data = {
            'id': stop.id,
            'stop_index': stop.stop_index,
            'location': {
                'id': stop.location.id,
                'name': stop.location.name,
                'lat': stop.location.lat,
                'lng': stop.location.lng,
                'type': stop.location.type
            }
        }
        response['stops'].append(stop_data)
    
    return jsonify(response)

@index_views.after_request
def inject_scripts(response):
    """Inject JavaScript code into HTML responses"""
    if response.content_type.startswith('text/html'):
        # Add script for map scrolling and zooming
        map_script = """
        <script>
        function previewRoute(routeId) {
            // Clear previous layers
            routeLayer.clearLayers();
            markersLayer.clearLayers();
            stopMarkers = {};
            
            // Scroll to map section smoothly
            document.getElementById('map').scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            // First, get the route stops
            fetch(`/api/routes/${routeId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.stops && data.stops.length > 0) {
                        // Add markers for each stop
                        const bounds = [];
                        data.stops.forEach(stop => {
                            const marker = L.marker([stop.location.lat, stop.location.lng])
                                .bindPopup(createStopPopup(stop))
                                .addTo(markersLayer);
                            
                            // Store marker reference and add coordinates to bounds
                            stopMarkers[stop.id] = marker;
                            bounds.push([stop.location.lat, stop.location.lng]);
                        });
                        
                        // Fit map to show all stops with padding
                        if (bounds.length > 0) {
                            map.fitBounds(bounds, {
                                padding: [50, 50],
                                maxZoom: 15
                            });
                        }
                        
                        // Now get realistic route directions
                        fetch(`/api/route-directions/${routeId}`)
                            .then(response => response.json())
                            .then(directions => {
                                if (directions.error) {
                                    console.warn('Error occured retrieving route lines:', directions.error);
                                    // Fallback to straight lines if API fails
                                    //const polyline = L.polyline(bounds, {color: 'purple', weight: 4}).addTo(routeLayer);
                                } else {
                                    // Add the GeoJSON route to the map
                                    L.geoJSON(directions, {
                                        style: {
                                            color: 'purple',
                                            weight: 4,
                                            opacity: 0.7
                                        }
                                    }).addTo(routeLayer);
                                }
                            })
                            .catch(error => {
                                console.error('Error fetching route directions:', error);
                                // Fallback to straight lines
                                // const polyline = L.polyline(bounds, {color: 'purple', weight: 4}).addTo(routeLayer);
                            });
                    }
                })
                .catch(error => {
                    console.error('Error fetching route data:', error);
                    M.toast({html: 'Error loading route preview'});
                });
        }
        </script>
        """
        
        # Insert the script before the closing body tag
        response.data = response.data.replace(
            b'</body>',
            f'{map_script}</body>'.encode()
        )
    
    return response