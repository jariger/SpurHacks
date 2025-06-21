#!/usr/bin/env python3
"""
Script to export geocoded data to Excel files
"""

import os
from dotenv import load_dotenv
from data_processor import DataProcessor

def main():
    load_dotenv()
    
    print("📊 EXCEL EXPORT TOOL")
    print("=" * 80)
    
    # Check if API key is available
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    if not api_key:
        print("❌ Error: GOOGLE_MAPS_API_KEY not found in environment variables")
        print("Please set your Google Maps API key in the .env file")
        return
    
    print(f"🔑 API Key found: {api_key[:10]}...")
    
    # Initialize data processor
    print(f"\n🚀 Initializing data processor...")
    data_processor = DataProcessor()
    
    # Ask user for options
    print(f"\n⚙️  Export Options:")
    print("1. Export with existing geocoded data (fast)")
    print("2. Re-geocode all addresses and export (may incur API costs)")
    
    choice = input("Enter your choice (1 or 2): ").strip()
    force_regeocode = choice == '2'
    
    if force_regeocode:
        print("⚠️  WARNING: This will re-geocode all addresses and may incur additional API costs.")
        confirm = input("Are you sure? Type 'yes' to continue: ").strip().lower()
        if confirm != 'yes':
            print("❌ Export cancelled.")
            return
    
    # Export to Excel
    try:
        main_file = data_processor.export_geocoded_data_to_excel(force_regeocode)
        
        print(f"\n🎉 SUCCESS!")
        print(f"📄 Main Excel file: {main_file}")
        print(f"📁 Check the 'geocoded_output' folder for all exported files")
        
        # Show file listing
        output_dir = 'geocoded_output'
        if os.path.exists(output_dir):
            files = [f for f in os.listdir(output_dir) if f.endswith('.xlsx')]
            if files:
                print(f"\n📋 All Excel files created:")
                for i, file in enumerate(sorted(files), 1):
                    file_path = os.path.join(output_dir, file)
                    file_size = os.path.getsize(file_path) / 1024  # KB
                    print(f"   {i:2d}. {file} ({file_size:.1f} KB)")
        
    except Exception as e:
        print(f"❌ Error during export: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 