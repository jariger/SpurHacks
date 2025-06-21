from typing import Dict, List, Any

class MapsConverter:
    def __init__(self):
        pass
    
    def convert_to_google_maps_format(self, data: Dict[str, List[Dict]], safety_data: Dict[str, Dict] = None) -> List[Dict]:
        """
        Convert filtered data to Google Maps API format with safety information
        
        Args:
            data: Dictionary containing the CSV data
            safety_data: Safety analysis data for each location
        """
        markers = []
        
        for data_type, records in data.items():
            for record in records:
                # Use geocoded coordinates if available, otherwise use default
                lat = record.get('latitude', 43.4643)  # Waterloo default
                lng = record.get('longitude', -80.5204)  # Waterloo default
                
                # Get location/title based on data type
                location = self._get_location_from_record(record, data_type)
                
                marker = {
                    'type': data_type,
                    'position': {
                        'lat': lat,
                        'lng': lng
                    },
                    'title': location,
                    'data': record
                }
                
                # Add safety information if available
                if safety_data and location in safety_data:
                    safety_info = safety_data[location]
                    marker.update(self._get_safety_styling(safety_info))
                else:
                    # Add default styling based on data type
                    marker.update(self._get_marker_styling(data_type, record))
                
                markers.append(marker)
        
        return markers
    
    def _get_location_from_record(self, record: Dict, data_type: str) -> str:
        """Extract location/title from record based on data type"""
        if data_type == 'parking_on_street':
            # For parking on street, use STREET field
            street = record.get('STREET', '')
            category = record.get('CATEGORY', '')
            return f"{street}" if street else f"{category} Parking"
            
        elif data_type == 'bylaw_infractions':
            # For bylaw infractions, look for Location field
            return record.get('Location', record.get('Street', 'Unknown Location'))
            
        elif data_type == 'parking_lots':
            # For parking lots, look for Name or Location
            return record.get('Name', record.get('Location', 'Parking Lot'))
            
        else:
            # Fallback
            return record.get('Location', record.get('STREET', record.get('Name', 'Unknown Location')))
    
    def _get_safety_styling(self, safety_info: Dict) -> Dict[str, Any]:
        """Get marker styling based on safety information"""
        return {
            'icon': self._get_safety_icon(safety_info['safety_level']),
            'color': safety_info['color'],
            'description': safety_info['recommendation'],
            'safety_score': safety_info['safety_score'],
            'safety_level': safety_info['safety_level'],
            'infraction_count': safety_info['infraction_count'],
            'recent_infractions': safety_info['recent_infractions']
        }
    
    def _get_safety_icon(self, safety_level: str) -> str:
        """Get icon based on safety level"""
        icon_mapping = {
            'very_safe': '🟢',
            'safe': '🟡',
            'moderate': '🟠',
            'risky': '🔴',
            'dangerous': '⚫'
        }
        return icon_mapping.get(safety_level, '⚪')
    
    def _get_marker_styling(self, data_type: str, record: Dict) -> Dict[str, Any]:
        """Get marker styling based on data type (fallback)"""
        if data_type == 'bylaw_infractions':
            return {
                'icon': '🔴',
                'color': '#FF0000',
                'description': f"Infraction: {record.get('Infraction_Type', record.get('INFRACTION_TYPE', 'Unknown'))}"
            }
        elif data_type == 'parking_on_street':
            parking_cost = record.get('PARKING_COST', 'Unknown')
            num_spaces = record.get('NUM_SPACES', 'Unknown')
            return {
                'icon': '🔵',
                'color': '#0000FF',
                'description': f"Street Parking: {num_spaces} spaces, {parking_cost}"
            }
        elif data_type == 'parking_lots':
            return {
                'icon': '🟢',
                'color': '#00FF00',
                'description': f"Parking Lot: {record.get('Type', record.get('CATEGORY', 'Unknown'))}"
            }
        else:
            return {
                'icon': '⚪',
                'color': '#808080',
                'description': 'Unknown type'
            } 