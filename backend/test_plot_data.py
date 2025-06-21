#!/usr/bin/env python3
"""
Direct function to get plot data for testing
"""

import pandas as pd
import os
from data_processor import DataProcessor
from enhanced_safety_predictor import EnhancedSafetyPredictor
import json

def get_plot_data():
    """
    Main function that returns the data needed for plotting markers
    This is what the frontend should receive
    """
    print("🗺️ Getting plot data...")
    
    try:
        # 1. Load CSV data
        data_files = {
            'bylaw_infractions': 'sample_data/City_of_Waterloo_Bylaw_Parking_Infractions_-239008864429410164.csv',
            'parking_on_street': 'sample_data/Parking_On_Street_-3246370995636778304.csv',
            'parking_lots': 'sample_data/ParkingLots_3219243981443247613.csv'
        }
        
        # Load dataframes
        bylaw_infractions = pd.read_csv(data_files['bylaw_infractions']) if os.path.exists(data_files['bylaw_infractions']) else pd.DataFrame()
        parking_on_street = pd.read_csv(data_files['parking_on_street']) if os.path.exists(data_files['parking_on_street']) else pd.DataFrame()
        parking_lots = pd.read_csv(data_files['parking_lots']) if os.path.exists(data_files['parking_lots']) else pd.DataFrame()
        
        print(f"📊 Loaded: {len(bylaw_infractions)} infractions, {len(parking_on_street)} street parking, {len(parking_lots)} lots")
        
        # 2. Get geocoded addresses
        data_processor = DataProcessor()
        geocoded_addresses = data_processor._load_geocode_cache()
        
        if not geocoded_addresses:
            print("❌ No geocoded addresses found!")
            return {'error': 'No geocoded data', 'markers': []}
        
        print(f"🌍 Found {len(geocoded_addresses)} geocoded addresses")
        
        # 3. Run safety analysis
        enhanced_predictor = EnhancedSafetyPredictor()
        safety_analysis = enhanced_predictor.analyze_comprehensive_parking_safety(
            bylaw_infractions,
            parking_on_street, 
            parking_lots
        )
        
        print(f"🛡️ Safety analysis complete: {len(safety_analysis)} locations")
        
        # 4. Create markers
        markers = []
        for location, analysis in safety_analysis.items():
            if location in geocoded_addresses:
                coords = geocoded_addresses[location]
                
                # Determine marker color based on safety level
                safety_score = analysis['safety_score']
                if safety_score >= 0.8:
                    icon = 'https://maps.google.com/mapfiles/ms/icons/green-dot.png'
                elif safety_score >= 0.6:
                    icon = 'https://maps.google.com/mapfiles/ms/icons/yellow-dot.png'
                elif safety_score >= 0.4:
                    icon = 'https://maps.google.com/mapfiles/ms/icons/orange-dot.png'
                else:
                    icon = 'https://maps.google.com/mapfiles/ms/icons/red-dot.png'
                
                # Create marker data
                marker = {
                    'position': {
                        'lat': coords['lat'],
                        'lng': coords['lng']
                    },
                    'title': f"{location} - Safety: {analysis['safety_level']} ({safety_score:.2f})",
                    'icon': icon,
                    'location': location,
                    'safety_score': safety_score,
                    'safety_level': analysis['safety_level'],
                    'infraction_count': analysis.get('infraction_analysis', {}).get('total_count', 0),
                }
                markers.append(marker)
        
        print(f"🗺️ Created {len(markers)} markers")
        
        # Print first few markers for debugging
        for i, marker in enumerate(markers[:3]):
            print(f"   Marker {i+1}: {marker['location']} at ({marker['position']['lat']:.4f}, {marker['position']['lng']:.4f})")
        
        return {
            'markers': markers,
            'total_locations': len(markers),
            'center': {'lat': 43.4723, 'lng': -80.5449}
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {'error': str(e), 'markers': []}

def test_plot_data():
    """Test the plot data function"""
    print("🔥 TESTING PLOT DATA FUNCTION")
    print("=" * 50)
    
    result = get_plot_data()
    
    if 'error' in result:
        print(f"❌ Error: {result['error']}")
        return False
    
    markers = result['markers']
    print(f"✅ Success! Generated {len(markers)} markers")
    
    if markers:
        print("\n📍 Sample markers:")
        for marker in markers[:5]:  # Show first 5
            pos = marker['position']
            print(f"   • {marker['location']}: ({pos['lat']:.4f}, {pos['lng']:.4f}) - {marker['safety_level']}")
        
        # Save to file for inspection
        with open('plot_data_test.json', 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n💾 Saved full data to 'plot_data_test.json'")
        
        return True
    else:
        print("❌ No markers generated!")
        return False

if __name__ == "__main__":
    success = test_plot_data()
    if success:
        print("\n🎉 Plot data function is working!")
    else:
        print("\n💥 Plot data function failed!") 