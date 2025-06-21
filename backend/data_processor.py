import pandas as pd
import os
from typing import Dict, List, Any, Optional, Tuple
from geocoding_service import GeocodingService
import json
from excel_exporter import ExcelExporter

class DataProcessor:
    def __init__(self):
        self.geocoding_service = GeocodingService()
        
        # File paths - updated to point to sample_data folder
        self.files = {
            'bylaw_infractions': 'sample_data/City_of_Waterloo_Bylaw_Parking_Infractions_-239008864429410164.csv',
            'parking_on_street': 'sample_data/Parking_On_Street_-3246370995636778304.csv',
            'parking_lots': 'sample_data/ParkingLots_3219243981443247613.csv'
        }
        
        # Cache file for geocoded coordinates
        self.geocode_cache_file = 'geocode_cache.json'
        self.geocode_cache = self._load_geocode_cache()
    
    def _load_geocode_cache(self) -> Dict[str, Dict[str, float]]:
        """Load cached geocoding results"""
        try:
            if os.path.exists(self.geocode_cache_file):
                with open(self.geocode_cache_file, 'r') as f:
                    cache = json.load(f)
                    print(f"📂 Loaded {len(cache)} cached geocoding results from {self.geocode_cache_file}")
                    return cache
        except Exception as e:
            print(f"❌ Error loading geocode cache: {e}")
        print(f"📂 No existing geocode cache found, starting fresh")
        return {}
    
    def _save_geocode_cache(self):
        """Save geocoding results to cache"""
        try:
            with open(self.geocode_cache_file, 'w') as f:
                json.dump(self.geocode_cache, f, indent=2)
            print(f"💾 Saved {len(self.geocode_cache)} geocoding results to cache")
        except Exception as e:
            print(f"❌ Error saving geocode cache: {e}")
    
    def load_csv_data(self) -> Dict[str, List[Dict]]:
        """Load and parse all CSV files"""
        data = {}
        
        print(f"\n📁 Loading CSV files...")
        print("-" * 50)
        
        try:
            for data_type, filename in self.files.items():
                if os.path.exists(filename):
                    print(f"📄 Loading {filename}...")
                    df = pd.read_csv(filename)
                    
                    # Clean the data - handle NaN values
                    df = df.fillna('')
                    
                    # Convert to records
                    records = df.to_dict('records')
                    
                    # Clean up records - convert any remaining NaN to empty strings
                    for record in records:
                        for key, value in record.items():
                            if pd.isna(value) or str(value).lower() == 'nan':
                                record[key] = ''
                    
                    data[data_type] = records
                    print(f"✅ Loaded {len(data[data_type]):,} records from {data_type}")
                    
                    # Show sample of column names for debugging
                    if records:
                        columns = list(records[0].keys())
                        print(f"   📋 Columns ({len(columns)}): {columns[:5]}{'...' if len(columns) > 5 else ''}")
                    
                else:
                    print(f"⚠️  Warning: {filename} not found")
                    data[data_type] = []
                    
        except Exception as e:
            print(f"❌ Error loading CSV files: {e}")
            return {}
        
        print("-" * 50)
        total_records = sum(len(records) for records in data.values())
        print(f"📊 Total records loaded: {total_records:,}")
        
        return data
    
    def extract_addresses_from_data(self, data: Dict[str, List[Dict]]) -> List[str]:
        """Extract unique addresses from the data for geocoding"""
        addresses = set()
        
        print(f"\n🔍 Extracting addresses from CSV data...")
        print("-" * 50)
        
        for data_type, records in data.items():
            print(f"📋 Processing {data_type} ({len(records):,} records)...")
            extracted_count = 0
            
            # Show sample addresses as we extract them
            sample_addresses = []
            
            for record in records:
                # Different address field names for different data types
                address_fields = self._get_address_fields_for_data_type(data_type)
                
                for field in address_fields:
                    if field in record and record[field]:
                        address = str(record[field]).strip()
                        if address and address.lower() not in ['nan', 'none', '']:
                            if address not in addresses:
                                addresses.add(address)
                                extracted_count += 1
                                
                                # Collect sample addresses for display
                                if len(sample_addresses) < 5:
                                    sample_addresses.append(address)
                            break
            
            print(f"   ✅ Extracted {extracted_count} unique addresses")
            if sample_addresses:
                print(f"   📍 Sample addresses: {', '.join(sample_addresses)}")
        
        print("-" * 50)
        print(f"📊 Total unique addresses found: {len(addresses)}")
        
        return list(addresses)
    
    def _get_address_fields_for_data_type(self, data_type: str) -> List[str]:
        """Get the appropriate address field names for each data type"""
        if data_type == 'parking_on_street':
            return ['STREET', 'Location', 'Address', 'Street_Name']
        elif data_type == 'bylaw_infractions':
            return ['STREET', 'ADDRESS', 'Location', 'Street', 'Street_Name']
        elif data_type == 'parking_lots':
            return ['Address', 'Lot Name', 'Location', 'Name', 'STREET', 'Street']
        else:
            return ['Location', 'Address', 'Street', 'Street_Name', 'STREET', 'Name']
    
    def geocode_all_addresses(self, force_regeocode: bool = False) -> Dict[str, Dict[str, float]]:
        """
        Geocode all addresses in the CSV files
        
        Args:
            force_regeocode: If True, re-geocode all addresses even if cached
        
        Returns:
            Dictionary mapping addresses to coordinates
        """
        if not self.geocoding_service.is_available():
            print("❌ Google Maps API not available. Cannot geocode addresses.")
            return {}
        
        # Load data
        data = self.load_csv_data()
        addresses = self.extract_addresses_from_data(data)
        
        print(f"\n📍 Geocoding Analysis:")
        print("-" * 50)
        print(f"Total addresses to process: {len(addresses)}")
        print(f"Already cached: {len(self.geocode_cache)}")
        
        # Filter out already cached addresses unless force_regeocode is True
        if not force_regeocode:
            uncached_addresses = [addr for addr in addresses if addr not in self.geocode_cache]
            print(f"New addresses to geocode: {len(uncached_addresses)}")
            
            if len(uncached_addresses) == 0:
                print("✅ All addresses already geocoded and cached!")
                return self.geocode_cache
        else:
            uncached_addresses = addresses
            print(f"Force re-geocoding all {len(addresses)} addresses")
        
        # Show sample of addresses to be geocoded
        if uncached_addresses:
            print(f"\n📋 Sample addresses to geocode:")
            for i, addr in enumerate(uncached_addresses[:10]):
                print(f"   {i+1:2d}. {addr}")
            if len(uncached_addresses) > 10:
                print(f"   ... and {len(uncached_addresses) - 10} more addresses")
        
        # Geocode new addresses
        if uncached_addresses:
            new_coordinates = self.geocoding_service.geocode_addresses_batch(uncached_addresses)
            
            # Add to cache
            self.geocode_cache.update(new_coordinates)
            self._save_geocode_cache()
            
            print(f"\n📊 Geocoding Summary:")
            print(f"   📍 Total addresses in dataset: {len(addresses)}")
            print(f"   ✅ Successfully geocoded: {len(new_coordinates)}")
            print(f"   💾 Total cached addresses: {len(self.geocode_cache)}")
            print(f"   📈 Overall coverage: {(len(self.geocode_cache)/len(addresses)*100):.1f}%")
        
        return self.geocode_cache
    
    def add_coordinates_to_data(self, data: Dict[str, List[Dict]], force_regeocode: bool = False) -> Dict[str, List[Dict]]:
        """
        Add latitude and longitude coordinates to all records using geocoding
        
        Args:
            data: Dictionary containing the CSV data
            force_regeocode: If True, re-geocode all addresses
        
        Returns:
            Updated data with coordinates added
        """
        print(f"\n🗺️  Adding coordinates to data records...")
        print("-" * 50)
        
        # Get geocoded coordinates
        geocoded_addresses = self.geocode_all_addresses(force_regeocode)
        
        if not geocoded_addresses and not self.geocoding_service.is_available():
            print("⚠️  No geocoding available. Adding default coordinates.")
            return self._add_default_coordinates(data)
        
        # Add coordinates to each record
        coords_added = 0
        total_records = 0
        coords_by_type = {}
        
        for data_type, records in data.items():
            print(f"\n📋 Processing {data_type}...")
            type_coords_added = 0
            type_total = len(records)
            
            for record in records:
                total_records += 1
                address = self._find_address_in_record(record, data_type)
                
                if address and address in geocoded_addresses:
                    coords = geocoded_addresses[address]
                    record['latitude'] = coords['lat']
                    record['longitude'] = coords['lng']
                    coords_added += 1
                    type_coords_added += 1
                else:
                    # Set default coordinates if geocoding fails
                    record['latitude'] = self.geocoding_service.default_coords[0]
                    record['longitude'] = self.geocoding_service.default_coords[1]
            
            coords_by_type[data_type] = {
                'total': type_total,
                'with_coords': type_coords_added,
                'percentage': (type_coords_added/type_total*100) if type_total > 0 else 0
            }
            
            print(f"   ✅ Added coordinates to {type_coords_added:,}/{type_total:,} records ({coords_by_type[data_type]['percentage']:.1f}%)")
        
        print("-" * 50)
        print(f"📊 Coordinate Addition Summary:")
        print(f"   📍 Total records processed: {total_records:,}")
        print(f"   ✅ Records with geocoded coordinates: {coords_added:,}")
        print(f"   📈 Overall success rate: {(coords_added/total_records*100):.1f}%")
        
        # Show breakdown by data type
        for data_type, stats in coords_by_type.items():
            print(f"   📋 {data_type}: {stats['with_coords']:,}/{stats['total']:,} ({stats['percentage']:.1f}%)")
        
        return data
    
    def _find_address_in_record(self, record: Dict, data_type: str) -> Optional[str]:
        """Find the address field in a record"""
        address_fields = self._get_address_fields_for_data_type(data_type)
        
        for field in address_fields:
            if field in record and record[field]:
                address = str(record[field]).strip()
                if address and address.lower() not in ['nan', 'none', '']:
                    return address
        
        return None
    
    def _add_default_coordinates(self, data: Dict[str, List[Dict]]) -> Dict[str, List[Dict]]:
        """Add default coordinates to all records"""
        for data_type, records in data.items():
            for record in records:
                record['latitude'] = self.geocoding_service.default_coords[0]
                record['longitude'] = self.geocoding_service.default_coords[1]
        
        return data
    
    def get_geocoding_stats(self) -> Dict[str, Any]:
        """Get statistics about geocoding status"""
        data = self.load_csv_data()
        addresses = self.extract_addresses_from_data(data)
        
        geocoded_count = len([addr for addr in addresses if addr in self.geocode_cache])
        
        # Get sample data for each file type
        sample_data = {}
        for data_type, records in data.items():
            if records:
                sample_data[data_type] = {
                    'record_count': len(records),
                    'columns': list(records[0].keys()),
                    'sample_record': records[0],
                    'address_fields_found': [field for field in self._get_address_fields_for_data_type(data_type) if field in records[0]]
                }
        
        return {
            'total_addresses': len(addresses),
            'geocoded_addresses': geocoded_count,
            'cached_addresses': len(self.geocode_cache),
            'geocoding_available': self.geocoding_service.is_available(),
            'sample_addresses': addresses[:10] if addresses else [],
            'data_summary': sample_data
        }
    
    def export_geocoded_data_to_excel(self, force_regeocode: bool = False) -> str:
        """
        Load data, geocode it, and export to Excel files
        
        Args:
            force_regeocode: If True, re-geocode all addresses
        
        Returns:
            Path to the main Excel file created
        """
        print(f"\n📊 EXCEL EXPORT PROCESS")
        print("=" * 60)
        
        # Load and geocode data
        data = self.load_csv_data()
        data_with_coords = self.add_coordinates_to_data(data, force_regeocode)
        
        # Get geocoded addresses for reference
        geocoded_addresses = self.geocode_cache
        
        # Initialize Excel exporter
        exporter = ExcelExporter()
        
        # Export to Excel
        main_file = exporter.export_geocoded_data_to_excel(data_with_coords, geocoded_addresses)
        
        # Also create Google Maps compatible export
        maps_file = exporter.export_for_google_maps(data_with_coords)
        
        print("=" * 60)
        print("✅ EXCEL EXPORT COMPLETED!")
        
        return main_file 