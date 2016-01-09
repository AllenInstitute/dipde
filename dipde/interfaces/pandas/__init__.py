import json
import pandas as pd

black_list = ['firing_rate_record', 
              'initial_firing_rate', 
              'metadata', 
              't_record']

json_list = ['p0', 'tau_m']

def to_df(p):
    
    return_dict = {}
    p_dict = p.to_dict()

    for key, val in p_dict['metadata'].items():
        return_dict[key] = val
    
    for key, val in p_dict.items():
        if key not in black_list:
            if key in json_list:
                val = [json.dumps(val)]
            return_dict[key] = [val]

    return pd.DataFrame(return_dict)

def dict_from_df(df):
    D = df.to_dict(orient='list')
    for key, val in D.items():
        if key in json_list:
            D[key] = json.loads(val[0][0])
        else:
            D[key] = val[0]
    return D

def reorder_df_columns(df, column_list):
    varlist = [w for w in df.columns if w not in column_list]
    return df[column_list+varlist]




