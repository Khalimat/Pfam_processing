import requests
import urllib.parse
import time
import pandas as pd

def doi_to_pubmed(doi_string):
    """
    Convert DOI(s) to PubMed ID(s) using NCBI E-utilities API.
    
    Args:
        doi_string: String containing one or more DOIs (comma-separated) or "_"
    
    Returns:
        - If input is "_", returns "_"
        - Otherwise returns string with PubMed IDs (separated by ";" if multiple)
          or None if not found, maintaining input DOI order
    """
    # Check for underscore case
    if doi_string.strip() == "_":
        return "_"
    
    # Split the input string into individual DOIs
    dois = [d.strip() for d in doi_string.split(';') if d.strip()]
    
    # Prepare the result list to maintain order
    results = []
    
    # NCBI E-utilities API endpoint
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    
    for doi in dois:
        # URL encode the DOI
        encoded_doi = urllib.parse.quote(doi)
        
        # Parameters for the API request
        params = {
            'db': 'pubmed',
            'term': f'{encoded_doi}[DOI]',
            'retmode': 'json',
            'retmax': 10  # Increased to catch multiple matches
        }
        
        try:
            # Make the API request
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            
            # Parse the JSON response
            data = response.json()
            
            # Extract PubMed IDs if available
            id_list = data.get('esearchresult', {}).get('idlist', [])
            
            if id_list:
                # Join multiple IDs with semicolon
                results.append(";".join(id_list))
            else:
                results.append("None")  # Using string "None" instead of None type
            
            
            time.sleep(0.34)  # NCBI recommends no more than 3 requests per second
            
        except Exception as e:
            print(f"Error processing DOI {doi}: {str(e)}")
            results.append("None")
    
    # Return as semicolon-separated string matching input DOI order
    return ";".join(results)

EVADES_df = pd.read_csv('EVADES.csv')
EVADES_df['PubMed_ID(s)'] =  EVADES_df['DOI'].apply(lambda x: doi_to_pubmed(x))
EVADES_df.to_csv('EVADES.csv')

