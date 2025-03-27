import requests
import time
import math
import pandas as pd

def get_pfam_metadata(pfam_ids):
    """
    Retrieve Pfam metadata for comma-separated IDs, handling NaN inputs gracefully.
    
    Args:
        pfam_ids (str/float): Comma-separated Pfam IDs or NaN
        
    Returns:
        dict/float: Dictionary of metadata if valid input, NaN if input is NaN
        Example outputs:
            NaN → NaN
            "PF00001" → {"PF00001": {"name": "7tm_1", "description": "7 transmembrane..."}}
            "PF00001,PF00002" → {PF00001: {...}, PF00002: {...}}
    """
    # Handle NaN/NA/None inputs
    if pd.isna(pfam_ids) or pfam_ids in ['NaN', 'NA', 'None', '']:
        return float('nan')
    
    # Handle numeric input that might come from pandas
    if isinstance(pfam_ids, (int, float)) and math.isnan(pfam_ids):
        return float('nan')
    
    # Process valid string inputs
    pfam_list = [pid.strip() for pid in str(pfam_ids).split(",") if pid.strip()]
    
    result = {}
    base_url = "https://www.ebi.ac.uk/interpro/api/entry/pfam/"
    
    for pfam_id in pfam_list:
        try:
            url = f"{base_url}{pfam_id}"
            response = requests.get(url, headers={"Accept": "application/json"})
            response.raise_for_status()
            data = response.json()
            
            metadata = data.get("metadata", {})
            result[pfam_id] = {
                "name": metadata.get("name", "Not found"),
                "description": metadata.get("description", "Not found")
            }
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {pfam_id}: {str(e)[:100]}...")
            result[pfam_id] = {"name": "Error", "description": "Error fetching data"}
        
        time.sleep(0.1)
    
    return result if result else float('nan')

EVADES_df = pd.read_csv('EVADES.csv')
EVADES_df['Pfam_description'] = EVADES_df['Existing Pfam domain'].apply(lambda x: get_pfam_metadata(x))
EVADES_df.to_csv('EVADES_pfam_desc.csv')
