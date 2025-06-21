#!/usr/bin/env python3
"""
Test script to demonstrate geocoding cache functionality
"""

import os
import json
from data_processor import DataProcessor
from geocoding_service import GeocodingService
from dotenv import load_dotenv

def test_geocoding_cache():
    load_dotenv()
    
    print("🗂️  GEOCODING CACHE TEST")
    print("=" * 60)
    
    # Initialize services
    data_processor = DataProcessor()
    geocoding_service = GeocodingService()
    
    # Check initial cache state
    print("📊 INITIAL CACHE STATE")
    print("-" * 30)
    cache_file = 'geocode_cache.json'
    
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            cache = json.load(f)
        print(f"✅ Cache file exists: {cache_file}")
        print(f"📍 Cached addresses: {len(cache)}")
        
        # Show sample cached addresses
        if cache:
            print("📋 Sample cached addresses:")
            for i, (addr, coords) in enumerate(list(cache.items())[:5], 1):
                print(f"   {i}. {addr} → ({coords['lat']:.6f}, {coords['lng']:.6f})")
            if len(cache) > 5:
                print(f"   ... and {len(cache) - 5} more addresses")
    else:
        print(f"📂 No cache file found: {cache_file}")
        print("🆕 This will be a fresh geocoding run")
    
    # Load data and extract addresses
    print(f"\n📁 LOADING DATA")
    print("-" * 20)
    data = data_processor.load_csv_data()
    addresses = data_processor.extract_addresses_from_data(data)
    
    print(f"📍 Total unique addresses found: {len(addresses)}")
    
    # Show cache hit/miss analysis
    print(f"\n🎯 CACHE ANALYSIS")
    print("-" * 20)
    
    cached_addresses = []
    new_addresses = []
    
    for address in addresses:
        if address in data_processor.geocode_cache:
            cached_addresses.append(address)
        else:
            new_addresses.append(address)
    
    print(f"✅ Cache hits: {len(cached_addresses)} addresses")
    print(f"🆕 Cache misses: {len(new_addresses)} addresses")
    print(f"📈 Cache hit rate: {(len(cached_addresses)/len(addresses)*100):.1f}%")
    
    if new_addresses:
        print(f"\n🆕 NEW ADDRESSES TO GEOCODE:")
        for i, addr in enumerate(new_addresses[:10], 1):
            print(f"   {i}. {addr}")
        if len(new_addresses) > 10:
            print(f"   ... and {len(new_addresses) - 10} more addresses")
        
        # Estimate cost
        estimated_cost = len(new_addresses) * 5 / 1000  # $5 per 1000 requests
        print(f"\n💰 Estimated API cost: ${estimated_cost:.2f}")
        print(f"⏱️  Estimated time: {len(new_addresses) * 0.1:.1f} seconds")
    else:
        print(f"\n🎉 All addresses are cached! No API calls needed.")
        print(f"💰 API cost: $0.00")
        print(f"⏱️  Time saved: ~{len(addresses) * 0.1:.1f} seconds")
    
    # Test geocoding with cache
    print(f"\n🚀 RUNNING GEOCODING (with cache)")
    print("-" * 40)
    
    import time
    start_time = time.time()
    
    # This will use cache for existing addresses and only geocode new ones
    geocoded_addresses = data_processor.geocode_all_addresses(force_regeocode=False)
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    print(f"✅ Geocoding completed in {elapsed:.2f} seconds")
    print(f"📍 Total geocoded addresses: {len(geocoded_addresses)}")
    
    # Show final cache state
    print(f"\n📊 FINAL CACHE STATE")
    print("-" * 25)
    
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            final_cache = json.load(f)
        
        file_size = os.path.getsize(cache_file) / 1024  # KB
        print(f"📁 Cache file size: {file_size:.1f} KB")
        print(f"📍 Total cached addresses: {len(final_cache)}")
        
        # Show cache growth
        initial_count = len(data_processor.geocode_cache) if hasattr(data_processor, 'geocode_cache') else 0
        growth = len(final_cache) - len(cached_addresses)
        if growth > 0:
            print(f"📈 New addresses added to cache: {growth}")
    
    # Test cache efficiency
    print(f"\n⚡ CACHE EFFICIENCY TEST")
    print("-" * 30)
    
    print("Testing second run (should be instant)...")
    start_time = time.time()
    
    # Second run should use cache entirely
    geocoded_addresses_2 = data_processor.geocode_all_addresses(force_regeocode=False)
    
    end_time = time.time()
    elapsed_2 = end_time - start_time
    
    print(f"✅ Second run completed in {elapsed_2:.3f} seconds")
    print(f"🚀 Speed improvement: {elapsed/elapsed_2:.1f}x faster")
    
    # Show sample geocoded results
    print(f"\n📋 SAMPLE GEOCODED RESULTS")
    print("-" * 35)
    
    sample_count = min(10, len(geocoded_addresses))
    for i, (addr, coords) in enumerate(list(geocoded_addresses.items())[:sample_count], 1):
        print(f"{i:2d}. {addr:<30} → ({coords['lat']:>10.6f}, {coords['lng']:>11.6f})")

def test_cache_invalidation():
    """Test what happens when we force re-geocoding"""
    
    print(f"\n🔄 CACHE INVALIDATION TEST")
    print("=" * 40)
    
    data_processor = DataProcessor()
    
    print("Testing force re-geocoding (ignores cache)...")
    
    import time
    start_time = time.time()
    
    # This will ignore cache and re-geocode everything
    geocoded_addresses = data_processor.geocode_all_addresses(force_regeocode=True)
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    print(f"✅ Force re-geocoding completed in {elapsed:.2f} seconds")
    print(f"📍 Total addresses re-geocoded: {len(geocoded_addresses)}")
    print("⚠️  Note: This uses API calls even for cached addresses")

def show_cache_contents():
    """Show detailed cache contents"""
    
    print(f"\n📖 DETAILED CACHE CONTENTS")
    print("=" * 40)
    
    cache_file = 'geocode_cache.json'
    
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            cache = json.load(f)
        
        print(f"📁 Cache file: {cache_file}")
        print(f"📍 Total cached addresses: {len(cache)}")
        
        # Sort by address name
        sorted_cache = sorted(cache.items())
        
        print(f"\n📋 ALL CACHED ADDRESSES:")
        print("-" * 70)
        print(f"{'No.':<4} {'Address':<35} {'Latitude':<12} {'Longitude':<12}")
        print("-" * 70)
        
        for i, (addr, coords) in enumerate(sorted_cache, 1):
            print(f"{i:<4} {addr[:34]:<35} {coords['lat']:<12.6f} {coords['lng']:<12.6f}")
        
        # Show geographic bounds
        if cache:
            lats = [coords['lat'] for coords in cache.values()]
            lngs = [coords['lng'] for coords in cache.values()]
            
            print(f"\n🗺️  GEOGRAPHIC BOUNDS:")
            print(f"   Latitude range:  {min(lats):.6f} to {max(lats):.6f}")
            print(f"   Longitude range: {min(lngs):.6f} to {max(lngs):.6f}")
            print(f"   Center point:    ({sum(lats)/len(lats):.6f}, {sum(lngs)/len(lngs):.6f})")
    else:
        print("❌ No cache file found")

if __name__ == "__main__":
    test_geocoding_cache()
    
    # Uncomment to test cache invalidation
    # test_cache_invalidation()
    
    # Uncomment to show all cache contents
    # show_cache_contents() 