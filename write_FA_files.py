import os
import pandas as pd

EVADES_df = pd.read_csv('EVADES.csv')
EVADES_df_no_Pfam = EVADES_df[EVADES_df['Existing Pfam domain'].isna() & 
                              EVADES_df['Profile HMM (status)'].isna()]

os.makedirs('no_Pfam_yet', exist_ok=True)

for index, row in EVADES_df_no_Pfam.iterrows():
    dir_name = row['Dir_name']
    protein_sequence = row['Protein sequence']
    
    dir_path = os.path.join('no_Pfam_yet', dir_name)
    os.makedirs(dir_path, exist_ok=True)
    
    fa_file_path = os.path.join(dir_path, 'FA')
    with open(fa_file_path, 'w') as f:
        f.write(f">seq\n{protein_sequence}\n")
