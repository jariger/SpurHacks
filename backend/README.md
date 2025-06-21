# SpurHacks Backend

A Flask-based backend API with Google Maps integration.

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Google Maps API Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Maps JavaScript API
   - Geocoding API
   - Places API
   - Directions API
4. Create credentials (API Key)
5. Restrict the API key to your domain for security

### 3. Environment Variables

Create a `.env` file in the backend directory with:

```env
# Google Maps API Configuration
GOOGLE_MAPS_API_KEY=your_actual_api_key_here

# Flask Configuration
FLASK_DEBUG=True
PORT=5000
```

### 4. Run the Backend

```bash
python server.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### Maps Configuration
- `GET /api/maps/config` - Get Google Maps configuration and API key

### Geocoding
- `POST /api/maps/geocode` - Convert address to coordinates
  ```json
  {
    "address": "Times Square, New York, NY"
  }
  ```

### Places Search
- `POST /api/maps/places` - Search for places near a location
  ```json
  {
    "location": {"lat": 40.7589, "lng": -73.9851},
    "radius": 5000,
    "type": "restaurant"
  }
  ```

### Directions
- `POST /api/maps/directions` - Get directions between two points
  ```json
  {
    "origin": "Times Square, New York, NY",
    "destination": "Central Park, New York, NY",
    "mode": "driving"
  }
  ```

### Vector Map Data
- `GET /api/maps/vector-data` - Get vector styling configuration

## Features

- ✅ Google Maps API integration
- ✅ Geocoding and reverse geocoding
- ✅ Places search
- ✅ Directions and routing
- ✅ Vector map styling support
- ✅ CORS enabled for frontend integration
- ✅ Error handling and validation 