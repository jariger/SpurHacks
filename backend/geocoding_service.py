import googlemaps
import os
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
import time

load_dotenv()

class GeocodingService:
    def __init__(self):
        self.api_key = os.getenv('GOOGLE_MAPS_API_KEY')
        self.client = None
        
        if not self.api_key:
            print("Warning: GOOGLE_MAPS_API_KEY not set. Geocoding will not work.")
        else:
            try:
                print(f"Initializing Google Maps client with API key: {self.api_key[:10]}...")
                self.client = googlemaps.Client(key=self.api_key)
                print("✅ Google Maps client initialized successfully")
            except ValueError as e:
                print(f"❌ Invalid Google Maps API key: {e}")
                print("Please check your API key in the .env file")
                self.client = None
            except Exception as e:
                print(f"❌ Error initializing Google Maps client: {e}")
                self.client = None
        
        self.default_city = "Waterloo, ON, Canada"
        self.default_coords = (43.4643, -80.5204)  # Waterloo center
    
    def geocode_address(self, address: str, city: str = None) -> Optional[Dict[str, float]]:
        """
        Convert an address to latitude/longitude coordinates
        
        Args:
            address: Street address
            city: City and country for better accuracy
        
        Returns:
            Dictionary with 'lat' and 'lng' keys or None if geocoding fails
        """
        if not self.client:
            return None
        
        try:
            city = city or self.default_city
            full_address = f"{address}, {city}"
            
            geocode_result = self.client.geocode(full_address)
            
            if geocode_result:
                location = geocode_result[0]['geometry']['location']
                return {
                    'lat': location['lat'],
                    'lng': location['lng']
                }
            else:
                print(f"Could not geocode address: {full_address}")
                return None
                
        except Exception as e:
            print(f"Error geocoding {address}: {e}")
            return None
    
    def geocode_addresses_batch(self, addresses: List[str], city: str = None) -> Dict[str, Dict[str, float]]:
        """
        Geocode multiple addresses in batch with rate limiting
        
        Args:
            addresses: List of addresses to geocode
            city: City and country for better accuracy
        
        Returns:
            Dictionary mapping addresses to coordinate dictionaries
        """
        if not self.client:
            print("Google Maps client not available for batch geocoding")
            return {}
        
        geocoded = {}
        city = city or self.default_city
        
        print(f"Starting batch geocoding of {len(addresses)} addresses...")
        
        for i, address in enumerate(addresses):
            if address not in geocoded:
                coords = self.geocode_address(address, city)
                if coords:
                    geocoded[address] = coords
                
                # Rate limiting: pause every 10 requests to avoid hitting limits
                if (i + 1) % 10 == 0:
                    print(f"Geocoded {i + 1}/{len(addresses)} addresses...")
                    time.sleep(0.1)  # 100ms pause
        
        print(f"Completed geocoding. Successfully geocoded {len(geocoded)}/{len(addresses)} addresses.")
        return geocoded
    
    def is_available(self) -> bool:
        """Check if geocoding service is available"""
        return self.client is not None
    
    def test_geocoding(self) -> bool:
        """Test if geocoding is working with a simple address"""
        if not self.client:
            return False
        
        try:
            test_address = "University Ave, Waterloo, ON, Canada"
            result = self.geocode_address(test_address)
            return result is not None
        except Exception as e:
            print(f"Geocoding test failed: {e}")
            return False 