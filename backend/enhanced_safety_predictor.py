import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta, time
from collections import defaultdict
import re

class EnhancedSafetyPredictor:
    def __init__(self):
        self.safety_thresholds = {
            'very_safe': 0.8,      # 80%+ safety score
            'safe': 0.6,           # 60-79% safety score
            'moderate': 0.4,       # 40-59% safety score
            'risky': 0.2,          # 20-39% safety score
            'dangerous': 0.0       # 0-19% safety score
        }
        
        self.safety_colors = {
            'very_safe': '#00FF00',    # Green
            'safe': '#90EE90',         # Light Green
            'moderate': '#FFFF00',     # Yellow
            'risky': '#FFA500',        # Orange
            'dangerous': '#FF0000'     # Red
        }
        
        # Infraction severity weights
        self.infraction_severity = {
            'NO PARKING': 1.5,
            'PERMIT PARKING ONLY': 1.3,
            'FIRE ROUTE': 2.0,
            'HANDICAP': 1.8,
            'LOADING ZONE': 1.2,
            'EXPIRED METER': 0.8,
            'OVERTIME PARKING': 0.9,
            'RESERVED': 1.4,
            'TIME LIMIT EXCEEDED': 0.7,
            'METER VIOLATION': 0.8
        }
    
    def analyze_comprehensive_parking_safety(self, bylaw_data: List[Dict], 
                                           parking_street_data: List[Dict], 
                                           parking_lots_data: List[Dict]) -> Dict[str, Dict]:
        """
        Comprehensive safety analysis considering all parking data types
        
        Args:
            bylaw_data: Bylaw infraction records
            parking_street_data: Street parking availability and rules
            parking_lots_data: Parking lot information
        
        Returns:
            Dictionary with comprehensive safety analysis for each location
        """
        print("🔍 Starting comprehensive parking safety analysis...")
        
        # Group data by location
        location_analysis = {}
        
        # Process each location mentioned in any dataset
        all_locations = self._extract_all_locations(bylaw_data, parking_street_data, parking_lots_data)
        
        print(f"📍 Found {len(all_locations)} unique locations to analyze")
        
        for location in all_locations:
            analysis = self._analyze_location_safety(
                location, bylaw_data, parking_street_data, parking_lots_data
            )
            location_analysis[location] = analysis
        
        return location_analysis
    
    def _extract_all_locations(self, bylaw_data: pd.DataFrame, 
                              parking_street_data: pd.DataFrame, 
                              parking_lots_data: pd.DataFrame) -> set:
        """Extract all unique locations from all datasets"""
        locations = set()
        
        # Extract from bylaw infractions
        if not bylaw_data.empty and 'STREET' in bylaw_data.columns:
            print(f"📍 Extracting locations from {len(bylaw_data)} bylaw infractions...")
            for _, record in bylaw_data.iterrows():
                street = record['STREET'] if pd.notna(record['STREET']) else ''
                if isinstance(street, str) and street.strip():
                    locations.add(street.strip().upper())
        
        # Extract from parking on street
        if not parking_street_data.empty and 'STREET' in parking_street_data.columns:
            print(f"📍 Extracting locations from {len(parking_street_data)} street parking records...")
            for _, record in parking_street_data.iterrows():
                street = record['STREET'] if pd.notna(record['STREET']) else ''
                if isinstance(street, str) and street.strip():
                    locations.add(street.strip().upper())
        
        # Extract from parking lots (using 'Address' field)
        if not parking_lots_data.empty and 'Address' in parking_lots_data.columns:
            print(f"📍 Extracting locations from {len(parking_lots_data)} parking lot records...")
            for _, record in parking_lots_data.iterrows():
                address = record['Address'] if pd.notna(record['Address']) else ''
                if isinstance(address, str) and address.strip():
                    locations.add(address.strip().upper())
        
        print(f"📍 Found {len(locations)} unique locations total")
        return locations
    
    def _extract_street_from_address(self, address: str) -> str:
        """Extract street name from full address"""
        # Remove numbers and extract street name
        # e.g., "100 REGINA ST S" -> "REGINA ST S"
        parts = address.split()
        if len(parts) > 1 and parts[0].isdigit():
            return ' '.join(parts[1:])
        return address
    
    def _analyze_location_safety(self, location: str, bylaw_data: List[Dict], 
                                parking_street_data: List[Dict], 
                                parking_lots_data: List[Dict]) -> Dict:
        """
        Comprehensive safety analysis for a specific location
        
        Returns detailed analysis including:
        - Safety score and level
        - Infraction analysis
        - Parking availability and rules
        - Time-based restrictions
        - Recommendations with reasoning
        """
        
        # 1. Analyze infractions at this location
        infractions = self._get_location_infractions(location, bylaw_data)
        infraction_analysis = self._analyze_infractions(infractions)
        
        # 2. Analyze street parking availability and rules
        street_parking = self._get_location_street_parking(location, parking_street_data)
        street_analysis = self._analyze_street_parking(street_parking)
        
        # 3. Analyze nearby parking lots
        nearby_lots = self._get_nearby_parking_lots(location, parking_lots_data)
        lot_analysis = self._analyze_parking_lots(nearby_lots)
        
        # 4. Calculate comprehensive safety score
        safety_score, score_details = self._calculate_comprehensive_safety_score(
            infraction_analysis, street_analysis, lot_analysis
        )
        
        # 5. Determine safety level
        safety_level = self._determine_safety_level(safety_score)
        
        # 6. Generate detailed recommendations with reasoning
        recommendations = self._generate_comprehensive_recommendations(
            safety_score, infraction_analysis, street_analysis, lot_analysis, score_details
        )
        
        return {
            'location': location,
            'safety_score': safety_score,
            'safety_level': safety_level,
            'color': self.safety_colors[safety_level],
            
            # Detailed analysis components
            'infraction_analysis': infraction_analysis,
            'street_parking_analysis': street_analysis,
            'parking_lots_analysis': lot_analysis,
            
            # Recommendations and reasoning
            'recommendations': recommendations,
            'reasoning': self._generate_safety_reasoning(
                safety_score, infraction_analysis, street_analysis, lot_analysis
            ),
            
            # Summary statistics
            'total_infractions': infraction_analysis['total_count'],
            'recent_infractions': infraction_analysis['recent_count'],
            'available_street_parking': street_analysis['total_spaces'],
            'free_parking_hours': street_analysis['free_hours_available'],
            'nearby_parking_lots': len(nearby_lots),
            
            # Time-based information
            'time_restrictions': self._get_time_restrictions(street_parking),
            'peak_infraction_times': infraction_analysis['peak_times'],
            'best_parking_times': self._determine_best_parking_times(
                street_analysis, infraction_analysis
            ),
            
            # Score details
            'score_details': score_details
        }
    
    def _get_location_infractions(self, location: str, bylaw_data: pd.DataFrame) -> List[Dict]:
        """Get all infractions for a specific location"""
        if bylaw_data.empty or 'STREET' not in bylaw_data.columns:
            return []
        
        # Filter infractions for this location
        location_infractions = bylaw_data[
            bylaw_data['STREET'].str.upper() == location.upper()
        ]
        
        infractions = []
        for _, record in location_infractions.iterrows():
            infraction = {
                'date': record.get('ISSUEDATE', ''),
                'reason': record.get('REASON', ''),
                'fine': record.get('VIOFINE', 0),
                'address': record.get('ADDRESS', ''),
                'street': record.get('STREET', '')
            }
            infractions.append(infraction)
        
        return infractions
    
    def _analyze_infractions(self, infractions: List[Dict]) -> Dict:
        """Analyze infraction patterns and severity"""
        if not infractions:
            return {
                'total_count': 0,
                'recent_count': 0,
                'severity_score': 0.0,
                'infraction_types': {},
                'peak_times': [],
                'temporal_pattern': 'No data',
                'average_fine': 0.0
            }
        
        # Count total and recent infractions
        recent_date = datetime.now() - timedelta(days=30)
        recent_count = 0
        
        # Analyze infraction types and severity
        infraction_types = defaultdict(int)
        total_severity = 0
        total_fines = 0
        fine_count = 0
        
        # Time pattern analysis
        time_patterns = defaultdict(int)
        
        for infraction in infractions:
            # Count infraction types
            reason = infraction.get('REASON', 'Unknown').upper()
            infraction_types[reason] += 1
            
            # Calculate severity
            severity = self._get_infraction_severity(reason)
            total_severity += severity
            
            # Analyze fines
            fine = infraction.get('VIOFINE', 0)
            if fine and str(fine).replace('.', '').isdigit():
                total_fines += float(fine)
                fine_count += 1
            
            # Check if recent
            issue_date = infraction.get('ISSUEDATE', '')
            if issue_date:
                try:
                    # Parse date (assuming format like "9/6/2018 12:00:00 AM")
                    date_obj = datetime.strptime(issue_date.split()[0], '%m/%d/%Y')
                    if date_obj >= recent_date:
                        recent_count += 1
                    
                    # Time pattern (hour of day, day of week)
                    hour = date_obj.hour if len(issue_date.split()) > 1 else 12
                    time_patterns[f"{hour:02d}:00"] += 1
                except:
                    pass
        
        # Calculate averages
        avg_severity = total_severity / len(infractions) if infractions else 0
        avg_fine = total_fines / fine_count if fine_count > 0 else 0
        
        # Find peak times
        peak_times = sorted(time_patterns.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            'total_count': len(infractions),
            'recent_count': recent_count,
            'severity_score': avg_severity,
            'infraction_types': dict(infraction_types),
            'peak_times': [time for time, count in peak_times],
            'temporal_pattern': self._analyze_temporal_pattern(infractions),
            'average_fine': avg_fine,
            'most_common_violation': max(infraction_types.items(), key=lambda x: x[1])[0] if infraction_types else 'None'
        }
    
    def _get_infraction_severity(self, reason: str) -> float:
        """Get severity weight for infraction type"""
        for key, weight in self.infraction_severity.items():
            if key in reason:
                return weight
        return 1.0  # Default severity
    
    def _get_location_street_parking(self, location: str, parking_street_data: pd.DataFrame) -> List[Dict]:
        """Get street parking info for a specific location"""
        if parking_street_data.empty or 'STREET' not in parking_street_data.columns:
            return []
        
        # Filter street parking for this location
        location_parking = parking_street_data[
            parking_street_data['STREET'].str.upper() == location.upper()
        ]
        
        parking_info = []
        for _, record in location_parking.iterrows():
            info = {
                'category': record.get('CATEGORY', ''),
                'subcategory': record.get('SUBCATEGORY', ''),
                'num_spaces': record.get('NUM_SPACES', 0),
                'parking_cost': record.get('PARKING_COST', ''),
                'hours': record.get('HOURS', ''),
                'days': record.get('DAYS', ''),
                'payment_method': record.get('PAYMENT_METHOD', ''),
                'max_rate': record.get('MAX_RATE', ''),
                'street': record.get('STREET', '')
            }
            parking_info.append(info)
        
        return parking_info
    
    def _analyze_street_parking(self, street_parking: List[Dict]) -> Dict:
        """Analyze street parking availability and rules"""
        if not street_parking:
            return {
                'total_spaces': 0,
                'free_hours_available': False,
                'parking_cost_info': 'No street parking data',
                'payment_methods': [],
                'restrictions': [],
                'ownership': 'Unknown',
                'has_street_parking': False,
                'free_parking_periods': [],
                'hours': 'Unknown',
                'parking_cost': 'Unknown'
            }
        
        total_spaces = 0
        for record in street_parking:
            num_spaces = record.get('num_spaces', 0)
            if num_spaces and str(num_spaces).replace('.', '').isdigit():
                total_spaces += int(float(num_spaces))
        
        # Analyze parking costs and free periods
        free_hours = []
        paid_parking = []
        payment_methods = set()
        restrictions = []
        owners = set()
        hours_info = []
        cost_info = []
        
        for record in street_parking:
            # Handle parking cost (could be string, float, or NaN)
            parking_cost = record.get('parking_cost', '')
            if parking_cost and str(parking_cost) not in ['nan', 'None', '']:
                parking_cost_str = str(parking_cost).strip()
                if parking_cost_str:
                    cost_info.append(parking_cost_str)
                    if 'FREE' in parking_cost_str.upper():
                        free_hours.append(parking_cost_str)
                    else:
                        paid_parking.append(parking_cost_str)
            
            # Handle payment method (could be string, float, or NaN)
            payment = record.get('payment_method', '')
            if payment and str(payment) not in ['nan', 'None', '']:
                payment_str = str(payment).strip()
                if payment_str and payment_str != ' ':
                    payment_methods.add(payment_str)
            
            # Handle hours (could be string, float, or NaN)
            hours = record.get('hours', '')
            if hours and str(hours) not in ['nan', 'None', '']:
                hours_str = str(hours).strip()
                if hours_str:
                    hours_info.append(hours_str)
        
        return {
            'total_spaces': total_spaces,
            'free_hours_available': len(free_hours) > 0,
            'free_parking_details': free_hours,
            'paid_parking_details': paid_parking,
            'parking_cost_info': '; '.join(set(free_hours + paid_parking)) if free_hours or paid_parking else 'No cost information',
            'payment_methods': list(payment_methods),
            'restrictions': restrictions,
            'ownership': list(owners),
            'has_metered_parking': any('METER' in method.upper() for method in payment_methods),
            'has_street_parking': len(street_parking) > 0,
            'free_parking_periods': free_hours,
            'hours': '; '.join(hours_info) if hours_info else 'Unknown',
            'parking_cost': '; '.join(cost_info) if cost_info else 'Unknown'
        }
    
    def _get_nearby_parking_lots(self, location: str, parking_lots_data: pd.DataFrame) -> List[Dict]:
        """Get nearby parking lots (same street or close by)"""
        if parking_lots_data.empty or 'Address' not in parking_lots_data.columns:
            return []
        
        nearby_lots = []
        for _, record in parking_lots_data.iterrows():
            address = record['Address'] if pd.notna(record['Address']) else ''
            if isinstance(address, str) and address.strip():
                # Check if location matches or is part of the address
                if (location.upper() in address.upper() or 
                    self._extract_street_from_address(address).upper() == location.upper()):
                    
                    # Helper function to safely get values from pandas Series
                    def safe_get(series, key, default=''):
                        try:
                            value = series[key] if key in series.index and pd.notna(series[key]) else default
                            return str(value) if value != default else default
                        except:
                            return default
                    
                    lot_info = {
                        'Lot Name': safe_get(record, 'Lot Name'),
                        'Address': safe_get(record, 'Address'),
                        'OWNER': safe_get(record, 'OWNER'),
                        'Lot Type': safe_get(record, 'Lot Type'),
                        'Accessibility': safe_get(record, 'Accessibility'),
                        'Accessible': safe_get(record, 'Accessible'),
                        'Capacity': safe_get(record, 'Capacity', 0),
                        '2HR Free Lot': safe_get(record, '2HR Free Lot'),
                        'Surface': safe_get(record, 'Surface')
                    }
                    nearby_lots.append(lot_info)
        
        return nearby_lots
    
    def _analyze_parking_lots(self, parking_lots: List[Dict]) -> Dict:
        """Analyze parking lot options"""
        if not parking_lots:
            return {
                'available_lots': 0,
                'lot_types': [],
                'free_options': [],
                'paid_options': [],
                'accessibility': [],
                'surfaces': [],
                'has_nearby_lots': False,
                'nearby_lot_count': 0
            }
        
        lot_types = []
        free_options = []
        paid_options = []
        accessibility = []
        surfaces = []
        
        for lot in parking_lots:
            lot_type = lot.get('Lot Type', '')
            if lot_type:
                lot_types.append(lot_type)
            
            # Check for free parking
            if lot.get('2HR Free Lot', '') == 'Y':
                free_options.append(f"{lot.get('Lot Name', 'Unknown')} - 2HR Free")
            
            # Check accessibility
            if lot.get('Accessible', '') == 'Y':
                accessibility.append(lot.get('Lot Name', 'Unknown'))
            
            # Surface type
            surface = lot.get('Surface', '')
            if surface:
                surfaces.append(surface)
        
        return {
            'available_lots': len(parking_lots),
            'lot_types': list(set(lot_types)),
            'free_options': free_options,
            'paid_options': paid_options,
            'accessibility': accessibility,
            'surfaces': list(set(surfaces)),
            'lot_details': parking_lots,
            'has_nearby_lots': len(parking_lots) > 0,
            'nearby_lot_count': len(parking_lots)
        }
    
    def _calculate_comprehensive_safety_score(self, 
                                            infraction_analysis: Dict,
                                            street_analysis: Dict,
                                            lot_analysis: Dict) -> Tuple[float, Dict]:
        """Calculate comprehensive safety score with detailed reasoning"""
        
        # Initialize score components
        base_score = 0.5  # Start with neutral score
        score_factors = {
            'infraction_penalty': 0.0,
            'time_restriction_bonus': 0.0,
            'free_parking_bonus': 0.0,
            'paid_parking_penalty': 0.0,
            'availability_bonus': 0.0,
            'enforcement_risk': 0.0
        }
        
        reasoning = []
        
        # 1. Infraction Analysis (40% weight)
        if infraction_analysis['total_count'] > 0:
            infraction_rate = infraction_analysis['total_count'] / 30
            
            if infraction_rate > 50:
                score_factors['infraction_penalty'] = -0.3
                reasoning.append(f"⚠️ High infraction rate: {infraction_rate:.1f}/day")
            elif infraction_rate > 20:
                score_factors['infraction_penalty'] = -0.2
                reasoning.append(f"⚠️ Moderate infraction rate: {infraction_rate:.1f}/day")
            elif infraction_rate > 5:
                score_factors['infraction_penalty'] = -0.1
                reasoning.append(f"⚠️ Low infraction rate: {infraction_rate:.1f}/day")
            else:
                reasoning.append(f"✅ Very low infraction rate: {infraction_rate:.1f}/day")
        else:
            score_factors['infraction_penalty'] = 0.1
            reasoning.append("✅ No parking infractions recorded")
        
        # 2. Street Parking Analysis (30% weight)
        if street_analysis and street_analysis.get('has_street_parking', False):
            # Check for free parking periods
            free_parking_info = street_analysis.get('free_parking_details', [])
            if free_parking_info:
                score_factors['free_parking_bonus'] = 0.15
                reasoning.append(f"✅ Free parking available: {', '.join(free_parking_info)}")
            
            # Check parking cost
            parking_cost = street_analysis.get('parking_cost_info', 'Unknown')
            if parking_cost and parking_cost != 'Unknown' and parking_cost != 'FREE':
                try:
                    cost_value = float(str(parking_cost).replace('$', '').replace('/hr', ''))
                    if cost_value > 0:
                        score_factors['paid_parking_penalty'] = -0.1
                        reasoning.append(f"💰 Paid parking: ${cost_value}/hr")
                except (ValueError, TypeError):
                    pass
            
            # Time restrictions
            hours_info = street_analysis.get('restrictions', 'Unknown')
            if hours_info and hours_info != 'Unknown':
                if 'FREE' in str(hours_info).upper():
                    score_factors['time_restriction_bonus'] = 0.1
                    reasoning.append(f"✅ Free parking hours: {hours_info}")
                elif any(keyword in str(hours_info).upper() for keyword in ['2HR', '1HR', '30MIN']):
                    score_factors['time_restriction_bonus'] = 0.05
                    reasoning.append(f"⏰ Time-limited parking: {hours_info}")
        
        # 3. Parking Lot Analysis (20% weight)
        if lot_analysis and lot_analysis.get('available_lots', 0) > 0:
            lot_count = lot_analysis['available_lots']
            score_factors['availability_bonus'] = min(0.1, lot_count * 0.02)
            reasoning.append(f"🅿️ {lot_count} nearby parking lot(s)")
        
        # 4. Enforcement Risk (10% weight)
        recent_infractions = infraction_analysis.get('recent_count', 0)
        if recent_infractions > 10:
            score_factors['enforcement_risk'] = -0.15
            reasoning.append(f"🚔 High enforcement activity: {recent_infractions} recent infractions")
        elif recent_infractions > 5:
            score_factors['enforcement_risk'] = -0.05
            reasoning.append(f"🚔 Moderate enforcement activity: {recent_infractions} recent infractions")
        
        # Calculate final score
        final_score = base_score + sum(score_factors.values())
        final_score = max(0.0, min(1.0, final_score))  # Clamp between 0 and 1
        
        return final_score, {
            'score_breakdown': score_factors,
            'reasoning': reasoning,
            'raw_score': final_score
        }
    
    def _determine_safety_level(self, safety_score: float) -> str:
        """Determine safety level based on comprehensive score"""
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
    
    def _generate_comprehensive_recommendations(self, 
                                              safety_score: float,
                                              infraction_analysis: Dict,
                                              street_analysis: Dict,
                                              lot_analysis: Dict,
                                              score_details: Dict) -> List[str]:
        """Generate comprehensive parking recommendations"""
        recommendations = []
        
        # Safety level recommendations
        if safety_score >= 0.8:
            recommendations.append("✅ VERY SAFE - Excellent parking choice")
        elif safety_score >= 0.6:
            recommendations.append("✅ SAFE - Good parking option with minor considerations")
        elif safety_score >= 0.4:
            recommendations.append("⚠️ MODERATE - Use caution, check time restrictions")
        else:
            recommendations.append("❌ HIGH RISK - Consider alternative parking")
        
        # Infraction-based recommendations
        total_infractions = infraction_analysis.get('total_count', 0)
        if total_infractions > 50:
            recommendations.append("🚔 High enforcement zone - strictly follow parking rules")
        elif total_infractions > 20:
            recommendations.append("⚠️ Moderate enforcement - be aware of restrictions")
        
        # Time-based recommendations
        if street_analysis and street_analysis.get('has_street_parking', False):
            hours_info = street_analysis.get('restrictions', '')
            parking_cost = street_analysis.get('parking_cost_info', '')
            
            # Check for free parking periods
            if hours_info and 'FREE' in str(hours_info).upper():
                recommendations.append(f"💰 Free parking available during: {hours_info}")
            
            # Check for paid parking
            if parking_cost and parking_cost != 'FREE' and parking_cost != 'Unknown':
                recommendations.append(f"💳 Paid parking required: {parking_cost}")
            
            # Time limit warnings
            if hours_info:
                if '2HR' in str(hours_info).upper():
                    recommendations.append("⏰ 2-hour time limit - set a reminder")
                elif '1HR' in str(hours_info).upper():
                    recommendations.append("⏰ 1-hour time limit - short-term parking only")
                elif '30MIN' in str(hours_info).upper():
                    recommendations.append("⏰ 30-minute limit - very short-term only")
        
        # Alternative parking recommendations
        if lot_analysis and lot_analysis.get('available_lots', 0) > 0:
            recommendations.append(f"🅿️ {lot_analysis['available_lots']} parking lot(s) available as alternatives")
        
        # Peak time warnings
        recent_infractions = infraction_analysis.get('recent_count', 0)
        if recent_infractions > 10:
            recommendations.append("🕐 Avoid peak hours - high enforcement activity")
        
        # Common violation warnings
        common_violations = infraction_analysis.get('infraction_types', [])
        if common_violations:
            top_violation = max(common_violations.items(), key=lambda x: x[1])[0] if common_violations else None
            if top_violation:
                recommendations.append(f"⚠️ Common violation: {top_violation}")
        
        # Seasonal considerations
        recommendations.append("❄️ Winter: Check for snow removal restrictions")
        recommendations.append("🌞 Summer: Popular area - arrive early for best spots")
        
        return recommendations
    
    def _generate_safety_reasoning(self, safety_score: float, infraction_analysis: Dict,
                                 street_analysis: Dict, lot_analysis: Dict) -> str:
        """Generate detailed reasoning for the safety score"""
        
        reasoning_parts = []
        
        # Score explanation
        reasoning_parts.append(f"Safety score: {safety_score:.1%}")
        
        # Infraction analysis
        if infraction_analysis['total_count'] == 0:
            reasoning_parts.append("No recorded infractions at this location")
        else:
            reasoning_parts.append(
                f"{infraction_analysis['total_count']} total infractions "
                f"({infraction_analysis['recent_count']} recent)"
            )
            
            if infraction_analysis['severity_score'] > 1.2:
                reasoning_parts.append("High severity violations recorded")
        
        # Parking availability
        if street_analysis['total_spaces'] > 0:
            reasoning_parts.append(f"{street_analysis['total_spaces']} street parking spaces available")
            
            if street_analysis['free_hours_available']:
                reasoning_parts.append("Free parking periods available")
        else:
            reasoning_parts.append("No official street parking")
        
        # Alternative options
        if lot_analysis['available_lots'] > 0:
            reasoning_parts.append(f"{lot_analysis['available_lots']} nearby parking lot(s)")
        
        return ". ".join(reasoning_parts) + "."
    
    def _get_time_restrictions(self, street_parking: List[Dict]) -> List[str]:
        """Extract time restrictions from parking data"""
        restrictions = []
        for record in street_parking:
            cost_info = record.get('PARKING_COST', '')
            if 'HOUR' in cost_info.upper():
                restrictions.append(cost_info)
        return restrictions
    
    def _analyze_temporal_pattern(self, infractions: List[Dict]) -> str:
        """Analyze when infractions typically occur"""
        if not infractions:
            return "No data"
        
        # This could be expanded to analyze day of week, time of day patterns
        return f"Based on {len(infractions)} infractions"
    
    def _determine_best_parking_times(self, street_analysis: Dict, infraction_analysis: Dict) -> List[str]:
        """Determine the best times to park based on free periods and low infraction times"""
        best_times = []
        
        # Add free parking periods
        if street_analysis['free_hours_available']:
            for free_period in street_analysis['free_parking_details']:
                best_times.append(f"Free period: {free_period}")
        
        # Avoid peak infraction times
        peak_times = infraction_analysis.get('peak_times', [])
        if peak_times:
            safe_times = [f"Avoid {time}" for time in peak_times]
            best_times.extend(safe_times)
        
        return best_times if best_times else ["Check local parking signs for regulations"] 