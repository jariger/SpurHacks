# Backend API for CSV Data Processing with Geocoding

This backend service processes three CSV files containing parking and bylaw data for Waterloo, geocodes addresses to coordinates, and provides safety analysis for Google Maps integration.

## Setup Instructions

### 1. Get Google Maps API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Geocoding API
   - Maps JavaScript API
4. Create credentials (API Key)
5. Copy your API key

### 2. Environment Setup

1. Copy the environment template:
```bash
cp .env.example .env
```

2. Add your Google Maps API key to the `.env` file:
```env
GOOGLE_MAPS_API_KEY=your_actual_api_key_here
```

### 3. Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run the geocoding script to process all addresses:
```bash
python geocode_csv_data.py
```

3. Start the server:
```bash
python server.py
```

## Geocoding Process

The system automatically:
1. Extracts addresses from CSV files
2. Geocodes addresses using Google Maps API
3. Caches results to avoid re-geocoding
4. Adds coordinates to all records

### Geocoding Endpoints

#### GET /api/geocode/status
Check geocoding status and statistics.

**Response:**
```json
{
  "success": true,
  "geocoding_available": true,
  "test_successful": true,
  "stats": {
    "total_addresses": 150,
    "geocoded_addresses": 145,
    "cached_addresses": 145,
    "geocoding_available": true,
    "sample_addresses": ["University Ave", "King St", ...]
  }
}
```

#### POST /api/geocode/process
Process geocoding for all addresses.

**Request Body:**
```json
{
  "force_regeocode": false
}
```

#### POST /api/geocode/single
Geocode a single address.

**Request Body:**
```json
{
  "address": "123 University Ave",
  "city": "Waterloo, ON, Canada"
}
```

#### GET /api/data/with-coordinates
Get all data with coordinates added.

#### GET /api/markers/geocoded
Get markers with geocoded coordinates and safety analysis.

## Usage Workflow

1. **Setup API Key**: Configure your Google Maps API key
2. **Run Geocoding**: Execute `python geocode_csv_data.py`
3. **Start Server**: Run `python server.py`
4. **Use API**: Call endpoints to get data with coordinates
5. **Plot on Maps**: Use the coordinates with Google Maps API

## Cost Considerations

- Geocoding API: $5 per 1,000 requests
- The system caches results to minimize API calls
- Monitor usage in Google Cloud Console

## File Structure

1. `City_of_Waterloo_Bylaw_Parking_Infractions_-239008864429410164.csv` - Bylaw parking infractions
2. `Parking_On_Street_-3246370995636778304.csv` - Street parking data
3. `ParkingLots_3219243981443247613.csv` - Parking lots data

## Data Types

- **Bylaw Infractions**: Red markers with infraction details
- **Street Parking**: Blue markers with parking type information
- **Parking Lots**: Green markers with lot type information

## Error Handling

All endpoints return error responses in the format:
```json
{
  "success": false,
  "error": "Error message"
}
```

## Usage with Google Maps

The markers returned by the API are formatted for direct use with Google Maps API. Each marker includes:
- `position`: Latitude and longitude coordinates
- `title`: Location name
- `icon`: Color indicator for the data type
- `description`: Additional information about the point
- `data`: Complete record data for custom tooltips or info windows 
- `data`: Complete record data for custom tooltips or info windows 
