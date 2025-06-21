from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import dotenv

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
dotenv.load_dotenv()

# Configuration
# app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
# app.config['DEBUG'] = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'

@app.route('/')
def home():
    """Home endpoint"""
    return jsonify({
        'message': 'Welcome to SpurHacks Backend API',
        'status': 'running',
        'version': '1.0.0'
    })

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': '2024-01-01T00:00:00Z'
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
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])
