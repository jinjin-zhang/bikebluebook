#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
process text info in the listings, add them to the bike attributes

@author: jz
"""
import numpy as np
import pandas as pd

import re
import nltk
import attrs_clean

def str2int(x):
    """
    reformat price
    """
    try:
        y = np.int(x.replace(' ','').replace(',',''))
    except:
        y = np.nan            
    return y

def str2nopunc(x):  
    """
    lower case, get rid of punctuations
    """
    if isinstance(x,str):
        y = re.sub(r'[^\w\s]','',x.lower().strip()).replace('_','')
    else:
        y = x
    return y

def intersection(lst1, lst2): 
    lst3 = [value for value in lst1 if value in lst2] 
    return lst3

def find_maker(bikemaker_set,text_section):
    text_maker = intersection(bikemaker_set, nltk.word_tokenize(text_section))
    if text_maker == []:
        text_maker = [np.nan]
    return text_maker[0]

def find_model(bikemodel_set,text_section):
    text_model = intersection(bikemodel_set, nltk.word_tokenize(text_section))
    if text_model == []:
        text_model = [np.nan]
    return text_model[0]

def find_type(biketype_set,text_section):
    text_model = intersection(biketype_set, nltk.word_tokenize(text_section))
    if text_model == []:
        text_model = [np.nan]
    return text_model[0]

def find_condition(bikecondition_set,text_section):
    text_model = intersection(bikecondition_set, nltk.word_tokenize(text_section))
    if text_model == []:
        text_model = [np.nan]
    return text_model[0]

def find_year(text_section):
    try:
        text_year = str2int(re.match(r'.*([1-3][0-9]{3})',text_section).group(1))
    except:
        text_year = np.nan
    if (text_year > 2019) | (text_year < 1930):
        text_year = np.nan
    if np.isnan(text_year):
        try:
            yrs_ago = str2int(re.match(r'.*([0-9]{1}) years ago',text_section).group(1))
            text_year = 2018 - yrs_ago
        except:
            pass
    if np.isnan(text_year):
        try:
            temp = intersection(['vintage'], nltk.word_tokenize(text_section))
            if temp != []:
                text_year = 1995
        except:
            pass        
    return text_year

##### find key words
def find_material(text_section):
    text_material = intersection(['carbon','aluminum','alloy'],nltk.word_tokenize(str2nopunc(text_section)))
    if text_material == []:
        text_material = [np.nan]
    return text_material[0]

def find_ultegra(text_section):
    text_material = intersection(['ultegra'],nltk.word_tokenize(str2nopunc(text_section)))
    if text_material == []:
        text_material = [np.nan]
    return text_material[0]

def find_sram(text_section):
    text_material = intersection(['sram'],nltk.word_tokenize(str2nopunc(text_section)))
    if text_material == []:
        text_material = [np.nan]
    return text_material[0]


def find_miles(text_section):
    text_material = intersection(['miles'],nltk.word_tokenize(str2nopunc(text_section)))
    if text_material == []:
        text_material = [np.nan]
    return text_material[0]

def find_fox(text_section):
    text_material = intersection(['fox'],nltk.word_tokenize(str2nopunc(text_section)))
    if text_material == []:
        text_material = [np.nan]
    return text_material[0]


def find_framesize(text_section):
    desp = str2nopunc(text_section)
    frame_txt = desp[desp.find('frame')-min(20,desp.find('frame')):desp.find('frame')]
    framesize = attrs_clean.bikeframe_str(frame_txt)
    return framesize


#####
    
def condition_year(cond,year):
    if np.isnan(year):
        if cond == 0.1:
            year = 1990
        elif cond == 1:
            year = 1995
        elif cond == 2:
            year = 2004
        elif cond == 3:
            year = 2009
        elif cond == 4:
            year = 2012
        elif cond == 4.5:
            year = 2015
        elif cond == 5:
            year = 2018
    return year

def year_condition(cond,year):
    if year<1990.0:
        cond2 = 'salvage'
    elif (year>=1995) & (year < 2005):
        cond2 = 'fair'
    elif (year>=2005) & (year < 2012):
        cond2 = 'good'
    else:
        cond2 = cond
    return cond2

def year_condition2(cond,year):
    if is_nan(year) == False:
        if year<1990.0:
            cond = 'salvage'
        elif (year>=1995) & (year < 2005):
            cond = 'fair'
        elif (year>=2005) & (year < 2012):
            cond = 'good'
    return cond

def is_nan(x):
    return (x != x)

def get_length(x):
    return (len(nltk.word_tokenize(x))-6)

def get_cap(x):
    return (sum(1 for c in x if c.isupper())/sum(1 for c in x))


##########################

def fill_attrs(df,bikemaker_set,bikemodel_set):
    
    # get the length and number of capital letters
    df['description_len'] = np.nan
    df['description_len'] = df['description'].apply(get_length)
    
    df['description_cap'] = np.nan
    df['description_cap'] = df['description'].apply(get_cap)

    
    # clean strings in title and description
    df['description'] = df['description'].apply(str2nopunc)
    df['title'] = df['title'].apply(str2nopunc)
    #df['descirption'] = df.apply(lambda x: x.title + x.description, axis=1).copy()

    #bikecondition_set = df.condition.value_counts()[df.condition.value_counts()>1].index.values
    bikecondition_set = ['salvage','fair','good','great','excellent','new']
    
    ###### this may take a while
    # extract bike maker, model, year and condition from title and description
    df = df.dropna(subset = ['description','title'])
    
    df.makemanufacturer = df.apply(lambda x: find_maker(bikemaker_set,x.title) 
             if is_nan(x.makemanufacturer) else x.makemanufacturer, axis=1)
    df.modelnamenumber = df.apply(lambda x: find_model(bikemodel_set,x.title) 
             if is_nan(x.modelnamenumber) else x.modelnamenumber, axis=1)
    
    df.makemanufacturer = df.apply(lambda x: find_maker(bikemaker_set,x.description) 
             if is_nan(x.makemanufacturer) else x.makemanufacturer, axis=1)
    df.modelnamenumber = df.apply(lambda x: find_model(bikemodel_set,x.description) 
             if is_nan(x.modelnamenumber) else x.modelnamenumber, axis=1)
    
    df.framesize = df.apply(lambda x: find_framesize(x.description) 
             if is_nan(x.framesize) else x.framesize, axis=1)
    
    
    df['condition'] = df.apply(lambda x: find_condition(bikecondition_set,x.title) 
                      if is_nan(x.condition) else x.condition, axis=1)
    df['condition'] = df.apply(lambda x: find_condition(bikecondition_set,x.description) 
                      if is_nan(x.condition) else x.condition, axis=1)
    
    df['year'] = np.nan
    df['year'] = df.apply(lambda x: find_year(x.title),axis=1)
    df['year'] = df.apply(lambda x: find_year(x.description) if np.isnan(x.year) else x.year, axis=1)
    
    df['material'] = 'unknown'
    df['material'] = df.apply(lambda x: find_material(x.description),axis=1)


######### some other key words
    df['ultegra'] = 'unknown'
    df['ultegra'] = df.apply(lambda x: find_ultegra(x.description),axis=1)

    df['sram'] = 'unknown'
    df['sram'] = df.apply(lambda x: find_sram(x.description),axis=1)

    df['miles'] = 'unknown'
    df['miles'] = df.apply(lambda x: find_miles(x.description),axis=1)

    df['fox'] = 'unknown'
    df['fox'] = df.apply(lambda x: find_fox(x.description),axis=1)


    # fill in the years according to condition
    #df.year = df.apply(lambda x: condition_year(x.condition, x.year),axis=1)
    
    # fill in the condition according to years
    df.condition = df.apply(lambda x: year_condition2(x.condition,x.year),axis=1)

    return df



