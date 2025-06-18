from App.models import Location
from App.config import config
import openrouteservice
import requests

def get_all_locations():
    return Location.query.all()

def validate_ors_api_key():
    """Validate the OpenRouteService API key"""
    ors_api_key = config.get('OPENROUTE_SERVICE_KEY', '')
    
    if not ors_api_key:
        return {
            'valid': False,
            'message': 'API key not configured'
        }
    
    try:
        # Test the API key with a simple request
        client = openrouteservice.Client(key=ors_api_key)
        
        # Try a simple geocoding request
        test_coords = [[8.681495, 49.41461], [8.686507, 49.41943]]
        response = client.directions(
            coordinates=test_coords,
            profile='driving-car',
            format='geojson'
        )
        
        if response and 'features' in response:
            return {
                'valid': True,
                'message': 'API key is valid'
            }
        else:
            return {
                'valid': False,
                'message': 'Invalid response from OpenRouteService'
            }
    except openrouteservice.exceptions.ApiError as e:
        return {
            'valid': False,
            'message': f'API error: {str(e)}'
        }
    except Exception as e:
        return {
            'valid': False,
            'message': f'Error: {str(e)}'
        }