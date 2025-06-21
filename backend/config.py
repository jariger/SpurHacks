import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Google Maps API Configuration
    GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
    
    # Default coordinates for Waterloo, ON
    DEFAULT_LAT = 43.4643
    DEFAULT_LNG = -80.5204
    
    # Geocoding settings
    DEFAULT_CITY = "Waterloo, ON, Canada"
    
    # API settings
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000)) 