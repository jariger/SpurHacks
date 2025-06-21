#!/usr/bin/env python3
"""
Script to test CSV file reading and show data structure
"""

from data_processor import DataProcessor
import json

def main():
    print("=== CSV File Reading Test ===\n")
    
    # Initialize data processor
    data_processor = DataProcessor()
    
    # Load CSV data
    print("Loading CSV data...")
    data = data_processor.load_csv_data()
    
    # Show summary for each file
    for data_type, records in data.items():
        print(f"\n--- {data_type.upper()} ---")
        print(f"Records loaded: {len(records)}")
        
        if records:
            # Show column names
            columns = list(records[0].keys())
            print(f"Columns ({len(columns)}): {columns}")
            
            # Show sample record
            print(f"\nSample record:")
            sample = records[0]
            for key, value in sample.items():
                print(f"  {key}: {value}")
            
            # Show address fields found
            address_fields = data_processor._get_address_fields_for_data_type(data_type)
            found_fields = [field for field in address_fields if field in sample]
            print(f"\nAddress fields found: {found_fields}")
            
            # Show sample addresses
            addresses = []
            for record in records[:5]:  # First 5 records
                addr = data_processor._find_address_in_record(record, data_type)
                if addr:
                    addresses.append(addr)
            
            if addresses:
                print(f"Sample addresses:")
                for addr in addresses:
                    print(f"  - {addr}")
            else:
                print("No addresses found in sample records")
        else:
            print("No records found")
    
    # Test address extraction
    print(f"\n--- ADDRESS EXTRACTION TEST ---")
    addresses = data_processor.extract_addresses_from_data(data)
    print(f"Total unique addresses extracted: {len(addresses)}")
    
    if addresses:
        print("First 10 addresses:")
        for addr in addresses[:10]:
            print(f"  - {addr}")
    
    # Show geocoding stats
    print(f"\n--- GEOCODING STATS ---")
    stats = data_processor.get_geocoding_stats()
    print(json.dumps(stats, indent=2, default=str))

if __name__ == "__main__":
    main() 