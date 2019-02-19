#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
predict the price from trained models

@author: jz
"""


import numpy as np
import pandas as pd
import pickle
import text_to_attrs

## predict the price from trained model

def predict_price(x1,x2,x3,x4,x5,x6,x7,x8,x9,x10,x11,x12,checklist_0,desp):
    # fill the checklist
    checklist =['unknown','unknown','unknown','unknown']
    fullcheck = ['ultegra','sram', 'miles', 'fox']
        
    for i1 in range(0,len(checklist_0)):
        for i2 in range(0,len(fullcheck)):
            try: 
                i = checklist_0.index(fullcheck[i2])
                checklist[i2] = fullcheck[i2]
            except:
                pass
        
    inbike_cat = [x1,x2,x3,x4,x5,x6,x7,x8,x9,x10,x11,x12] + checklist
    inbike_desp = desp
    
    # load trained model and run model on input data
    with open('df_encod_dict.pickle', 'rb') as handle:
        df_encod_dict2 = pickle.load(handle)

    #with open('tfidf.pickle', 'rb') as handle:
     #   tfidf2 = pickle.load(handle)

    with open('feature_names.pickle', 'rb') as handle:
        feature_names = pickle.load(handle)


    input_col = ['condition_numcat', 'description_len_numcat','description_cap_numcat',
           'bicycletype_numcat', 'makemanufacturer_numcat',
           'modelnamenumber_numcat', 'wheelsize_numcat', 'framesize_numcat',
           'material_numcat', 'braketype_numcat', 'suspension_numcat',
           'electricassist_numcat', 'handlebartype_numcat', 'ultegra_numcat',
           'sram_numcat', 'miles_numcat', 'fox_numcat']

    # process the year info
    if not text_to_attrs.is_nan(text_to_attrs.str2int(inbike_cat[1])):
        inbike_cat[0] = text_to_attrs.year_condition(inbike_cat[0],text_to_attrs.str2int(inbike_cat[1]))
    inbike_cat.pop(1)

    # pick different trained models, depending on the input data types (1. cat only; 2 cat+text)
    if inbike_desp == None:
        input_col.pop(1)# pop the desp_len
        input_col.pop(1)# pop the desp_cap
        # load the model with nlp data
        predict_model = pickle.load(open('bbb_model_numcat.sav', 'rb'))
        # get the numcat df, two numerical variables extracted from nlp        
        dfin = pd.DataFrame(data=inbike_cat,index=input_col,columns=['inputbike'])
        dfin = dfin.T

        # le encoding and condition transform
        dfin_p = dfin.copy()
        for i in range(0,dfin.shape[1]-1):
            dfin_p[dfin.columns[i+1]] = dfin[dfin.columns[i+1]].map(df_encod_dict2[i])   
    else:
        # process the input description and insert
        inbike_desp = text_to_attrs.str2nopunc(inbike_desp)
        desp_len = text_to_attrs.get_length(inbike_desp) + 6
        desp_cap = text_to_attrs.get_cap(inbike_desp)
        inbike_cat.insert(1,desp_len)
        inbike_cat.insert(2,desp_cap)        
        # tfidf transform of description
        #ttvec = tfidf2.transform([text_to_attrs.str2nopunc(inbike_desp)])
        #dfin_desp_vec = pd.DataFrame(ttvec.T.todense(), index=feature_names,columns=['inputbike'])    
        # load the model with nlp data
        #predict_model = pickle.load(open('bbb_model_numcatnlp.sav', 'rb'))
        # get the numcat df, two numerical variables extracted from nlp
        #dfin = pd.DataFrame(data=inbike_cat,index=input_col,columns=['inputbike'])
        #dfin = dfin.T
        # le encoding and condition transform
        #dfin_p = dfin.copy()
        #for i in range(0,dfin.shape[1]-3):
         #   dfin_p[dfin.columns[i+3]] = dfin[dfin.columns[i+3]].map(df_encod_dict2[i])    
                        
    condition_dict = {'salvage':0.1, 'fair':1, 'good':2,'great':3,'excellent':3.5,'likenew':4,'new':5}
    dfin_p['condition_numcat'] = dfin_p['condition_numcat'].map(condition_dict)

    if inbike_desp == None:
        X_in = dfin_p
    else:
        # combine df from numcat and nlp
        X_in = pd.concat([dfin_p,dfin_desp_vec.T],axis=1)

    # predict model
    price_predict = np.exp(predict_model.predict(X_in))
    
    return price_predict[0]