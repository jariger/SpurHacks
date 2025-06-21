#!/usr/bin/env python3
"""
Script to show cache details and status
"""

from cache_manager import CacheManager
import json

def main():
    print("🗂️ CACHE STATUS REPORT")
    print("=" * 50)
    
    cache_manager = CacheManager()
    status = cache_manager.get_cache_status()
    
    print(f"📁 Cache Directory: {status['cache_directory']}")
    print()
    
    for cache_name, cache_info in status['caches'].items():
        print(f"📋 {cache_name.replace('_', ' ').title()}:")
        
        if not cache_info['exists']:
            print("   ❌ Not cached")
        elif 'error' in cache_info:
            print(f"   ⚠️ Error: {cache_info['error']}")
        else:
            print(f"   ✅ Cached")
            print(f"   📅 Last Updated: {cache_info.get('last_updated', 'Unknown')}")
            
            if 'total_locations' in cache_info:
                print(f"   📍 Locations: {cache_info['total_locations']}")
            if 'total_addresses' in cache_info:
                print(f"   🌍 Addresses: {cache_info['total_addresses']}")
            
            file_size = cache_info.get('file_size', 0)
            if file_size > 1024 * 1024:
                print(f"   💾 Size: {file_size / (1024*1024):.1f} MB")
            elif file_size > 1024:
                print(f"   💾 Size: {file_size / 1024:.1f} KB")
            else:
                print(f"   💾 Size: {file_size} bytes")
        
        print()

if __name__ == "__main__":
    main() 