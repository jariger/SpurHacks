#!/usr/bin/env python3
"""
Geocoding cache management utilities
"""

import os
import json
import pickle
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import hashlib

class CacheManager:
    def __init__(self, cache_dir: str = 'cache'):
        self.cache_dir = cache_dir
        self.safety_cache_file = os.path.join(cache_dir, 'safety_analysis_cache.json')
        self.geocode_cache_file = os.path.join(cache_dir, 'geocode_cache.json')
        self.metadata_file = os.path.join(cache_dir, 'cache_metadata.json')
        
        # Create cache directory if it doesn't exist
        self._ensure_cache_dir()
    
    def _ensure_cache_dir(self):
        """Create cache directory if it doesn't exist"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            print(f"📁 Created cache directory: {self.cache_dir}")
    
    def _get_data_hash(self, data_files: Dict[str, str]) -> str:
        """Generate hash of data files to detect changes"""
        hash_content = ""
        for file_path in data_files.values():
            if os.path.exists(file_path):
                # Get file modification time and size for hash
                stat = os.stat(file_path)
                hash_content += f"{file_path}:{stat.st_mtime}:{stat.st_size}:"
        
        return hashlib.md5(hash_content.encode()).hexdigest()
    
    def save_safety_analysis(self, analysis_data: Dict[str, Any], data_files: Dict[str, str]):
        """Save safety analysis results to cache"""
        try:
            # Create cache entry with metadata
            cache_entry = {
                'timestamp': datetime.now().isoformat(),
                'data_hash': self._get_data_hash(data_files),
                'analysis_data': analysis_data,
                'total_locations': len(analysis_data),
                'cache_version': '1.0'
            }
            
            # Save to JSON file
            with open(self.safety_cache_file, 'w') as f:
                json.dump(cache_entry, f, indent=2, default=str)
            
            # Update metadata
            self._update_metadata('safety_analysis', cache_entry['timestamp'])
            
            print(f"💾 Safety analysis cached: {len(analysis_data)} locations")
            
        except Exception as e:
            print(f"❌ Error saving safety analysis cache: {e}")
    
    def load_safety_analysis(self, data_files: Dict[str, str], max_age_hours: int = 24) -> Optional[Dict[str, Any]]:
        """Load safety analysis from cache if valid"""
        try:
            if not os.path.exists(self.safety_cache_file):
                print("📋 No safety analysis cache found")
                return None
            
            with open(self.safety_cache_file, 'r') as f:
                cache_entry = json.load(f)
            
            # Check cache age
            cache_time = datetime.fromisoformat(cache_entry['timestamp'])
            if datetime.now() - cache_time > timedelta(hours=max_age_hours):
                print(f"⏰ Safety analysis cache expired (older than {max_age_hours} hours)")
                return None
            
            # Check if data files have changed
            current_hash = self._get_data_hash(data_files)
            if cache_entry.get('data_hash') != current_hash:
                print("🔄 Data files have changed, cache invalid")
                return None
            
            print(f"✅ Loading safety analysis from cache: {cache_entry['total_locations']} locations")
            return cache_entry['analysis_data']
            
        except Exception as e:
            print(f"❌ Error loading safety analysis cache: {e}")
            return None
    
    def save_geocoded_addresses(self, geocoded_data: Dict[str, Dict[str, float]]):
        """Save geocoded addresses to cache"""
        try:
            cache_entry = {
                'timestamp': datetime.now().isoformat(),
                'geocoded_addresses': geocoded_data,
                'total_addresses': len(geocoded_data),
                'cache_version': '1.0'
            }
            
            with open(self.geocode_cache_file, 'w') as f:
                json.dump(cache_entry, f, indent=2)
            
            self._update_metadata('geocoded_addresses', cache_entry['timestamp'])
            print(f"💾 Geocoded addresses cached: {len(geocoded_data)} locations")
            
        except Exception as e:
            print(f"❌ Error saving geocoded addresses cache: {e}")
    
    def load_geocoded_addresses(self, max_age_days: int = 30) -> Optional[Dict[str, Dict[str, float]]]:
        """Load geocoded addresses from cache"""
        try:
            if not os.path.exists(self.geocode_cache_file):
                print("📋 No geocoded addresses cache found")
                return None
            
            with open(self.geocode_cache_file, 'r') as f:
                cache_entry = json.load(f)
            
            # Check cache age
            cache_time = datetime.fromisoformat(cache_entry['timestamp'])
            if datetime.now() - cache_time > timedelta(days=max_age_days):
                print(f"⏰ Geocoded addresses cache expired (older than {max_age_days} days)")
                return None
            
            print(f"✅ Loading geocoded addresses from cache: {cache_entry['total_addresses']} locations")
            return cache_entry['geocoded_addresses']
            
        except Exception as e:
            print(f"❌ Error loading geocoded addresses cache: {e}")
            return None
    
    def _update_metadata(self, cache_type: str, timestamp: str):
        """Update cache metadata"""
        try:
            metadata = {}
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, 'r') as f:
                    metadata = json.load(f)
            
            metadata[cache_type] = {
                'last_updated': timestamp,
                'file_path': getattr(self, f'{cache_type.replace("_", "_")}_file', 'unknown')
            }
            
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
                
        except Exception as e:
            print(f"❌ Error updating metadata: {e}")
    
    def get_cache_status(self) -> Dict[str, Any]:
        """Get status of all caches"""
        status = {
            'cache_directory': self.cache_dir,
            'caches': {}
        }
        
        # Check safety analysis cache
        if os.path.exists(self.safety_cache_file):
            try:
                with open(self.safety_cache_file, 'r') as f:
                    cache_data = json.load(f)
                status['caches']['safety_analysis'] = {
                    'exists': True,
                    'last_updated': cache_data.get('timestamp'),
                    'total_locations': cache_data.get('total_locations', 0),
                    'file_size': os.path.getsize(self.safety_cache_file)
                }
            except:
                status['caches']['safety_analysis'] = {'exists': True, 'error': 'Cannot read cache'}
        else:
            status['caches']['safety_analysis'] = {'exists': False}
        
        # Check geocoded addresses cache
        if os.path.exists(self.geocode_cache_file):
            try:
                with open(self.geocode_cache_file, 'r') as f:
                    cache_data = json.load(f)
                status['caches']['geocoded_addresses'] = {
                    'exists': True,
                    'last_updated': cache_data.get('timestamp'),
                    'total_addresses': cache_data.get('total_addresses', 0),
                    'file_size': os.path.getsize(self.geocode_cache_file)
                }
            except:
                status['caches']['geocoded_addresses'] = {'exists': True, 'error': 'Cannot read cache'}
        else:
            status['caches']['geocoded_addresses'] = {'exists': False}
        
        return status
    
    def clear_cache(self, cache_type: str = 'all'):
        """Clear specific cache or all caches"""
        cleared = []
        
        if cache_type in ['all', 'safety_analysis'] and os.path.exists(self.safety_cache_file):
            os.remove(self.safety_cache_file)
            cleared.append('safety_analysis')
        
        if cache_type in ['all', 'geocoded_addresses'] and os.path.exists(self.geocode_cache_file):
            os.remove(self.geocode_cache_file)
            cleared.append('geocoded_addresses')
        
        if cache_type == 'all' and os.path.exists(self.metadata_file):
            os.remove(self.metadata_file)
            cleared.append('metadata')
        
        print(f"🗑️ Cleared caches: {', '.join(cleared)}")
        return cleared

def show_cache_stats():
    """Show cache statistics"""
    cache_file = 'geocode_cache.json'
    
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            cache = json.load(f)
        
        file_size = os.path.getsize(cache_file)
        
        print(f"📊 CACHE STATISTICS")
        print(f"   File: {cache_file}")
        print(f"   Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        print(f"   Addresses: {len(cache):,}")
        print(f"   Avg per address: {file_size/len(cache):.1f} bytes")
        
        # Calculate potential savings
        api_calls_saved = len(cache)
        cost_saved = api_calls_saved * 5 / 1000
        time_saved = api_calls_saved * 0.1
        
        print(f"\n💰 SAVINGS:")
        print(f"   API calls saved: {api_calls_saved:,}")
        print(f"   Cost saved: ${cost_saved:.2f}")
        print(f"   Time saved: {time_saved:.1f} seconds")
    else:
        print("❌ No cache file found")

def backup_cache():
    """Backup the cache file"""
    cache_file = 'geocode_cache.json'
    
    if os.path.exists(cache_file):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"geocode_cache_backup_{timestamp}.json"
        
        import shutil
        shutil.copy2(cache_file, backup_file)
        print(f"✅ Cache backed up to: {backup_file}")
    else:
        print("❌ No cache file to backup")

def clear_cache():
    """Clear the geocoding cache"""
    cache_file = 'geocode_cache.json'
    
    if os.path.exists(cache_file):
        backup_cache()  # Backup before clearing
        os.remove(cache_file)
        print(f"🗑️  Cache cleared: {cache_file}")
        print("⚠️  Next geocoding run will rebuild the cache")
    else:
        print("❌ No cache file to clear")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "stats":
            show_cache_stats()
        elif command == "backup":
            backup_cache()
        elif command == "clear":
            clear_cache()
        else:
            print("Usage: python cache_manager.py [stats|backup|clear]")
    else:
        show_cache_stats() 