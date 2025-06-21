from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import dotenv
import googlemaps
import json
from datetime import datetime

app = Flask(__name__)
# Configure CORS to allow requests from the frontend
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"], supports_credentials=True)
dotenv.load_dotenv()

# Google Maps API Configuration
GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
if GOOGLE_MAPS_API_KEY:
    gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)
else:
    gmaps = None


@app.route('/')
def home():
    """Home endpoint"""
    return jsonify({
        'message': 'Welcome to SpurHacks Backend API',
        'status': 'running',
        'version': '1.0.0',
        'maps_enabled': gmaps is not None
    })

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'maps_api': 'available' if gmaps else 'not_configured'
    })

@app.route('/api/maps/config')
def maps_config():
    """Return Google Maps configuration"""
    try:
        return jsonify({
            'api_key': GOOGLE_MAPS_API_KEY if GOOGLE_MAPS_API_KEY else None,
            'enabled': gmaps is not None,
            'vector_support': True,
            'default_center': {
                'lat': 40.7589,
                'lng': -73.9851
            },
            'default_zoom': 15
        })
    except Exception as e:
        print(f"Error in maps_config: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/maps/geocode', methods=['POST'])
def geocode_address():
    """Geocode an address to coordinates"""
    if not gmaps:
        return jsonify({'error': 'Google Maps API not configured'}), 500
    
    try:
        data = request.get_json()
        address = data.get('address')
        
        if not address:
            return jsonify({'error': 'Address is required'}), 400
        
        # Geocode the address
        geocode_result = gmaps.geocode(address)
        
        if geocode_result:
            location = geocode_result[0]['geometry']['location']
            return jsonify({
                'success': True,
                'location': location,
                'formatted_address': geocode_result[0]['formatted_address'],
                'place_id': geocode_result[0]['place_id']
            })
        else:
            return jsonify({'error': 'Address not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/maps/places', methods=['POST'])
def search_places():
    """Search for places near a location"""
    if not gmaps:
        return jsonify({'error': 'Google Maps API not configured'}), 500
    
    try:
        data = request.get_json()
        location = data.get('location')  # {lat, lng}
        radius = data.get('radius', 5000)  # meters
        place_type = data.get('type', 'restaurant')
        
        if not location:
            return jsonify({'error': 'Location is required'}), 400
        
        # Search for places
        places_result = gmaps.places_nearby(
            location=location,
            radius=radius,
            type=place_type
        )
        
        return jsonify({
            'success': True,
            'places': places_result.get('results', []),
            'next_page_token': places_result.get('next_page_token')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/maps/directions', methods=['POST'])
def get_directions():
    """Get directions between two points"""
    if not gmaps:
        return jsonify({'error': 'Google Maps API not configured'}), 500
    
    try:
        data = request.get_json()
        origin = data.get('origin')
        destination = data.get('destination')
        mode = data.get('mode', 'driving')
        
        if not origin or not destination:
            return jsonify({'error': 'Origin and destination are required'}), 400
        
        # Get directions
        directions_result = gmaps.directions(origin, destination, mode=mode)
        
        if directions_result:
            route = directions_result[0]
            return jsonify({
                'success': True,
                'route': route,
                'summary': route['summary'],
                'distance': route['legs'][0]['distance'],
                'duration': route['legs'][0]['duration'],
                'steps': route['legs'][0]['steps']
            })
        else:
            return jsonify({'error': 'No route found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/maps/vector-data')
def get_vector_data():
    """Return vector map data for custom styling"""
    return jsonify({
        'styles': {
            'dark': {
                'featureType': 'all',
                'elementType': 'geometry',
                'stylers': [{'color': '#242f3e'}]
            },
            'labels': {
                'featureType': 'all',
                'elementType': 'labels.text.fill',
                'stylers': [{'color': '#746855'}]
            },
            'roads': {
                'featureType': 'road',
                'elementType': 'geometry',
                'stylers': [{'color': '#38414e'}]
            },
            'water': {
                'featureType': 'water',
                'elementType': 'geometry',
                'stylers': [{'color': '#17263c'}]
            }
        },
        'default_center': {
            'lat': 40.7589,
            'lng': -73.9851
        },
        'default_zoom': 15
    })

@app.route('/api/test', methods=['GET', 'POST'])
def test_endpoint():
    """Test endpoint that accepts GET and POST requests"""
    if request.method == 'GET':
        return jsonify({
            'message': 'GET request successful',
            'method': 'GET'
        })
    elif request.method == 'POST':
        data = request.get_json() or {}
        return jsonify({
            'message': 'POST request successful',
            'method': 'POST',
            'received_data': data
        })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)
