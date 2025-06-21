#!/usr/bin/env python3
"""
Script to geocode all addresses in CSV files
"""

import os
from dotenv import load_dotenv
from data_processor import DataProcessor
from geocoding_service import GeocodingService

def main():
    load_dotenv()
    
    print("=== CSV Data Geocoding Tool ===")
    
    # Check if API key is available
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if not api_key:
        print("❌ Error: GOOGLE_MAPS_API_KEY not found in environment variables")
        print("Please set your Google Maps API key in the .env file")
        return
    
    # Initialize services
    data_processor = DataProcessor()
    geocoding_service = GeocodingService()
    
    # Test geocoding
    print("🔍 Testing geocoding service...")
    if not geocoding_service.test_geocoding():
        print("❌ Geocoding test failed. Please check your API key and internet connection.")
        return
    
    print("✅ Geocoding service is working!")
    
    # Get current status
    print("\n📊 Current geocoding status:")
    stats = data_processor.get_geocoding_stats()
    print(f"   Total addresses found: {stats['total_addresses']}")
    print(f"   Already geocoded: {stats['geocoded_addresses']}")
    print(f"   Cached results: {stats['cached_addresses']}")
    
    if stats['total_addresses'] == 0:
        print("❌ No addresses found in CSV files. Please check your file paths.")
        return
    
    # Ask user if they want to force re-geocoding
    force_regeocode = input("\n🔄 Force re-geocode all addresses? (y/N): ").lower().startswith('y')
    
    if force_regeocode:
        print("⚠️  Warning: This will re-geocode all addresses and may incur additional API costs.")
        confirm = input("Are you sure? (y/N): ").lower().startswith('y')
        if not confirm:
            print("Geocoding cancelled.")
            return
    
    # Process geocoding
    print(f"\n Starting geocoding process...")
    geocoded_addresses = data_processor.geocode_all_addresses(force_regeocode)
    
    print(f"\n✅ Geocoding completed!")
    print(f"   Successfully geocoded: {len(geocoded_addresses)} addresses")
    
    # Show final status
    final_stats = data_processor.get_geocoding_stats()
    print(f"\n📊 Final status:")
    print(f"   Total addresses: {final_stats['total_addresses']}")
    print(f"   Geocoded addresses: {final_stats['geocoded_addresses']}")
    print(f"   Success rate: {(final_stats['geocoded_addresses']/final_stats['total_addresses']*100):.1f}%")
    
    print("\n🎉 Geocoding process complete! You can now use the API endpoints to get data with coordinates.")

if __name__ == "__main__":
    main() 