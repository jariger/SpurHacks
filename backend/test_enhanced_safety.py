#!/usr/bin/env python3
"""
Test the enhanced safety analysis system
"""

from data_processor import DataProcessor
from enhanced_safety_predictor import EnhancedSafetyPredictor
from dotenv import load_dotenv
import json

def test_enhanced_safety_analysis():
    load_dotenv()
    
    print("🛡️ ENHANCED PARKING SAFETY ANALYSIS")
    print("=" * 60)
    
    # Initialize services
    data_processor = DataProcessor()
    enhanced_predictor = EnhancedSafetyPredictor()
    
    # Load all data
    print("📁 Loading comprehensive parking data...")
    data = data_processor.load_csv_data()
    data_with_coords = data_processor.add_coordinates_to_data(data)
    
    # Perform enhanced analysis
    print("🔍 Performing enhanced safety analysis...")
    safety_analysis = enhanced_predictor.analyze_comprehensive_parking_safety(
        data_with_coords.get('bylaw_infractions', []),
        data_with_coords.get('parking_on_street', []),
        data_with_coords.get('parking_lots', [])
    )
    
    if not safety_analysis:
        print("❌ No safety analysis data generated")
        return
    
    print(f"\n📊 Analysis completed for {len(safety_analysis)} locations")
    
    # Show detailed analysis for top locations
    show_detailed_location_analysis(safety_analysis)
    
    # Show safety distribution
    show_safety_distribution(safety_analysis)
    
    # Show specific examples
    show_location_examples(safety_analysis)
    
    # Export detailed results
    export_enhanced_results(safety_analysis)

def show_detailed_location_analysis(safety_analysis: dict):
    """Show detailed analysis for top locations"""
    
    print(f"\n🏆 TOP 5 LOCATIONS - DETAILED ANALYSIS")
    print("=" * 60)
    
    # Sort by safety score
    sorted_locations = sorted(
        safety_analysis.items(), 
        key=lambda x: x[1]['safety_score'], 
        reverse=True
    )
    
    for i, (location, analysis) in enumerate(sorted_locations[:5], 1):
        print(f"\n{i}. 📍 {location}")
        print(f"   Safety Level: {analysis['safety_level'].replace('_', ' ').title()}")
        print(f"   Safety Score: {analysis['safety_score']:.1%}")
        
        # Infraction details
        infraction = analysis['infraction_analysis']
        print(f"   🚨 Infractions: {infraction['total_count']} total, {infraction['recent_count']} recent")
        if infraction['most_common_violation'] != 'None':
            print(f"   ⚠️  Common violation: {infraction['most_common_violation']}")
        
        # Street parking details
        street = analysis['street_parking_analysis']
        if street['total_spaces'] > 0:
            print(f"   🅿️  Street parking: {street['total_spaces']} spaces")
            if street['free_hours_available']:
                print(f"   ✅ Free parking: {', '.join(street['free_parking_details'])}")
            if street['has_metered_parking']:
                print(f"   💰 Metered parking available")
        else:
            print(f"   ❌ No street parking spaces")
        
        # Parking lot details
        lots = analysis['parking_lots_analysis']
        if lots['available_lots'] > 0:
            print(f"   🏢 Nearby lots: {lots['available_lots']}")
            if lots['free_options']:
                print(f"   ✅ Free lot options: {', '.join(lots['free_options'])}")
        
        # Recommendations
        print(f"   💡 Key recommendations:")
        for rec in analysis['recommendations'][:3]:
            print(f"      • {rec}")
        
        print(f"   🧠 Reasoning: {analysis['reasoning']}")

def show_safety_distribution(safety_analysis: dict):
    """Show distribution of safety levels"""
    
    print(f"\n📊 SAFETY LEVEL DISTRIBUTION")
    print("-" * 40)
    
    # Count by safety level
    levels = {'very_safe': 0, 'safe': 0, 'moderate': 0, 'risky': 0, 'dangerous': 0}
    for analysis in safety_analysis.values():
        level = analysis['safety_level']
        if level in levels:
            levels[level] += 1
    
    total = sum(levels.values())
    emojis = {'very_safe': '🟢', 'safe': '🟡', 'moderate': '🟠', 'risky': '🔴', 'dangerous': '⚫'}
    
    for level, count in levels.items():
        percentage = (count / total * 100) if total > 0 else 0
        emoji = emojis.get(level, '⚪')
        print(f"   {emoji} {level.replace('_', ' ').title():<12}: {count:3d} locations ({percentage:5.1f}%)")

def show_location_examples(safety_analysis: dict):
    """Show specific examples of different safety scenarios"""
    
    print(f"\n🔍 LOCATION EXAMPLES BY SCENARIO")
    print("=" * 50)
    
    # Find examples of different scenarios
    scenarios = {
        'free_parking_available': [],
        'high_infractions': [],
        'metered_parking': [],
        'parking_lots_nearby': [],
        'no_parking_options': []
    }
    
    for location, analysis in safety_analysis.items():
        # Free parking available
        if analysis['street_parking_analysis']['free_hours_available']:
            scenarios['free_parking_available'].append((location, analysis))
        
        # High infractions
        if analysis['infraction_analysis']['total_count'] > 20:
            scenarios['high_infractions'].append((location, analysis))
        
        # Metered parking
        if analysis['street_parking_analysis']['has_metered_parking']:
            scenarios['metered_parking'].append((location, analysis))
        
        # Parking lots nearby
        if analysis['parking_lots_analysis']['available_lots'] > 0:
            scenarios['parking_lots_nearby'].append((location, analysis))
        
        # No parking options
        if (analysis['street_parking_analysis']['total_spaces'] == 0 and 
            analysis['parking_lots_analysis']['available_lots'] == 0):
            scenarios['no_parking_options'].append((location, analysis))
    
    # Show examples
    for scenario, locations in scenarios.items():
        if locations:
            print(f"\n🔸 {scenario.replace('_', ' ').title()}:")
            for location, analysis in locations[:3]:  # Show first 3 examples
                score = analysis['safety_score']
                level = analysis['safety_level'].replace('_', ' ').title()
                print(f"   • {location} (Safety: {score:.1%} - {level})")

def export_enhanced_results(safety_analysis: dict):
    """Export enhanced results to JSON file"""
    
    print(f"\n💾 EXPORTING ENHANCED RESULTS")
    print("-" * 35)
    
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create output directory
    import os
    output_dir = 'enhanced_safety_output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Export comprehensive analysis
    filename = f"{output_dir}/enhanced_safety_analysis_{timestamp}.json"
    with open(filename, 'w') as f:
        json.dump(safety_analysis, f, indent=2, default=str)
    
    print(f"✅ Enhanced analysis exported: {filename}")
    
    # Create summary report
    summary_filename = f"{output_dir}/safety_summary_{timestamp}.txt"
    with open(summary_filename, 'w') as f:
        f.write("ENHANCED PARKING SAFETY ANALYSIS SUMMARY\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total locations analyzed: {len(safety_analysis)}\n\n")
        
        # Safety distribution
        levels = {'very_safe': 0, 'safe': 0, 'moderate': 0, 'risky': 0, 'dangerous': 0}
        for analysis in safety_analysis.values():
            levels[analysis['safety_level']] += 1
        
        f.write("SAFETY DISTRIBUTION:\n")
        for level, count in levels.items():
            f.write(f"  {level.replace('_', ' ').title()}: {count} locations\n")
        
        f.write("\nTOP 10 SAFEST LOCATIONS:\n")
        sorted_locations = sorted(safety_analysis.items(), key=lambda x: x[1]['safety_score'], reverse=True)
        for i, (location, analysis) in enumerate(sorted_locations[:10], 1):
            f.write(f"  {i:2d}. {location} ({analysis['safety_score']:.1%})\n")
    
    print(f"✅ Summary report exported: {summary_filename}")

if __name__ == "__main__":
    test_enhanced_safety_analysis() 