#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NLP processing of the title and description of the craigslist listings

@author: jz
"""
# the normal imports
from sklearn import feature_extraction
import numpy as np
import pandas as pd
import re
import gensim
import nltk
from nltk.corpus import wordnet as wn
from nltk.stem.wordnet import WordNetLemmatizer
nltk.download('wordnet')
nltk.download('stopwords')

import spacy
spacy.load('en')
from spacy.lang.en import English
parser = English()

## text cleaning for NLP
def str2nopunc(x):  
    """
    lower case, get rid of punctuations
    """
    if isinstance(x,str):
        y = re.sub(r'[^\w\s]','',x.lower().strip()).replace('_','')
    else:
        y = x
    return y

def tokenize(text):
    lda_tokens = []
    tokens = parser(text)
    for token in tokens:
        if token.orth_.isspace():
            continue
        elif token.like_url:
            lda_tokens.append('URL')
        elif token.orth_.startswith('@'):
            lda_tokens.append('SCREEN_NAME')
        else:
            lda_tokens.append(token.lower_)
    return lda_tokens

def strip_head(text):
    try:
        if text.startswith(' QR Code Link to This Post'):
            text = text[27:]
    except:
        pass
    return text

def str_clean(data):
    # Remove Emails
    data = re.sub('\S*@\S*\s?', '', data)
    # Remove new line characters
    data = re.sub('\s+', ' ',  data)
    # Remove distracting single quotes
    data = re.sub("\'", "", data)
    # Remove distracting single quotes
    data = re.sub("\*", "", data)
    data = data.replace('/',' ')
    return data

def text_clean(text):
    y = tokenize(str2nopunc((text)))
    #y= bigram_trigram(y1,min_count,threshold)
    return y

# extend stopwords    
stopwords = nltk.corpus.stopwords.words('english')
newStopWords = ['bike','bikes','please','bicycle','could', 'might', 
                'must', 'need', 'would','post','link','code','qr',]
stopwords.extend(newStopWords)
en_stop = set(stopwords)

def get_lemma(word):
    lemma = wn.morphy(word)
    if lemma is None:
        return word
    else:
        return lemma

def get_lemma2(word):
    return WordNetLemmatizer().lemmatize(word)

def prepare_text_for_lda(text):
    tokens = text_clean(text)
    tokens = [token for token in tokens if len(token) > 2]
    tokens = [token for token in tokens if token not in en_stop]
    tokens = [get_lemma(token) for token in tokens]
    return tokens

def make_trigrams(data_words):
    
    bigram = gensim.models.Phrases(data_words, min_count=5, threshold=50)
    trigram = gensim.models.Phrases(bigram[data_words], threshold=50)  
    
    bigram_mod = gensim.models.phrases.Phraser(bigram)
    trigram_mod = gensim.models.phrases.Phraser(trigram)
    
    def make_bigrams(texts):
        return [bigram_mod[doc] for doc in texts]
    
    return [trigram_mod[bigram_mod[doc]] for doc in data_words]

def bigram_trigram(data_words,min_count,threshold):
       
    text_gram_list = make_trigrams(data_words)
    
    return text_gram_list

### calculate the tfidf matrix
def calc_tfidf(text_list, max_features=None,ngram_range=(1,1)):
    # this can take some time
    if max_features is None:
        tfidf = feature_extraction.text.TfidfVectorizer(
            tokenizer=text_clean, stop_words=en_stop,ngram_range=ngram_range)
    else:
        tfidf = feature_extraction.text.TfidfVectorizer(
            tokenizer=text_clean, stop_words=en_stop,
            max_features=max_features,ngram_range=ngram_range)
    tfs_vectors = tfidf.fit_transform(text_list)
    return tfs_vectors, tfidf



