# from medcat.utils.preprocess_snomed import Snomed

# def get_snomed_to_ICD_map(path_to_snomed_data: str) -> (dict, dict):
#     snomed = Snomed(path_to_snomed_data)
#     snomed_df = snomed.to_concept_df()
#     icd_df = snomed.map_snomed2icd10()
#     sctid2icd10 = {k: g["mapTarget"].tolist() for k,g in icd_df[['referencedComponentId', 'mapTarget']].groupby("referencedComponentId")}
#     sctid2icd10_advice = {k: (g["mapTarget"].tolist(),g["mapAdvice"].tolist()) for k,g in icd_df[['referencedComponentId', 'mapTarget', 'mapAdvice']].groupby("referencedComponentId")}

#     return (sctid2icd10, sctid2icd10_advice)

# sctd2icd10, sct2icd10_with_advice = get_snomed_to_ICD_map('path_to_snomed_db')

import medcat
from medcat.utils.preprocess_snomed import Snomed
import pandas as pd
import numpy as np

#%%
def get_snomed_to_ICD_map(path_to_snomed_data: str) -> (dict, dict):
    snomed = Snomed(path_to_snomed_data)
    snomed_df = snomed.to_concept_df()
    icd_df = snomed.map_snomed2icd10()
    sctid2icd10 = {k: g["mapTarget"].tolist() for k,g in icd_df[['referencedComponentId', 'mapTarget']].groupby("referencedComponentId")}
    sctid2icd10_advice = {k: (g["mapTarget"].tolist(),g["mapAdvice"].tolist()) for k,g in icd_df[['referencedComponentId', 'mapTarget', 'mapAdvice']].groupby("referencedComponentId")}

    return (sctid2icd10, sctid2icd10_advice)

sctd2icd10, sct2icd10_with_advice = get_snomed_to_ICD_map('SNOMED2ICD')

#%%
def snomed_2_icd(lst):   
    if not pd.isna(lst):
        # print(lst)
        if '[' in lst:
            lst = lst.replace('[','').replace(']','').replace('\'','').split(', ')
        #print(type(lst))
        print(lst)
        if type(lst) == list:
            lst_icd = [sctd2icd10[x][0] for x in lst if x in sctd2icd10.keys() ]
            lst_notinicd = [x for x in lst if x not in sctd2icd10.keys() ]
            if len(lst_icd) > 0:
                print(lst_icd)
            else:
                lst_icd = np.nan
            if len(lst_notinicd) > 0:
                print(lst_notinicd)
            else:
                lst_notinicd = np.nan
            return pd.Series([lst_icd, lst_notinicd]) 
        else:
            print('not list')
            return pd.Series([np.nan, np.nan])
    else:
        print('Null')
        return  pd.Series([np.nan, np.nan])

print("Sample of snomed_2_icd: ", snomed_2_icd(['90708001']))

#print("Sample of snomed_2_icd: ", snomed_2_icd(['1003367004']))

#%%
def snomed_2_icd_short(x):
    if x in sctd2icd10.keys():
        return sctd2icd10[x][0]
    else:
        return

print("Sample of snomed_2_icd_short: ", snomed_2_icd_short('90708001'))

#print("Sample of snomed_2_icd_short: ", snomed_2_icd_short('1003367004'))

#%% Sample test in df
# boundary_data[['prev_SNOMED2ICD', 'prev_SNOMED_notin_ICD']] = boundary_data['previous_snomed'].apply(lambda x:snomed_2_icd(x))
# boundary_data[~boundary_data['prev_SNOMED2ICD'].isna()]
# boundary_data[~boundary_data['prev_SNOMED_notin_ICD'].isna()]
# data_add_diag_code[['ICD10', 'SNOMED_notin_ICD']] = data_add_diag_code['snomed'].apply(lambda x:snomed_2_icd(x)) 

# %%
