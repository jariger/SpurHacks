from flask import Flask, request, jsonify
from flask_cors import CORS
from data_processor import DataProcessor
from filter_service import FilterService
from maps_converter import MapsConverter
from geocoding_service import GeocodingService
from safety_predictor import SafetyPredictor
import os
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()
import googlemaps
import json
from datetime import datetime

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"], supports_credentials=True)

try:
    # Initialize services
    data_processor = DataProcessor()
    filter_service = FilterService()
    maps_converter = MapsConverter()
    geocoding_service = GeocodingService()
    safety_predictor = SafetyPredictor()
    print("✅ All services initialized successfully")
except Exception as e:
    print(f"⚠️  Warning: Some services failed to initialize: {e}")
    print("The server will run with limited functionality")
    # You can still run the server, just without geocoding
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

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'geocoding_available': geocoding_service.is_available()
    })

@app.route('/api/test-geocoding', methods=['GET'])
def test_geocoding():
    """Test geocoding service"""
    try:
        if not geocoding_service.is_available():
            return jsonify({
                'success': False,
                'error': 'Geocoding service not available',
                'api_key_set': bool(os.getenv('GOOGLE_MAPS_API_KEY'))
            })
        
        # Test with a simple address
        test_result = geocoding_service.test_geocoding()
        
        return jsonify({
            'success': test_result,
            'message': 'Geocoding test completed',
            'service_available': geocoding_service.is_available()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/data', methods=['GET'])
def get_data():
    """Get all data without filtering"""
    try:
        data = data_processor.load_csv_data()
        return jsonify({
            'success': True,
            'data': data,
            'count': {k: len(v) for k, v in data.items()}
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/geocode/status', methods=['GET'])
def get_geocoding_status():
    """Get geocoding status and statistics"""
    try:
        stats = data_processor.get_geocoding_stats()
        test_result = geocoding_service.test_geocoding()
        
        return jsonify({
            'success': True,
            'geocoding_available': geocoding_service.is_available(),
            'test_successful': test_result,
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/geocode/process', methods=['POST'])
def process_geocoding():
    """Process geocoding for all addresses in CSV files"""
    try:
        request_data = request.json or {}
        force_regeocode = request_data.get('force_regeocode', False)
        
        if not geocoding_service.is_available():
            return jsonify({
                'success': False,
                'error': 'Google Maps API key not configured'
            }), 400
        
        # Process geocoding
        geocoded_addresses = data_processor.geocode_all_addresses(force_regeocode)
        
        return jsonify({
            'success': True,
            'message': 'Geocoding completed successfully',
            'geocoded_count': len(geocoded_addresses),
            'force_regeocode': force_regeocode
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/geocode/single', methods=['POST'])
def geocode_single():
    """Geocode a single address"""
    try:
        request_data = request.json
        address = request_data.get('address')
        city = request_data.get('city', 'Waterloo, ON, Canada')
        
        if not address:
            return jsonify({
                'success': False,
                'error': 'Address is required'
            }), 400
        
        coords = geocoding_service.geocode_address(address, city)
        
        if coords:
            return jsonify({
                'success': True,
                'address': address,
                'coordinates': coords
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Could not geocode address: {address}'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/data/with-coordinates', methods=['GET'])
def get_data_with_coordinates():
    """Get all data with coordinates added"""
    try:
        data = data_processor.load_csv_data()
        data_with_coords = data_processor.add_coordinates_to_data(data)
        
        # Count records with valid coordinates
        total_records = 0
        records_with_coords = 0
        
        for data_type, records in data_with_coords.items():
            total_records += len(records)
            for record in records:
                if record.get('latitude') and record.get('longitude'):
                    records_with_coords += 1
        
        return jsonify({
            'success': True,
            'data': data_with_coords,
            'total_records': total_records,
            'records_with_coordinates': records_with_coords,
            'coordinate_coverage': f"{(records_with_coords/total_records*100):.1f}%" if total_records > 0 else "0%"
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/markers/geocoded', methods=['GET'])
def get_geocoded_markers():
    """Get all data as Google Maps markers with geocoded coordinates"""
    try:
        data = data_processor.load_csv_data()
        data_with_coords = data_processor.add_coordinates_to_data(data)
        
        # Get safety analysis
        safety_data = safety_predictor.analyze_parking_safety(
            data_with_coords.get('bylaw_infractions', []),
            data_with_coords.get('parking_on_street', [])
        )
        
        # Convert to markers with safety information
        markers = maps_converter.convert_to_google_maps_format(data_with_coords, safety_data)
        
        # Filter out markers with default coordinates (failed geocoding)
        valid_markers = []
        default_lat, default_lng = geocoding_service.default_coords
        
        for marker in markers:
            if (marker['position']['lat'] != default_lat or 
                marker['position']['lng'] != default_lng):
                valid_markers.append(marker)
        
        return jsonify({
            'success': True,
            'markers': valid_markers,
            'total_markers': len(markers),
            'valid_markers': len(valid_markers),
            'geocoding_success_rate': f"{(len(valid_markers)/len(markers)*100):.1f}%" if markers else "0%"
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/safety-analysis', methods=['GET'])
def get_safety_analysis():
    """Get safety analysis for all locations"""
    try:
        data = data_processor.load_csv_data()
        
        # Analyze safety for parking locations
        safety_data = safety_predictor.analyze_parking_safety(
            data.get('bylaw_infractions', []),
            data.get('parking_on_street', [])
        )
        
        return jsonify({
            'success': True,
            'safety_data': safety_data,
            'total_locations': len(safety_data)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/markers', methods=['GET'])
def get_markers():
    """Get all data as Google Maps markers"""
    try:
        data = data_processor.load_csv_data()
        
        # Add coordinates to data if geocoding is enabled
        if geocoding_service.is_available():
            data = data_processor.add_coordinates_to_data(data)
        
        markers = maps_converter.convert_to_google_maps_format(data)
        
        return jsonify({
            'success': True,
            'markers': markers,
            'count': len(markers)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get statistics about the data"""
    try:
        data = data_processor.load_csv_data()
        stats = {}
        
        for data_type, records in data.items():
            if records:
                stats[data_type] = {
                    'total_records': len(records),
                    'sample_record': records[0],
                    'columns': list(records[0].keys()) if records else []
                }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/safety-prediction', methods=['POST'])
def predict_safety():
    """Predict safety for a specific location"""
    try:
        request_data = request.json
        location = request_data.get('location')
        
        if not location:
            return jsonify({
                'success': False,
                'error': 'Location is required'
            }), 400
        
        data = data_processor.load_csv_data()
        prediction = safety_predictor.predict_safety_for_new_location(
            location, 
            data.get('bylaw_infractions', [])
        )
        
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
            'success': True,
            'location': location,
            'prediction': prediction
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/markers-with-safety', methods=['GET'])
def get_markers_with_safety():
    """Get all data as Google Maps markers with safety information"""
    try:
        data = data_processor.load_csv_data()
        
        # Add coordinates to data if geocoding is enabled
        if geocoding_service.is_available():
            data = data_processor.add_coordinates_to_data(data)
        
        # Get safety analysis
        safety_data = safety_predictor.analyze_parking_safety(
            data.get('bylaw_infractions', []),
            data.get('parking_on_street', [])
        )
        
        # Convert to markers with safety information
        markers = maps_converter.convert_to_google_maps_format(data, safety_data)
        
        return jsonify({
            'success': True,
            'markers': markers,
            'count': len(markers),
            'safety_summary': {
                'very_safe': len([m for m in markers if m.get('safety_level') == 'very_safe']),
                'safe': len([m for m in markers if m.get('safety_level') == 'safe']),
                'moderate': len([m for m in markers if m.get('safety_level') == 'moderate']),
                'risky': len([m for m in markers if m.get('safety_level') == 'risky']),
                'dangerous': len([m for m in markers if m.get('safety_level') == 'dangerous'])
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/filter', methods=['POST'])
def filter_data_endpoint():
    """Filter data based on provided criteria"""
    try:
        filters = request.json or {}
        data = data_processor.load_csv_data()
        
        # Add coordinates to data if geocoding is enabled
        if geocoding_service.is_available():
            data = data_processor.add_coordinates_to_data(data)
        
        filtered_data = filter_service.filter_data(data, filters)
        markers = maps_converter.convert_to_google_maps_format(filtered_data)
        
        return jsonify({
            'success': True,
            'markers': markers,
            'count': len(markers),
            'filters_applied': filters
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/safety-thresholds', methods=['GET'])
def get_safety_thresholds():
    """Get safety threshold information"""
    return jsonify({
        'success': True,
        'thresholds': safety_predictor.safety_thresholds,
        'colors': safety_predictor.safety_colors,
        'description': {
            'very_safe': 'Less than 10% infraction rate - Very safe to park',
            'safe': 'Less than 25% infraction rate - Generally safe to park',
            'moderate': 'Less than 50% infraction rate - Moderate risk',
            'risky': 'Less than 75% infraction rate - High chance of ticket',
            'dangerous': '75%+ infraction rate - Avoid parking here'
        }
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'True').lower() == 'true'
    host = os.getenv('HOST', '0.0.0.0')
    
    print(f"🚀 Starting server on {host}:{port}")
    app.run(debug=debug, host=host, port=port)
