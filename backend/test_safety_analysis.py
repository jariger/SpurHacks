#!/usr/bin/env python3
"""
Test script to analyze and display safety scores for all parking locations
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from data_processor import DataProcessor
from safety_predictor import SafetyPredictor
from collections import defaultdict
import pandas as pd

def main():
    load_dotenv()
    
    print("🛡️  PARKING SAFETY ANALYSIS TEST")
    print("=" * 80)
    
    # Initialize services
    print("🚀 Initializing services...")
    data_processor = DataProcessor()
    safety_predictor = SafetyPredictor()
    
    # Load data
    print("\n📁 Loading CSV data...")
    data = data_processor.load_csv_data()
    
    if not data:
        print("❌ No data loaded. Please check your CSV files.")
        return
    
    # Add coordinates if geocoding is available
    print("\n🗺️  Processing coordinates...")
    data_with_coords = data_processor.add_coordinates_to_data(data)
    
    # Perform safety analysis
    print("\n🛡️  Performing safety analysis...")
    safety_data = safety_predictor.analyze_parking_safety(
        data_with_coords.get('bylaw_infractions', []),
        data_with_coords.get('parking_on_street', [])
    )
    
    # Display comprehensive results
    display_safety_results(safety_data, data_with_coords)
    
    # Export results to files
    export_safety_results(safety_data, data_with_coords)
    
    print("\n" + "=" * 80)
    print("✅ SAFETY ANALYSIS COMPLETED!")

def display_safety_results(safety_data, data_with_coords):
    """Display comprehensive safety analysis results"""
    
    print("\n📊 SAFETY ANALYSIS RESULTS")
    print("=" * 80)
    
    if not safety_data:
        print("❌ No safety data available. This might happen if:")
        print("   - No bylaw infractions data found")
        print("   - No matching locations between infractions and parking data")
        return
    
    # Overall statistics
    total_locations = len(safety_data)
    safety_counts = defaultdict(int)
    
    for location, analysis in safety_data.items():
        safety_counts[analysis['safety_level']] += 1
    
    print(f"📍 Total locations analyzed: {total_locations}")
    print(f"📊 Safety level distribution:")
    for level, count in safety_counts.items():
        percentage = (count / total_locations * 100) if total_locations > 0 else 0
        emoji = get_safety_emoji(level)
        print(f"   {emoji} {level.replace('_', ' ').title()}: {count} locations ({percentage:.1f}%)")
    
    # Detailed location analysis
    print(f"\n📋 DETAILED LOCATION ANALYSIS")
    print("-" * 80)
    
    # Sort locations by safety score (safest first)
    sorted_locations = sorted(
        safety_data.items(), 
        key=lambda x: x[1]['safety_score'], 
        reverse=True
    )
    
    print(f"{'Rank':<4} {'Location':<35} {'Safety Level':<12} {'Score':<6} {'Infractions':<11} {'Recent':<6}")
    print("-" * 80)
    
    for rank, (location, analysis) in enumerate(sorted_locations, 1):
        emoji = get_safety_emoji(analysis['safety_level'])
        score_str = f"{analysis['safety_score']:.3f}"
        level_str = f"{emoji} {analysis['safety_level'].replace('_', ' ').title()}"
        
        print(f"{rank:<4} {location[:34]:<35} {level_str:<20} {score_str:<6} "
              f"{analysis['infraction_count']:<11} {analysis['recent_infractions']:<6}")
    
    # Show top 10 safest locations
    print(f"\n🏆 TOP 10 SAFEST PARKING LOCATIONS")
    print("-" * 60)
    
    for i, (location, analysis) in enumerate(sorted_locations[:10], 1):
        emoji = get_safety_emoji(analysis['safety_level'])
        print(f"{i:2d}. {emoji} {location}")
        print(f"    Safety Score: {analysis['safety_score']:.1%}")
        print(f"    Total Infractions: {analysis['infraction_count']}")
        print(f"    Recent Infractions: {analysis['recent_infractions']}")
        print(f"    Recommendation: {analysis['recommendation']}")
        print()
    
    # Show top 10 most dangerous locations
    print(f"\n⚠️  TOP 10 MOST DANGEROUS PARKING LOCATIONS")
    print("-" * 60)
    
    dangerous_locations = sorted_locations[-10:][::-1]  # Last 10, reversed
    
    for i, (location, analysis) in enumerate(dangerous_locations, 1):
        emoji = get_safety_emoji(analysis['safety_level'])
        print(f"{i:2d}. {emoji} {location}")
        print(f"    Safety Score: {analysis['safety_score']:.1%}")
        print(f"    Total Infractions: {analysis['infraction_count']}")
        print(f"    Recent Infractions: {analysis['recent_infractions']}")
        print(f"    Recommendation: {analysis['recommendation']}")
        print()
    
    # Safety score distribution
    print(f"\n📈 SAFETY SCORE DISTRIBUTION")
    print("-" * 40)
    
    scores = [analysis['safety_score'] for analysis in safety_data.values()]
    if scores:
        print(f"Average Safety Score: {sum(scores)/len(scores):.3f}")
        print(f"Highest Safety Score: {max(scores):.3f}")
        print(f"Lowest Safety Score: {min(scores):.3f}")
        print(f"Standard Deviation: {calculate_std_dev(scores):.3f}")
    
    # Infraction analysis
    print(f"\n🚨 INFRACTION ANALYSIS")
    print("-" * 40)
    
    total_infractions = sum(analysis['infraction_count'] for analysis in safety_data.values())
    total_recent = sum(analysis['recent_infractions'] for analysis in safety_data.values())
    
    print(f"Total Infractions: {total_infractions:,}")
    print(f"Recent Infractions (30 days): {total_recent:,}")
    print(f"Average Infractions per Location: {total_infractions/total_locations:.1f}")
    print(f"Average Recent per Location: {total_recent/total_locations:.1f}")
    
    # Show locations by infraction count
    infraction_sorted = sorted(
        safety_data.items(),
        key=lambda x: x[1]['infraction_count'],
        reverse=True
    )
    
    print(f"\n🔥 LOCATIONS WITH MOST INFRACTIONS")
    print("-" * 50)
    
    for location, analysis in infraction_sorted[:10]:
        print(f"{location[:40]:<40} {analysis['infraction_count']:>6} infractions")

def get_safety_emoji(safety_level):
    """Get emoji for safety level"""
    emojis = {
        'very_safe': '🟢',
        'safe': '🟡',
        'moderate': '🟠',
        'risky': '🔴',
        'dangerous': '⚫'
    }
    return emojis.get(safety_level, '⚪')

def calculate_std_dev(values):
    """Calculate standard deviation"""
    if not values:
        return 0
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return variance ** 0.5

def export_safety_results(safety_data, data_with_coords):
    """Export safety results to files"""
    
    print(f"\n💾 EXPORTING SAFETY RESULTS")
    print("-" * 40)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create output directory
    output_dir = 'safety_analysis_output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 Created output directory: {output_dir}")
    
    # Export to JSON
    json_filename = f"{output_dir}/safety_analysis_{timestamp}.json"
    with open(json_filename, 'w') as f:
        json.dump(safety_data, f, indent=2, default=str)
    print(f"📄 JSON export: {json_filename}")
    
    # Export to CSV
    csv_filename = f"{output_dir}/safety_analysis_{timestamp}.csv"
    
    # Prepare data for CSV
    csv_data = []
    for location, analysis in safety_data.items():
        csv_data.append({
            'Location': location,
            'Safety_Level': analysis['safety_level'],
            'Safety_Score': analysis['safety_score'],
            'Safety_Percentage': f"{analysis['safety_score']:.1%}",
            'Infraction_Count': analysis['infraction_count'],
            'Recent_Infractions': analysis['recent_infractions'],
            'Infraction_Rate': analysis['infraction_rate'],
            'Severity_Score': analysis['severity_score'],
            'Color': analysis['color'],
            'Recommendation': analysis['recommendation']
        })
    
    # Sort by safety score (safest first)
    csv_data.sort(key=lambda x: x['Safety_Score'], reverse=True)
    
    # Add rank
    for i, row in enumerate(csv_data, 1):
        row['Safety_Rank'] = i
    
    # Write CSV
    if csv_data:
        df = pd.DataFrame(csv_data)
        df.to_csv(csv_filename, index=False)
        print(f"📊 CSV export: {csv_filename}")
    
    # Export detailed report
    report_filename = f"{output_dir}/safety_report_{timestamp}.txt"
    with open(report_filename, 'w') as f:
        f.write("WATERLOO PARKING SAFETY ANALYSIS REPORT\n")
        f.write("=" * 50 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("SUMMARY STATISTICS\n")
        f.write("-" * 20 + "\n")
        f.write(f"Total locations analyzed: {len(safety_data)}\n")
        
        # Safety level counts
        safety_counts = defaultdict(int)
        for analysis in safety_data.values():
            safety_counts[analysis['safety_level']] += 1
        
        f.write("\nSafety Level Distribution:\n")
        for level, count in safety_counts.items():
            percentage = (count / len(safety_data) * 100) if safety_data else 0
            f.write(f"  {level.replace('_', ' ').title()}: {count} ({percentage:.1f}%)\n")
        
        f.write("\nDETAILED LOCATION ANALYSIS\n")
        f.write("-" * 30 + "\n")
        
        # Sort and write all locations
        sorted_locations = sorted(
            safety_data.items(),
            key=lambda x: x[1]['safety_score'],
            reverse=True
        )
        
        for rank, (location, analysis) in enumerate(sorted_locations, 1):
            f.write(f"\n{rank}. {location}\n")
            f.write(f"   Safety Level: {analysis['safety_level'].replace('_', ' ').title()}\n")
            f.write(f"   Safety Score: {analysis['safety_score']:.3f} ({analysis['safety_score']:.1%})\n")
            f.write(f"   Total Infractions: {analysis['infraction_count']}\n")
            f.write(f"   Recent Infractions: {analysis['recent_infractions']}\n")
            f.write(f"   Infraction Rate: {analysis['infraction_rate']:.2f}\n")
            f.write(f"   Severity Score: {analysis['severity_score']:.2f}\n")
            f.write(f"   Recommendation: {analysis['recommendation']}\n")
    
    print(f"📝 Report export: {report_filename}")
    
    # Export summary statistics
    stats_filename = f"{output_dir}/safety_statistics_{timestamp}.json"
    
    scores = [analysis['safety_score'] for analysis in safety_data.values()]
    infractions = [analysis['infraction_count'] for analysis in safety_data.values()]
    
    stats = {
        'timestamp': datetime.now().isoformat(),
        'total_locations': len(safety_data),
        'safety_distribution': dict(safety_counts),
        'score_statistics': {
            'mean': sum(scores) / len(scores) if scores else 0,
            'min': min(scores) if scores else 0,
            'max': max(scores) if scores else 0,
            'std_dev': calculate_std_dev(scores)
        },
        'infraction_statistics': {
            'total': sum(infractions),
            'mean_per_location': sum(infractions) / len(infractions) if infractions else 0,
            'min': min(infractions) if infractions else 0,
            'max': max(infractions) if infractions else 0
        }
    }
    
    with open(stats_filename, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"📈 Statistics export: {stats_filename}")
    
    print(f"\n✅ All exports completed in: {output_dir}/")

def test_individual_location(location_name):
    """Test safety analysis for a specific location"""
    
    print(f"\n🔍 TESTING SPECIFIC LOCATION: {location_name}")
    print("-" * 50)
    
    # Initialize services
    data_processor = DataProcessor()
    safety_predictor = SafetyPredictor()
    
    # Load data
    data = data_processor.load_csv_data()
    data_with_coords = data_processor.add_coordinates_to_data(data)
    
    # Perform safety analysis
    safety_data = safety_predictor.analyze_parking_safety(
        data_with_coords.get('bylaw_infractions', []),
        data_with_coords.get('parking_on_street', [])
    )
    
    # Find matching locations
    matching_locations = [
        (loc, analysis) for loc, analysis in safety_data.items()
        if location_name.lower() in loc.lower()
    ]
    
    if matching_locations:
        print(f"Found {len(matching_locations)} matching location(s):")
        for location, analysis in matching_locations:
            emoji = get_safety_emoji(analysis['safety_level'])
            print(f"\n{emoji} {location}")
            print(f"   Safety Level: {analysis['safety_level'].replace('_', ' ').title()}")
            print(f"   Safety Score: {analysis['safety_score']:.3f} ({analysis['safety_score']:.1%})")
            print(f"   Total Infractions: {analysis['infraction_count']}")
            print(f"   Recent Infractions: {analysis['recent_infractions']}")
            print(f"   Recommendation: {analysis['recommendation']}")
    else:
        print(f"❌ No locations found matching '{location_name}'")
        print("\nAvailable locations:")
        for i, location in enumerate(list(safety_data.keys())[:10], 1):
            print(f"   {i}. {location}")
        if len(safety_data) > 10:
            print(f"   ... and {len(safety_data) - 10} more locations")

if __name__ == "__main__":
    main()
    
    # Uncomment to test a specific location
    # test_individual_location("UNIVERSITY") 