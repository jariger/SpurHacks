import pandas as pd
import os
from typing import Dict, List, Any
from datetime import datetime
import json

class ExcelExporter:
    def __init__(self):
        self.output_dir = 'geocoded_output'
        self._ensure_output_dir()
    
    def _ensure_output_dir(self):
        """Create output directory if it doesn't exist"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"📁 Created output directory: {self.output_dir}")
    
    def export_geocoded_data_to_excel(self, data: Dict[str, List[Dict]], geocoded_addresses: Dict[str, Dict[str, float]]) -> str:
        """
        Export geocoded data to Excel files
        
        Args:
            data: Dictionary containing the CSV data with coordinates
            geocoded_addresses: Dictionary mapping addresses to coordinates
        
        Returns:
            Path to the main Excel file created
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print(f"\n📊 Exporting geocoded data to Excel...")
        print("-" * 60)
        
        # Create main Excel file with all data
        main_filename = f"{self.output_dir}/geocoded_data_{timestamp}.xlsx"
        
        with pd.ExcelWriter(main_filename, engine='openpyxl') as writer:
            # Export each data type to a separate sheet
            for data_type, records in data.items():
                if records:
                    df = pd.DataFrame(records)
                    sheet_name = data_type.replace('_', ' ').title()
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    print(f"✅ Exported {len(records):,} records to sheet '{sheet_name}'")
            
            # Create a summary sheet with geocoding statistics
            self._create_summary_sheet(writer, data, geocoded_addresses)
            
            # Create a coordinates lookup sheet
            self._create_coordinates_sheet(writer, geocoded_addresses)
        
        print(f"✅ Main Excel file created: {main_filename}")
        
        # Create individual Excel files for each data type
        individual_files = []
        for data_type, records in data.items():
            if records:
                individual_filename = f"{self.output_dir}/{data_type}_geocoded_{timestamp}.xlsx"
                df = pd.DataFrame(records)
                df.to_excel(individual_filename, index=False)
                individual_files.append(individual_filename)
                print(f"✅ Individual file created: {individual_filename}")
        
        # Create a geocoded addresses lookup file
        lookup_filename = f"{self.output_dir}/geocoded_addresses_lookup_{timestamp}.xlsx"
        self._create_geocoded_lookup_file(lookup_filename, geocoded_addresses)
        
        # Create summary report
        report_filename = f"{self.output_dir}/geocoding_report_{timestamp}.xlsx"
        self._create_geocoding_report(report_filename, data, geocoded_addresses)
        
        print("-" * 60)
        print(f"📊 Export Summary:")
        print(f"   📄 Main file: {main_filename}")
        print(f"   📄 Individual files: {len(individual_files)}")
        print(f"   📄 Lookup file: {lookup_filename}")
        print(f"   📄 Report file: {report_filename}")
        
        return main_filename
    
    def _create_summary_sheet(self, writer, data: Dict[str, List[Dict]], geocoded_addresses: Dict[str, Dict[str, float]]):
        """Create a summary sheet with statistics"""
        summary_data = []
        
        total_records = 0
        total_with_coords = 0
        
        for data_type, records in data.items():
            records_count = len(records)
            with_coords = sum(1 for record in records 
                            if record.get('latitude') != 43.4643 or record.get('longitude') != -80.5204)  # Not default coords
            
            total_records += records_count
            total_with_coords += with_coords
            
            summary_data.append({
                'Data Type': data_type.replace('_', ' ').title(),
                'Total Records': records_count,
                'Records with Geocoded Coordinates': with_coords,
                'Records with Default Coordinates': records_count - with_coords,
                'Geocoding Success Rate (%)': f"{(with_coords/records_count*100):.1f}" if records_count > 0 else "0.0"
            })
        
        # Add overall summary
        summary_data.append({
            'Data Type': 'OVERALL TOTAL',
            'Total Records': total_records,
            'Records with Geocoded Coordinates': total_with_coords,
            'Records with Default Coordinates': total_records - total_with_coords,
            'Geocoding Success Rate (%)': f"{(total_with_coords/total_records*100):.1f}" if total_records > 0 else "0.0"
        })
        
        # Add geocoding statistics
        summary_data.append({})  # Empty row
        summary_data.append({
            'Data Type': 'GEOCODING STATISTICS',
            'Total Records': '',
            'Records with Geocoded Coordinates': '',
            'Records with Default Coordinates': '',
            'Geocoding Success Rate (%)': ''
        })
        summary_data.append({
            'Data Type': 'Unique Addresses Found',
            'Total Records': len(geocoded_addresses),
            'Records with Geocoded Coordinates': '',
            'Records with Default Coordinates': '',
            'Geocoding Success Rate (%)': ''
        })
        
        df_summary = pd.DataFrame(summary_data)
        df_summary.to_excel(writer, sheet_name='Summary', index=False)
        print(f"✅ Created summary sheet with geocoding statistics")
    
    def _create_coordinates_sheet(self, writer, geocoded_addresses: Dict[str, Dict[str, float]]):
        """Create a sheet with all geocoded coordinates"""
        coords_data = []
        
        for address, coords in sorted(geocoded_addresses.items()):
            coords_data.append({
                'Address': address,
                'Latitude': coords['lat'],
                'Longitude': coords['lng'],
                'Google Maps Link': f"https://maps.google.com/?q={coords['lat']},{coords['lng']}"
            })
        
        if coords_data:
            df_coords = pd.DataFrame(coords_data)
            df_coords.to_excel(writer, sheet_name='Geocoded Coordinates', index=False)
            print(f"✅ Created coordinates sheet with {len(coords_data)} geocoded addresses")
    
    def _create_geocoded_lookup_file(self, filename: str, geocoded_addresses: Dict[str, Dict[str, float]]):
        """Create a standalone geocoded addresses lookup file"""
        coords_data = []
        
        for address, coords in sorted(geocoded_addresses.items()):
            coords_data.append({
                'Address': address,
                'Latitude': coords['lat'],
                'Longitude': coords['lng'],
                'Decimal Degrees': f"{coords['lat']:.6f}, {coords['lng']:.6f}",
                'Google Maps Link': f"https://maps.google.com/?q={coords['lat']},{coords['lng']}",
                'Google Maps Search': f"https://www.google.com/maps/search/{address.replace(' ', '+')}"
            })
        
        if coords_data:
            df = pd.DataFrame(coords_data)
            df.to_excel(filename, index=False)
            print(f"✅ Created geocoded lookup file: {filename}")
    
    def _create_geocoding_report(self, filename: str, data: Dict[str, List[Dict]], geocoded_addresses: Dict[str, Dict[str, float]]):
        """Create a detailed geocoding report"""
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Overview sheet
            overview_data = [
                {'Metric': 'Export Date', 'Value': datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
                {'Metric': 'Total Data Files Processed', 'Value': len(data)},
                {'Metric': 'Total Records Processed', 'Value': sum(len(records) for records in data.values())},
                {'Metric': 'Unique Addresses Found', 'Value': len(geocoded_addresses)},
                {'Metric': 'Successfully Geocoded Addresses', 'Value': len(geocoded_addresses)},
            ]
            
            # Add geographic bounds
            if geocoded_addresses:
                lats = [coords['lat'] for coords in geocoded_addresses.values()]
                lngs = [coords['lng'] for coords in geocoded_addresses.values()]
                
                overview_data.extend([
                    {'Metric': '', 'Value': ''},  # Empty row
                    {'Metric': 'GEOGRAPHIC BOUNDS', 'Value': ''},
                    {'Metric': 'Minimum Latitude', 'Value': f"{min(lats):.6f}"},
                    {'Metric': 'Maximum Latitude', 'Value': f"{max(lats):.6f}"},
                    {'Metric': 'Minimum Longitude', 'Value': f"{min(lngs):.6f}"},
                    {'Metric': 'Maximum Longitude', 'Value': f"{max(lngs):.6f}"},
                    {'Metric': 'Center Latitude', 'Value': f"{sum(lats)/len(lats):.6f}"},
                    {'Metric': 'Center Longitude', 'Value': f"{sum(lngs)/len(lngs):.6f}"},
                ])
            
            df_overview = pd.DataFrame(overview_data)
            df_overview.to_excel(writer, sheet_name='Overview', index=False)
            
            # Data type breakdown
            breakdown_data = []
            for data_type, records in data.items():
                if records:
                    with_coords = sum(1 for record in records 
                                    if record.get('latitude') != 43.4643 or record.get('longitude') != -80.5204)
                    
                    breakdown_data.append({
                        'Data Type': data_type.replace('_', ' ').title(),
                        'Total Records': len(records),
                        'With Geocoded Coordinates': with_coords,
                        'With Default Coordinates': len(records) - with_coords,
                        'Success Rate (%)': f"{(with_coords/len(records)*100):.1f}",
                        'Sample Addresses': ', '.join([
                            record.get('STREET', record.get('Address', 'N/A'))
                            for record in records[:3]
                            if record.get('STREET') or record.get('Address')
                        ])
                    })
            
            df_breakdown = pd.DataFrame(breakdown_data)
            df_breakdown.to_excel(writer, sheet_name='Data Breakdown', index=False)
            
            print(f"✅ Created geocoding report: {filename}")
    
    def export_for_google_maps(self, data: Dict[str, List[Dict]], filename: str = None) -> str:
        """
        Export data in a format optimized for Google Maps import
        
        Args:
            data: Dictionary containing the CSV data with coordinates
            filename: Optional custom filename
        
        Returns:
            Path to the Google Maps compatible Excel file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.output_dir}/google_maps_import_{timestamp}.xlsx"
        
        print(f"\n🗺️  Creating Google Maps compatible export...")
        
        # Combine all data into one sheet for Google Maps
        maps_data = []
        
        for data_type, records in data.items():
            for record in records:
                # Skip records with default coordinates
                if (record.get('latitude') == 43.4643 and record.get('longitude') == -80.5204):
                    continue
                
                # Extract relevant information based on data type
                if data_type == 'bylaw_infractions':
                    maps_data.append({
                        'Name': f"Infraction: {record.get('STREET', 'Unknown')}",
                        'Description': f"Reason: {record.get('REASON', 'N/A')} | Fine: ${record.get('VIOFINE', 'N/A')} | Date: {record.get('ISSUEDATE', 'N/A')}",
                        'Latitude': record.get('latitude'),
                        'Longitude': record.get('longitude'),
                        'Type': 'Bylaw Infraction',
                        'Street': record.get('STREET', ''),
                        'Address': record.get('ADDRESS', ''),
                        'Date': record.get('ISSUEDATE', ''),
                        'Reason': record.get('REASON', ''),
                        'Fine': record.get('VIOFINE', ''),
                        'Icon': 'red'
                    })
                
                elif data_type == 'parking_on_street':
                    maps_data.append({
                        'Name': f"Street Parking: {record.get('STREET', 'Unknown')}",
                        'Description': f"Spaces: {record.get('NUM_SPACES', 'N/A')} | Cost: {record.get('PARKING_COST', 'N/A')} | Owner: {record.get('OWNERSHIP', 'N/A')}",
                        'Latitude': record.get('latitude'),
                        'Longitude': record.get('longitude'),
                        'Type': 'Street Parking',
                        'Street': record.get('STREET', ''),
                        'Spaces': record.get('NUM_SPACES', ''),
                        'Cost': record.get('PARKING_COST', ''),
                        'Owner': record.get('OWNERSHIP', ''),
                        'Payment': record.get('PAYMENT_METHOD', ''),
                        'Icon': 'blue'
                    })
                
                elif data_type == 'parking_lots':
                    maps_data.append({
                        'Name': f"Parking Lot: {record.get('Lot Name', 'Unknown')}",
                        'Description': f"Type: {record.get('Lot Type', 'N/A')} | Address: {record.get('Address', 'N/A')} | Owner: {record.get('OWNER', 'N/A')}",
                        'Latitude': record.get('latitude'),
                        'Longitude': record.get('longitude'),
                        'Type': 'Parking Lot',
                        'Lot_Name': record.get('Lot Name', ''),
                        'Address': record.get('Address', ''),
                        'Owner': record.get('OWNER', ''),
                        'Lot_Type': record.get('Lot Type', ''),
                        'Surface': record.get('Surface', ''),
                        'Accessible': record.get('Accessible', ''),
                        'Icon': 'green'
                    })
        
        if maps_data:
            df_maps = pd.DataFrame(maps_data)
            df_maps.to_excel(filename, index=False)
            print(f"✅ Created Google Maps import file: {filename}")
            print(f"   📍 Total mappable points: {len(maps_data)}")
            
            # Show breakdown by type
            type_counts = {}
            for item in maps_data:
                item_type = item['Type']
                type_counts[item_type] = type_counts.get(item_type, 0) + 1
            
            for item_type, count in type_counts.items():
                print(f"   📊 {item_type}: {count} points")
        
        return filename 