#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Recommendation model using the processed bike feature vectors and feature importances

@author: jz
"""

import numpy as np
import pandas as pd
from sklearn import metrics
import pickle

from bs4 import BeautifulSoup
import urllib3
import requests
import certifi
from collections import defaultdict


def get_new_posting_attrs(posting_URLs):        
    bike_attrs = defaultdict(list)    
    col_name = ['title','price','URL','imageURL','imagefile','description', 'timeposted',
                'latitude','longitude','bicycletype','braketype','condition',
                'framesize','handlebartype','makemanufacturer','modelnamenumber',
                'serialnumber','wheelsize','suspension','electricassist']    
    for var in col_name:        
        bike_attrs[var] = []    
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',ca_certs=certifi.where())
    # get the html text data and imageURL         
    try:
        response = http.request('GET',posting_URLs)
        soup = BeautifulSoup(response.data, "lxml")
        #print('requested*************',soup)
        images = soup('img')
        imageURL = images[0]['src']
    except:
        print('request error')                
    # Get bike attributes
    bike_attrs['title'].append(soup.find('span',{'id':'titletextonly'}).text.strip().replace(',',' '))            
    try:
        bike_attrs['price'].append(soup.find('span',{'class':'price'}).text.strip()[1:])
    except:
        bike_attrs['price'].append('')
    bike_attrs['description'].append(soup.find('section',{'id':'postingbody'}).text.strip().replace('\n',' ').replace(',',' '))
    bike_attrs['imageURL'].append(imageURL)
    bike_attrs['imagefile'].append(str(np.nan))
    bike_attrs['URL'].append(posting_URLs)
    bike_attrs['timeposted'].append(soup.find('p',{'class':'postinginfo reveal'}).text.strip()[-18:])
    bike_attrs['latitude'].append(str(np.nan))
    bike_attrs['longitude'].append(str(np.nan))
    ## fill in 'nan' for all bike detailed attrs first
    sub_attrs = ['bicycletype','braketype','condition',\
            'framesize','handlebartype','makemanufacturer','modelnamenumber','serialnumber',\
            'wheelsize','suspension','electricassist']
    attrs_text = soup.find('p',{'class':'attrgroup'}).find_all('span')
    try:
        for ii in range(0,len(attrs_text)):
            attrs_name = attrs_text[ii].text.split(':')[0].strip().replace(' ','').replace('/','').replace(',','')
            attrs_content = attrs_text[ii].text.split(':')[1].strip().replace(' ','').replace('/','').replace(',','')
            bike_attrs[attrs_name].append(attrs_content)
            sub_attrs.pop(sub_attrs.index(attrs_name))

        for i_attr in sub_attrs:
            bike_attrs[i_attr].append(str(np.nan))
    except:
        print(attrs_text)                
    attrs_list = []    
    for var in col_name:
        attrs_list.append(bike_attrs[var])    
    df_in = pd.DataFrame(attrs_list, index = col_name).T         
    return df_in


def url2input(url):    
    # scraping
    df_in = get_new_posting_attrs(url)  
    max_price = np.int(df_in.price.iloc[0])
    print('url2input finished')
    return df_in,max_price


import text_to_attrs
import attrs_clean


def bike_data_process(df):    
    df.drop(columns=['serialnumber'],inplace=True)    
    # parameters for feature engineering --------------------------------
    price_log = True    
    # inital cleanning of bike attrs
    df_c1 = attrs_clean.bike_attrs_clean(df,price_log=price_log)

    with open('maker_model_set.pickle', 'rb') as handle:
        maker_model_set = pickle.load(handle)    
    # combine title into description for processing
    df_c1.description = df_c1.apply(lambda x: x.title + x.description, axis=1).copy()  
    # extract attrs from text and fill into the categories
    df_c3 = text_to_attrs.fill_attrs(df_c1,maker_model_set[0],maker_model_set[1])
          
    df_c3.fillna(value='unknown',inplace=True)
    df_c4 = df_c3.copy()
    # transform condition into numerical data
    condition_dict = {'salvage':0.1, 'fair':1, 'good':2,'great':3,'excellent':3.5,'likenew':4,'new':5}
    df_c4.condition = df_c4.condition.map(condition_dict)
    # features, through the URL and etc.
    df_num = df_c4[['condition']].copy()    
    df_cat = df_c4[['bicycletype', 'makemanufacturer','modelnamenumber', 
                        'wheelsize', 'framesize','material',
                'braketype','suspension', 'electricassist','handlebartype',
                       'ultegra', 'sram', 'miles', 'fox']].copy()
    # do the same one-hot econding
    with open('proc_df.pickle', 'rb') as handle:
        proc_df = pickle.load(handle) 
    proc_df.drop(columns=['condition','price'],inplace=True)
    df_e_short = pd.get_dummies(df_cat,drop_first=False)
    df_e_long = pd.DataFrame(proc_df.iloc[0]).T
    df_e_long.reset_index(inplace=True,drop=True)
    df_e_long.iloc[0] = 0    
    for x in df_e_short.columns.values:
        if x in proc_df.columns.values:
            df_e_long[x] = df_e_short[x]            
    vec_in_proc = pd.concat([df_num,df_e_long],axis=1)    
    
    return vec_in_proc,pd.concat([df_num,df_cat],axis=1)


def recommend_bike(url,droplist,city):
    
    #url =  'https://newyork.craigslist.org/brk/bik/d/brooklyn-almost-new-vintage-miyata-one/6815672413.html'
    #  url =    "https://newyork.craigslist.org/lgi/bik/d/commack-6-speed-trek-mt-60-mountain/6810413669.html"
    #  url =    "https://newyork.craigslist.org/brk/bik/d/brooklyn-54cm-unknown-combat-track-bike/6798218217.html"
    # https://newyork.craigslist.org/jsy/bik/d/fort-lee-canyon-road-race-bike/6815664410.html     
    #url ='https://newyork.craigslist.org/mnh/bik/d/new-york-city-2008-specialized-allez/6815591084.html'          
    ### droplist index: vintage fuji 477 ; cannondale 12044 ; trek kids 1472; 11732 track bike    
#    droplist = '29427: title'
#    url = None

    city = 'US' 
    
    # load the saved processed bike data and feature importance
    with open('bike_df.pickle', 'rb') as handle:
        bike_df = pickle.load(handle)
    with open('proc_df.pickle', 'rb') as handle:
        proc_df = pickle.load(handle)
    with open('fi_wt.pickle', 'rb') as handle:
        fi_wt = pickle.load(handle)
    
    X_wt = proc_df[proc_df.columns[:-1]].copy()
    y = proc_df[proc_df.columns[-1]]
    
    # THIS WAS DONE BEFORE SAVING THE DATA
    #fi_wt[:] = fi_wt.values + fi_wt.mean(axis=1)[0]*1e-15
    #X_wt[:] = np.divide(X_wt.values,np.sqrt(fi_wt.values))    
    #X_wt[:] = X_wt.divide(np.sqrt(fi_wt.loc[0]),axis=1)  
    
    if (url == None) or (url == ''):
        # input vector - input vector * weight (element-wise)
        i = np.int(droplist.split(':')[0])
        vec_in = list(X_wt.loc[i])
        maxprice = y.loc[i]
        # do price filtering on input matrix
        X_wt_price = X_wt[y < maxprice].copy()    
        X_in = np.array([vec_in]*1)  
        df_cat = pd.DataFrame(list(bike_df.loc[i]),index=bike_df.columns).T
        df_cat.price = np.exp(float(df_cat.price)).copy()
    
    else:
        # transform url of listing into format of input vector
        vec_in, maxprice = url2input(url)
        X_wt_price = X_wt[y < np.log(maxprice)].copy()
        vec_in_proc,df_cat = bike_data_process(vec_in)
        X_in = np.array([list(vec_in_proc.loc[0])]*1) 
        # add weighted to X_in
        #fi_wt_mat = fi_wt.append([fi_wt]*1)
        #fi_wt_mat.set_index(keys = X_wt.index,inplace=True)
        #X_in[:] = np.multiply(X_in,np.sqrt(fi_wt.values))
        # add the newly scraped imageURL and other raw parameters to df_cat for displaying purpose
        df_cat['imageURL'] = vec_in['imageURL'].iloc[0]
        df_cat['URL'] = vec_in['URL'].iloc[0]
        df_cat['title'] = vec_in['title'].iloc[0]
        df_cat['price'] = vec_in['price'].iloc[0]
        
        
    # calculate the weighted cosine similarity
    wcs_mat = metrics.pairwise.cosine_similarity(X_in, X_wt_price)
    wcs = wcs_mat[0]
    
    similarity = pd.Series(wcs, index = X_wt_price.index).apply(lambda x: 0 if np.round(x,decimals=6) == 1.0 else x).sort_values(ascending=False)
    sim_idx = similarity.index
    
    # remove the duplicated listings
    bike_df.drop_duplicates(subset=['title'],keep='first',inplace=True)
    
    # filter the selected geography index
    if city != 'US':
        # index of bikes at the selected city
        city_idx = bike_df[bike_df.city == city].index
        f_idx = similarity[list(set(sim_idx) & set(city_idx) & set(bike_df.index))].sort_values(ascending=False).index
    else:
        f_idx = similarity[list(set(sim_idx) & set(bike_df.index))].sort_values(ascending=False).index
    
    # check if the selected listing still exist or not
    
    
    # recommended listings
    df_recom = bike_df.loc[f_idx[0:5]]
    df_recom.price = np.exp(df_recom.price)
        
    return df_recom,df_cat