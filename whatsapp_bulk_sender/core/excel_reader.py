import pandas as pd
import numpy as np

class ExcelReader:
    @staticmethod
    def read_leads(file_path):
        """
        Reads leads from the given Excel file.
        Returns a list of dictionaries and an error message (if any).
        """
        try:
            df = pd.read_excel(file_path)
            
            leads = []
            for index, row in df.iterrows():
                # Extract phone number, handle floats/strings
                phone_raw = row.get('Phone Number (Digits)')
                
                # Check for NaN/null
                if pd.isna(phone_raw):
                    continue
                    
                phone = str(phone_raw).strip()
                if phone.endswith('.0'):
                    phone = phone[:-2]
                    
                if not phone or phone == 'nan':
                    continue # Skip empty numbers
                    
                # Other fields
                exp = str(row.get('Work Experience', '')).strip()
                exp_year = str(row.get('Experience Year', '')).strip()
                country = str(row.get('Country / Visa Interest', '')).strip()
                link = str(row.get('WhatsApp Link (Auto)', '')).strip()
                
                # Replace 'nan' with empty strings
                if exp.lower() == 'nan' or pd.isna(row.get('Work Experience')): exp = ''
                if exp_year.lower() == 'nan' or pd.isna(row.get('Experience Year')): exp_year = ''
                if country.lower() == 'nan' or pd.isna(row.get('Country / Visa Interest')): country = ''
                if link.lower() == 'nan' or pd.isna(row.get('WhatsApp Link (Auto)')): link = ''
                
                leads.append({
                    'id': index, 
                    'phone': phone,
                    'experience': exp,
                    'experience_year': exp_year,
                    'country': country,
                    'link': link,
                    'status': 'Pending' # Default status: Pending, Sent, Failed
                })
            return leads, None
        except Exception as e:
            return None, str(e)

    @staticmethod
    def export_results(file_path, leads, output_path):
        """
        Takes the original file, appends/updates the Status column based on `leads`,
        and saves to `output_path`.
        """
        try:
            df = pd.read_excel(file_path)
            
            # Update status
            status_map = {lead['id']: lead['status'] for lead in leads}
            
            # Add a 'Status' column if it doesn't exist
            if 'Status' not in df.columns:
                df['Status'] = ''
                
            for idx, status in status_map.items():
                if idx in df.index:
                    df.at[idx, 'Status'] = status
                
            df.to_excel(output_path, index=False)
            return True, None
        except Exception as e:
            return False, str(e)
