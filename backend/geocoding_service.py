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
            
            print(f"🔍 Geocoding: {full_address}")
            geocode_result = self.client.geocode(full_address)
            
            if geocode_result:
                location = geocode_result[0]['geometry']['location']
                coords = {
                    'lat': location['lat'],
                    'lng': location['lng']
                }
                formatted_address = geocode_result[0]['formatted_address']
                print(f"✅ Success: {address} → ({coords['lat']:.6f}, {coords['lng']:.6f}) [{formatted_address}]")
                return coords
            else:
                print(f"❌ Failed: Could not geocode address: {full_address}")
                return None
                
        except Exception as e:
            print(f"❌ Error geocoding {address}: {e}")
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
            print("❌ Google Maps client not available for batch geocoding")
            return {}
        
        geocoded = {}
        city = city or self.default_city
        
        print(f"\n🚀 Starting batch geocoding of {len(addresses)} addresses...")
        print("=" * 80)
        
        successful_geocodes = 0
        failed_geocodes = 0
        
        for i, address in enumerate(addresses):
            if address not in geocoded:
                coords = self.geocode_address(address, city)
                if coords:
                    geocoded[address] = coords
                    successful_geocodes += 1
                else:
                    failed_geocodes += 1
                
                # Progress update every 10 requests
                if (i + 1) % 10 == 0:
                    print(f"\n📊 Progress: {i + 1}/{len(addresses)} addresses processed")
                    print(f"   ✅ Successful: {successful_geocodes}")
                    print(f"   ❌ Failed: {failed_geocodes}")
                    print(f"   📈 Success rate: {(successful_geocodes/(successful_geocodes + failed_geocodes)*100):.1f}%")
                    print("-" * 40)
                    time.sleep(0.1)  # 100ms pause for rate limiting
        
        print("\n" + "=" * 80)
        print(f"🎉 Batch geocoding completed!")
        print(f"📊 Final Results:")
        print(f"   📍 Total addresses processed: {len(addresses)}")
        print(f"   ✅ Successfully geocoded: {successful_geocodes}")
        print(f"   ❌ Failed to geocode: {failed_geocodes}")
        print(f"   📈 Overall success rate: {(successful_geocodes/len(addresses)*100):.1f}%")
        print("=" * 80)
        
        # Show sample of successfully geocoded addresses
        if geocoded:
            print(f"\n📋 Sample of successfully geocoded addresses:")
            sample_count = min(10, len(geocoded))
            for i, (addr, coords) in enumerate(list(geocoded.items())[:sample_count]):
                print(f"   {i+1:2d}. {addr:<30} → ({coords['lat']:.6f}, {coords['lng']:.6f})")
            if len(geocoded) > sample_count:
                print(f"   ... and {len(geocoded) - sample_count} more addresses")
        
        return geocoded
    
    def is_available(self) -> bool:
        """Check if geocoding service is available"""
        return self.client is not None
    
    def test_geocoding(self) -> bool:
        """Test if geocoding is working with a simple address"""
        if not self.client:
            return False
        
        try:
            print(f"\n🧪 Testing geocoding service...")
            test_address = "University Ave, Waterloo, ON, Canada"
            result = self.geocode_address(test_address)
            success = result is not None
            print(f"🧪 Test result: {'✅ PASSED' if success else '❌ FAILED'}")
            return success
        except Exception as e:
            print(f"🧪 Geocoding test failed: {e}")
            return False 