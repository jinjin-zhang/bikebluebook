#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
data cleaning of the bike attributes

@author: jz
"""
import numpy as np
from numpy.random import randn
import pandas as pd
from scipy import stats

import math
import re
import nltk
import datetime

################################## functions for bike attrs cleaning
def str2int(x):
    """
    reformat price
    """
    try:
        y = np.int(x.replace(' ','').replace(',',''))
    except:
        y = np.nan            
    return y

def bikeattrs_str(x):   
    """
    reformat fixed bike attrs
    """
    if isinstance(x,str):
        if (x.strip() == 'nan') or (x.strip == ''):
            y = np.nan
        else:
            y = x.strip()
    else:
        y = x
    return y

def bikemaker_str(x): 
    """
    reformat bike manufactuer, get rid of all non-alphabet chars and punctuations
    """
    if isinstance(x,str):
        x = x.lower()
        regex = re.compile('[^a-zA-Z]')
        y = regex.sub('',x)
    else:
        y = x
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

def framesize(x):
    if type(x) == str:
        if (x=='xs'):
            y = 'XS'
        elif (x=='small'):
            y = 'S'
        elif (x=='medium'):
            y = 'M'
        elif (x=='large'):
            y = 'L'
        elif (x=='xl'):
            y = 'XL'
        else:
            y = np.nan
    else:
        if ((x>=9) & (x<=14)) | ((x>=47) & (x<=49)):
            y = 'XS'
        elif ((x>=15) & (x<=16)) | ((x>=50) & (x<=52)):
            y = 'S'
        elif ((x>=17) & (x<=18)) | ((x>=53) & (x<=54)):
            y = 'M'
        elif ((x>=19) & (x<=20)) | ((x>=55) & (x<=57)):
            y = 'L'
        elif ((x>=21) & (x<=22)) | ((x>=58) & (x<=71)):
            y = 'XL'
        else:
            y = np.nan
    return y

def bikeframe_str(x):
    if type(x) == str:
        y1 = re.sub(r'[^\w\s]',' ',x.lower().strip()).replace('_',' ')
        y2 = re.sub('[a-zA-z]', ' ', y1)
        y3 = nltk.word_tokenize(y2)
        try:
            y4 = [(float(s)) for s in y3 if ((float(s)>=9)&(float(s)<=22)) 
                     or ((float(s)>=47)&(float(s)<=71))]
        except:
            y = np.nan
            y4=[]
    else:
        y4 = [x]
    if y4 != []:    
        y = framesize(y4[0])
    else:
        if ((y1.find('kid') != -1) | (y1.find('child') != -1)|(y1.find('girl') != -1) | (y1.find('boy') != -1)) == True:
            y = 'kids'
        else: 
            y5 = nltk.word_tokenize(y1)
            y6 = intersection(y5,['small','medium','large','xl']) 
            if y6 != []:
                y = framesize(y6[0])
            else:
                y = np.nan
    return y

def get_days(x):
    y = (datetime.date(2019,1,29) - datetime.datetime.strptime(x.split()[0], "%Y-%m-%d").date()).days
    return y

##############################

def bike_attrs_clean(df,price_log):

    # clean the price data
    df['price'] = df['price'].apply(str2int)
    df = df.dropna(subset = ['price']).copy()
    df['price'] = df['price'].apply(lambda x: 1 if x == 0 else x)
    if price_log == True:
        df.price = np.log(df.price)
    
    # acquire time stamp data
    df['timeposted'] = df['timeposted'].apply(get_days)
    
    # special clean for maker, model and framesize attrs    
    df['makemanufacturer'] = df['makemanufacturer'].apply(bikemaker_str)
    df['modelnamenumber'] = df['modelnamenumber'].apply(str2nopunc)
    df['framesize'] = df['framesize'].apply(bikeframe_str)
    
    # clean all bike attrs
    df['makemanufacturer'] = df['makemanufacturer'].apply(bikeattrs_str)
    df['modelnamenumber'] = df['modelnamenumber'].apply(bikeattrs_str)
    #df['framesize'] = df['framesize'].apply(bikeattrs_str)    
    df['bicycletype'] = df['bicycletype'].apply(bikeattrs_str)
    df['braketype'] = df['braketype'].apply(bikeattrs_str)
    df['handlebartype'] = df['handlebartype'].apply(bikeattrs_str)
    df['suspension'] = df['suspension'].apply(bikeattrs_str)
    df['electricassist'] = df['electricassist'].apply(bikeattrs_str)
    df['condition'] = df['condition'].apply(bikeattrs_str)
        
    return df






