import requests 
import os
        
def traduce_booleans(bool_):
    
    if bool_:
        return 'SI'
    return 'NO'




def merge_by_field(subfields_df):
    
    fields = set([subfield_name.split('-')[0] for subfield_name in subfields_df['Parcela']])
    
    fields_merged = {k: v for k, v in zip(fields, [{} for i in range(len(fields))])}
    
    for subfield, surface, crop in subfields_df[['Parcela', 'Superficie', 'Cultivo']].values:
        
        field = subfield.split('-')[0]
        
        fields_merged[field].update({crop:surface})
        
    return fields_merged



def check_fastapi_status():
    FASTAPI_URL = os.getenv("FASTAPI_URL", "http://127.0.0.1:8001/health")
    try:
        response = requests.get(FASTAPI_URL)
        return response.status_code == 200
    except:
        return False