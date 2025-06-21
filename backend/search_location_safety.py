#!/usr/bin/env python3
"""
Search for safety information of specific locations
"""

from data_processor import DataProcessor
from safety_predictor import SafetyPredictor
from dotenv import load_dotenv
import sys

def search_location_safety(search_term):
    load_dotenv()
    
    print(f"🔍 SEARCHING FOR: '{search_term}'")
    print("=" * 50)
    
    # Initialize and load data
    data_processor = DataProcessor()
    safety_predictor = SafetyPredictor()
    
    data = data_processor.load_csv_data()
    data_with_coords = data_processor.add_coordinates_to_data(data)
    
    safety_data = safety_predictor.analyze_parking_safety(
        data_with_coords.get('bylaw_infractions', []),
        data_with_coords.get('parking_on_street', [])
    )
    
    # Search for matching locations
    matches = []
    search_lower = search_term.lower()
    
    for location, analysis in safety_data.items():
        if search_lower in location.lower():
            matches.append((location, analysis))
    
    if matches:
        print(f"Found {len(matches)} matching location(s):\n")
        
        # Sort by safety score
        matches.sort(key=lambda x: x[1]['safety_score'], reverse=True)
        
        emojis = {'very_safe': '🟢', 'safe': '🟡', 'moderate': '🟠', 'risky': '🔴', 'dangerous': '⚫'}
        
        for i, (location, analysis) in enumerate(matches, 1):
            emoji = emojis.get(analysis['safety_level'], '⚪')
            print(f"{i}. {emoji} {location}")
            print(f"   Safety Level: {analysis['safety_level'].replace('_', ' ').title()}")
            print(f"   Safety Score: {analysis['safety_score']:.3f} ({analysis['safety_score']:.1%})")
            print(f"   Total Infractions: {analysis['infraction_count']}")
            print(f"   Recent Infractions: {analysis['recent_infractions']}")
            print(f"   💡 {analysis['recommendation']}")
            print()
    else:
        print(f"❌ No locations found matching '{search_term}'")
        print("\nTry searching for:")
        print("   - Street names: 'UNIVERSITY', 'KING', 'COLLEGE'")
        print("   - Partial names: 'ST', 'AVE', 'STREET'")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        search_term = " ".join(sys.argv[1:])
        search_location_safety(search_term)
    else:
        print("Usage: python search_location_safety.py <location_name>")
        print("Example: python search_location_safety.py UNIVERSITY") 