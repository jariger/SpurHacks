import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from collections import defaultdict

class SafetyPredictor:
    def __init__(self):
        self.safety_thresholds = {
            'very_safe': 0.1,      # Less than 10% infraction rate
            'safe': 0.25,          # Less than 25% infraction rate
            'moderate': 0.5,       # Less than 50% infraction rate
            'risky': 0.75,         # Less than 75% infraction rate
            'dangerous': 1.0       # 75%+ infraction rate
        }
        
        self.safety_colors = {
            'very_safe': '#00FF00',    # Green
            'safe': '#90EE90',         # Light Green
            'moderate': '#FFFF00',     # Yellow
            'risky': '#FFA500',        # Orange
            'dangerous': '#FF0000'     # Red
        }
    
    def analyze_parking_safety(self, bylaw_data: List[Dict], parking_data: List[Dict]) -> Dict[str, Dict]:
        """
        Analyze parking safety for each location based on infraction data
        
        Args:
            bylaw_data: List of bylaw infraction records
            parking_data: List of parking location records
        
        Returns:
            Dictionary with safety analysis for each location
        """
        # Group infractions by location
        location_infractions = self._group_infractions_by_location(bylaw_data)
        
        # Calculate safety scores for each location
        safety_analysis = {}
        
        for location, infractions in location_infractions.items():
            safety_score = self._calculate_safety_score(infractions, parking_data)
            safety_analysis[location] = safety_score
        
        return safety_analysis
    
    def _group_infractions_by_location(self, bylaw_data: List[Dict]) -> Dict[str, List[Dict]]:
        """Group infraction records by location"""
        location_groups = defaultdict(list)
        
        for record in bylaw_data:
            location = record.get('Location', 'Unknown')
            location_groups[location].append(record)
        
        return dict(location_groups)
    
    def _calculate_safety_score(self, infractions: List[Dict], parking_data: List[Dict]) -> Dict:
        """
        Calculate safety score for a location based on infraction patterns
        
        Args:
            infractions: List of infraction records for this location
            parking_data: All parking data for context
        
        Returns:
            Dictionary with safety metrics and score
        """
        if not infractions:
            return {
                'safety_level': 'very_safe',
                'safety_score': 1.0,
                'infraction_count': 0,
                'infraction_rate': 0.0,
                'recent_infractions': 0,
                'severity_score': 0.0,
                'color': self.safety_colors['very_safe'],
                'recommendation': 'Safe to park - no recent infractions'
            }
        
        # Calculate basic metrics
        total_infractions = len(infractions)
        
        # Calculate recent infractions (last 30 days)
        recent_date = datetime.now() - timedelta(days=30)
        recent_infractions = 0
        
        for infraction in infractions:
            try:
                infraction_date = datetime.strptime(infraction.get('Date', ''), '%Y-%m-%d')
                if infraction_date >= recent_date:
                    recent_infractions += 1
            except:
                pass
        
        # Calculate severity score based on infraction types
        severity_score = self._calculate_severity_score(infractions)
        
        # Calculate infraction rate (infractions per parking spot)
        parking_spots_in_area = self._estimate_parking_spots(infractions[0].get('Location', ''), parking_data)
        infraction_rate = total_infractions / max(parking_spots_in_area, 1)
        
        # Calculate overall safety score (0-1, where 1 is safest)
        safety_score = self._calculate_overall_safety_score(
            total_infractions, recent_infractions, severity_score, infraction_rate
        )
        
        # Determine safety level
        safety_level = self._determine_safety_level(safety_score)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(safety_level, total_infractions, recent_infractions)
        
        return {
            'safety_level': safety_level,
            'safety_score': safety_score,
            'infraction_count': total_infractions,
            'infraction_rate': infraction_rate,
            'recent_infractions': recent_infractions,
            'severity_score': severity_score,
            'color': self.safety_colors[safety_level],
            'recommendation': recommendation
        }
    
    def _calculate_severity_score(self, infractions: List[Dict]) -> float:
        """Calculate severity score based on infraction types"""
        severity_weights = {
            'No Parking': 1.0,
            'Expired Meter': 0.7,
            'Overtime Parking': 0.8,
            'Fire Route': 1.5,
            'Handicap': 1.3,
            'Loading Zone': 0.9,
            'Reserved': 1.2
        }
        
        total_severity = 0
        for infraction in infractions:
            infraction_type = infraction.get('Infraction_Type', 'Unknown')
            weight = severity_weights.get(infraction_type, 1.0)
            total_severity += weight
        
        return total_severity / len(infractions) if infractions else 0
    
    def _estimate_parking_spots(self, location: str, parking_data: List[Dict]) -> int:
        """Estimate number of parking spots in the area"""
        # This is a simplified estimation
        # In a real implementation, you might use actual parking spot data
        location_parking = [p for p in parking_data if location.lower() in p.get('Location', '').lower()]
        return len(location_parking) if location_parking else 10  # Default estimate
    
    def _calculate_overall_safety_score(self, total_infractions: int, recent_infractions: int, 
                                      severity_score: float, infraction_rate: float) -> float:
        """
        Calculate overall safety score (0-1, where 1 is safest)
        
        Formula considers:
        - Total infractions (weighted less)
        - Recent infractions (weighted more)
        - Severity of infractions
        - Infraction rate per parking spot
        """
        # Normalize factors
        total_factor = max(0, 1 - (total_infractions / 100))  # Cap at 100 infractions
        recent_factor = max(0, 1 - (recent_infractions / 20))  # Cap at 20 recent infractions
        severity_factor = max(0, 1 - (severity_score / 2))  # Cap at severity 2
        rate_factor = max(0, 1 - (infraction_rate / 5))  # Cap at 5 infractions per spot
        
        # Weighted average (recent infractions weighted more heavily)
        safety_score = (
            total_factor * 0.2 +
            recent_factor * 0.4 +
            severity_factor * 0.2 +
            rate_factor * 0.2
        )
        
        return max(0, min(1, safety_score))  # Ensure between 0 and 1
    
    def _determine_safety_level(self, safety_score: float) -> str:
        """Determine safety level based on safety score"""
        if safety_score >= 0.8:
            return 'very_safe'
        elif safety_score >= 0.6:
            return 'safe'
        elif safety_score >= 0.4:
            return 'moderate'
        elif safety_score >= 0.2:
            return 'risky'
        else:
            return 'dangerous'
    
    def _generate_recommendation(self, safety_level: str, total_infractions: int, recent_infractions: int) -> str:
        """Generate parking recommendation based on safety level"""
        recommendations = {
            'very_safe': f"Very safe to park here. Only {total_infractions} total infractions, {recent_infractions} recent.",
            'safe': f"Generally safe to park here. {total_infractions} total infractions, {recent_infractions} recent.",
            'moderate': f"Moderate risk. {total_infractions} total infractions, {recent_infractions} recent. Consider alternatives.",
            'risky': f"Risky parking area. {total_infractions} total infractions, {recent_infractions} recent. High chance of ticket.",
            'dangerous': f"Dangerous parking area! {total_infractions} total infractions, {recent_infractions} recent. Avoid if possible."
        }
        
        return recommendations.get(safety_level, "Safety level unknown")
    
    def predict_safety_for_new_location(self, location: str, bylaw_data: List[Dict]) -> Dict:
        """
        Predict safety for a new location based on similar patterns
        
        Args:
            location: New location to predict safety for
            bylaw_data: Historical bylaw data
        
        Returns:
            Predicted safety metrics
        """
        # Find similar locations based on street name patterns
        similar_locations = self._find_similar_locations(location, bylaw_data)
        
        if not similar_locations:
            return {
                'safety_level': 'moderate',
                'safety_score': 0.5,
                'prediction_confidence': 'low',
                'recommendation': 'Limited data available. Park with caution.'
            }
        
        # Calculate average safety metrics from similar locations
        avg_safety_score = np.mean([loc['safety_score'] for loc in similar_locations])
        avg_infractions = np.mean([loc['infraction_count'] for loc in similar_locations])
        
        safety_level = self._determine_safety_level(avg_safety_score)
        
        return {
            'safety_level': safety_level,
            'safety_score': avg_safety_score,
            'prediction_confidence': 'medium',
            'similar_locations_analyzed': len(similar_locations),
            'avg_infractions': avg_infractions,
            'recommendation': f"Based on {len(similar_locations)} similar locations. {self._generate_recommendation(safety_level, int(avg_infractions), 0)}"
        }
    
    def _find_similar_locations(self, location: str, bylaw_data: List[Dict]) -> List[Dict]:
        """Find locations with similar street patterns"""
        location_words = set(location.lower().split())
        similar_locations = []
        
        # Group by location and find similar patterns
        location_groups = self._group_infractions_by_location(bylaw_data)
        
        for loc, infractions in location_groups.items():
            loc_words = set(loc.lower().split())
            # Calculate similarity based on common words
            common_words = location_words.intersection(loc_words)
            if len(common_words) >= 1:  # At least one common word
                safety_score = self._calculate_safety_score(infractions, [])
                similar_locations.append({
                    'location': loc,
                    'safety_score': safety_score['safety_score'],
                    'infraction_count': safety_score['infraction_count']
                })
        
        return similar_locations 