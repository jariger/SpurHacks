#!/usr/bin/env python3
"""
Script to run geocoding with detailed output
"""

import os
from dotenv import load_dotenv
from data_processor import DataProcessor
from geocoding_service import GeocodingService

def main():
    load_dotenv()
    
    print("🗺️  GEOCODING PROCESSOR")
    print("=" * 80)
    
    # Check if API key is available
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if not api_key:
        print("❌ Error: GOOGLE_MAPS_API_KEY not found in environment variables")
        print("Please set your Google Maps API key in the .env file")
        return
    
    print(f"🔑 API Key found: {api_key[:10]}...")
    
    # Initialize services
    print(f"\n🚀 Initializing services...")
    data_processor = DataProcessor()
    geocoding_service = GeocodingService()
    
    # Test geocoding service
    if not geocoding_service.test_geocoding():
        print("❌ Geocoding test failed. Exiting.")
        return
    
    # Ask user for options
    print(f"\n⚙️  Geocoding Options:")
    print("1. Process new addresses only (recommended)")
    print("2. Force re-geocode all addresses (may incur additional costs)")
    
    choice = input("Enter your choice (1 or 2): ").strip()
    force_regeocode = choice == '2'
    
    if force_regeocode:
        print("⚠️  WARNING: This will re-geocode all addresses and may incur additional API costs.")
        confirm = input("Are you sure? Type 'yes' to continue: ").strip().lower()
        if confirm != 'yes':
            print("❌ Geocoding cancelled.")
            return
    
    # Process geocoding
    print(f"\n🎯 Starting geocoding process...")
    geocoded_addresses = data_processor.geocode_all_addresses(force_regeocode)
    
    # Show final results
    print(f"\n🎉 GEOCODING COMPLETED!")
    print("=" * 80)
    
    if geocoded_addresses:
        print(f"📊 Final Statistics:")
        print(f"   📍 Total geocoded addresses: {len(geocoded_addresses)}")
        
        # Show all geocoded locations
        print(f"\n📋 ALL GEOCODED LOCATIONS:")
        print("-" * 80)
        for i, (address, coords) in enumerate(sorted(geocoded_addresses.items()), 1):
            print(f"{i:3d}. {address:<40} → ({coords['lat']:>10.6f}, {coords['lng']:>11.6f})")
        
        # Show geographic bounds
        lats = [coords['lat'] for coords in geocoded_addresses.values()]
        lngs = [coords['lng'] for coords in geocoded_addresses.values()]
        
        print(f"\n🗺️  Geographic Bounds:")
        print(f"   📍 Latitude range:  {min(lats):.6f} to {max(lats):.6f}")
        print(f"   📍 Longitude range: {min(lngs):.6f} to {max(lngs):.6f}")
        print(f"   📍 Center point:    ({sum(lats)/len(lats):.6f}, {sum(lngs)/len(lngs):.6f})")
        
    else:
        print("❌ No addresses were successfully geocoded.")
    
    print("=" * 80)
    print("✅ Geocoding process complete!")

if __name__ == "__main__":
    main() 