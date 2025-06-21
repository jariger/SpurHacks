from typing import Dict, List, Any

class FilterService:
    def __init__(self):
        pass
    
    def filter_data(self, data: Dict[str, List[Dict]], filters: Dict[str, Any]) -> Dict[str, List[Dict]]:
        """Filter data based on provided criteria"""
        filtered_data = {}
        
        for data_type, records in data.items():
            filtered_records = records.copy()
            
            # Apply filters based on data type
            if data_type == 'bylaw_infractions':
                filtered_records = self._filter_bylaw_infractions(records, filters)
            elif data_type == 'parking_on_street':
                filtered_records = self._filter_parking_street(records, filters)
            elif data_type == 'parking_lots':
                filtered_records = self._filter_parking_lots(records, filters)
            
            filtered_data[data_type] = filtered_records
        
        return filtered_data
    
    def _filter_bylaw_infractions(self, records: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
        """Filter bylaw infractions data"""
        filtered = records
        
        # Filter by date range
        if 'start_date' in filters and 'end_date' in filters:
            filtered = [
                record for record in filtered
                if filters['start_date'] <= record.get('Date', record.get('DATE', '')) <= filters['end_date']
            ]
        
        # Filter by location
        if 'location' in filters:
            location_filter = filters['location'].lower()
            filtered = [
                record for record in filtered
                if location_filter in str(record.get('Location', record.get('LOCATION', ''))).lower()
            ]
        
        # Filter by infraction type
        if 'infraction_type' in filters:
            infraction_filter = filters['infraction_type'].lower()
            filtered = [
                record for record in filtered
                if infraction_filter in str(record.get('Infraction_Type', record.get('INFRACTION_TYPE', ''))).lower()
            ]
        
        return filtered
    
    def _filter_parking_street(self, records: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
        """Filter parking on street data"""
        filtered = records
        
        # Filter by location/street
        if 'location' in filters:
            location_filter = filters['location'].lower()
            filtered = [
                record for record in filtered
                if (location_filter in str(record.get('STREET', '')).lower() or 
                    location_filter in str(record.get('Location', '')).lower())
            ]
        
        # Filter by parking type/category
        if 'parking_type' in filters:
            parking_filter = filters['parking_type'].lower()
            filtered = [
                record for record in filtered
                if (parking_filter in str(record.get('CATEGORY', '')).lower() or
                    parking_filter in str(record.get('SUBCATEGORY', '')).lower() or
                    parking_filter in str(record.get('PARKING_COST', '')).lower())
            ]
        
        # Filter by ownership
        if 'ownership' in filters:
            ownership_filter = filters['ownership'].lower()
            filtered = [
                record for record in filtered
                if ownership_filter in str(record.get('OWNERSHIP', '')).lower()
            ]
        
        # Filter by payment method
        if 'payment_method' in filters:
            payment_filter = filters['payment_method'].lower()
            filtered = [
                record for record in filtered
                if payment_filter in str(record.get('PAYMENT_METHOD', '')).lower()
            ]
        
        return filtered
    
    def _filter_parking_lots(self, records: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
        """Filter parking lots data"""
        filtered = records
        
        # Filter by location
        if 'location' in filters:
            location_filter = filters['location'].lower()
            filtered = [
                record for record in filtered
                if (location_filter in str(record.get('Location', '')).lower() or
                    location_filter in str(record.get('Name', '')).lower() or
                    location_filter in str(record.get('ADDRESS', '')).lower())
            ]
        
        # Filter by lot type
        if 'lot_type' in filters:
            lot_filter = filters['lot_type'].lower()
            filtered = [
                record for record in filtered
                if (lot_filter in str(record.get('Type', '')).lower() or
                    lot_filter in str(record.get('CATEGORY', '')).lower())
            ]
        
        return filtered 