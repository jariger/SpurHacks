#!/usr/bin/env python3
"""
Quick safety test - shows just the essential safety information
"""

from data_processor import DataProcessor
from safety_predictor import SafetyPredictor
from dotenv import load_dotenv

def quick_safety_test():
    load_dotenv()
    
    print("🛡️  QUICK SAFETY TEST")
    print("=" * 50)
    
    # Initialize and load data
    data_processor = DataProcessor()
    safety_predictor = SafetyPredictor()
    
    print("Loading data...")
    data = data_processor.load_csv_data()
    data_with_coords = data_processor.add_coordinates_to_data(data)
    
    print("Analyzing safety...")
    safety_data = safety_predictor.analyze_parking_safety(
        data_with_coords.get('bylaw_infractions', []),
        data_with_coords.get('parking_on_street', [])
    )
    
    if not safety_data:
        print("❌ No safety data generated")
        return
    
    print(f"\n📊 Found {len(safety_data)} locations with safety analysis")
    
    # Count by safety level
    levels = {'very_safe': 0, 'safe': 0, 'moderate': 0, 'risky': 0, 'dangerous': 0}
    for analysis in safety_data.values():
        level = analysis['safety_level']
        if level in levels:
            levels[level] += 1
    
    print("\n🎨 Safety Distribution:")
    emojis = {'very_safe': '🟢', 'safe': '🟡', 'moderate': '🟠', 'risky': '🔴', 'dangerous': '⚫'}
    for level, count in levels.items():
        emoji = emojis.get(level, '⚪')
        print(f"   {emoji} {level.replace('_', ' ').title()}: {count} locations")
    
    # Show top 5 safest and most dangerous
    sorted_locations = sorted(safety_data.items(), key=lambda x: x[1]['safety_score'], reverse=True)
    
    print("\n🏆 TOP 5 SAFEST LOCATIONS:")
    for i, (location, analysis) in enumerate(sorted_locations[:5], 1):
        emoji = emojis.get(analysis['safety_level'], '⚪')
        score = analysis['safety_score']
        infractions = analysis['infraction_count']
        print(f"   {i}. {emoji} {location[:40]} (Score: {score:.2f}, Infractions: {infractions})")
    
    print("\n⚠️  TOP 5 MOST DANGEROUS LOCATIONS:")
    for i, (location, analysis) in enumerate(sorted_locations[-5:][::-1], 1):
        emoji = emojis.get(analysis['safety_level'], '⚪')
        score = analysis['safety_score']
        infractions = analysis['infraction_count']
        print(f"   {i}. {emoji} {location[:40]} (Score: {score:.2f}, Infractions: {infractions})")
    
    print("\n✅ Quick safety test completed!")

if __name__ == "__main__":
    quick_safety_test() 