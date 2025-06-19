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
    """Inject our scripts into HTML responses"""
    if response.content_type == 'text/html; charset=utf-8':
        html = response.get_data(as_text=True)
        
        # Only inject into index page
        if '<title>Next Stop</title>' in html:
            # Create inline script for scrolling and filtering
            script_tags = """
            <!-- Auto-injected scripts -->
            <script>
            // Wait for the page to load
            document.addEventListener('DOMContentLoaded', function() {
                // Override the previewRoute function to add scrolling
                const originalPreviewRoute = window.previewRoute;
                window.previewRoute = function(routeId) {
                    // Call the original function
                    if (originalPreviewRoute) {
                        originalPreviewRoute(routeId);
                    }
                    
                    // Store current route ID for filtering
                    window.currentRouteId = routeId;
                    
                    // Scroll to map
                    setTimeout(function() {
                        document.getElementById('map').scrollIntoView({
                            behavior: 'smooth',
                            block: 'center'
                        });
                    }, 100);
                };
                
                // Handle URL parameters
                const urlParams = new URLSearchParams(window.location.search);
                const routeId = urlParams.get('route_id');
                const scrollToMap = urlParams.get('scroll_to_map');
                
                if (routeId && scrollToMap === 'true') {
                    // Wait for map to initialize
                    setTimeout(function() {
                        window.previewRoute(routeId);
                    }, 500);
                }
                
                // Add filtering to search
                const searchInput = document.getElementById('stop-search');
                if (searchInput) {
                    // Store original event handlers
                    const originalHandlers = searchInput._handlers || [];
                    
                    // Override with our handler
                    const searchHandler = function() {
                        const query = searchInput.value.trim();
                        const searchResults = document.getElementById('search-results');
                        
                        if (query.length < 2) {
                            searchResults.style.display = 'none';
                            return;
                        }
                        
                        // Include current route ID if available
                        const routeParam = window.currentRouteId ? `&route_id=${window.currentRouteId}` : '';
                        
                        // Fetch search results with route filtering
                        fetch(`/api/stops/search?q=${encodeURIComponent(query)}${routeParam}`)
                            .then(response => response.json())
                            .then(data => {
                                // Process results
                                searchResults.innerHTML = '';
                                
                                if (data.length === 0) {
                                    searchResults.innerHTML = '<div class="collection-item">No stops found</div>';
                                } else {
                                    data.forEach(stop => {
                                        const item = document.createElement('a');
                                        item.href = '#';
                                        item.className = 'collection-item';
                                        
                                        // Show routes that use this stop
                                        let routesList = '';
                                        if (stop.routes && stop.routes.length > 0) {
                                            routesList = stop.routes.map(r => r.name).join(', ');
                                        }
                                        
                                        item.innerHTML = `
                                            <span class="title">${stop.name}</span>
                                            <p>${stop.type}</p>
                                            ${routesList ? `<p class="grey-text">Routes: ${routesList}</p>` : ''}
                                        `;
                                        
                                        item.addEventListener('click', function(e) {
                                            e.preventDefault();
                                            
                                            // Center map on selected stop
                                            map.setView([stop.lat, stop.lng], 15);
                                            
                                            // Add marker for the stop
                                            markersLayer.clearLayers();
                                            const marker = L.marker([stop.lat, stop.lng])
                                                .bindPopup(`<b>${stop.name}</b><br>${stop.type}`)
                                                .addTo(markersLayer);
                                            
                                            marker.openPopup();
                                            
                                            // Clear search
                                            searchInput.value = '';
                                            searchResults.style.display = 'none';
                                            
                                            // Scroll to map
                                            document.getElementById('map').scrollIntoView({
                                                behavior: 'smooth',
                                                block: 'center'
                                            });
                                        });
                                        
                                        searchResults.appendChild(item);
                                    });
                                }
                                
                                searchResults.style.display = 'block';
                            })
                            .catch(error => {
                                console.error('Error searching stops:', error);
                                searchResults.innerHTML = '<div class="collection-item">Error searching stops</div>';
                                searchResults.style.display = 'block';
                            });
                    };
                    
                    // Replace the original initializeSearch function
                    window.initializeSearch = function() {
                        searchInput.addEventListener('input', debounce(searchHandler, 300));
                    };
                    
                    // If the search is already initialized, add our handler
                    searchInput.addEventListener('input', debounce(searchHandler, 300));
                }
            });
            </script>
            """
            
            # Insert before closing body tag
            html = html.replace('</body>', f'{script_tags}\n</body>')
            
            # Update response
            response.set_data(html)
            
    return response