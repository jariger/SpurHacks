# SpurHacks Backend

A basic Flask backend server for the SpurHacks project.

## Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the server:**
   ```bash
   python server.py
   ```

   The server will start on `http://localhost:5000`

## API Endpoints

- `GET /` - Home endpoint with server info
- `GET /api/health` - Health check endpoint
- `GET /api/test` - Test GET endpoint
- `POST /api/test` - Test POST endpoint (accepts JSON data)

## Environment Variables

- `SECRET_KEY` - Flask secret key (defaults to 'dev-secret-key')
- `FLASK_DEBUG` - Enable debug mode (defaults to 'True')
- `PORT` - Server port (defaults to 5000)

## Features

- CORS enabled for frontend integration
- JSON API responses
- Error handling for 404 and 500 errors
- Configurable through environment variables 