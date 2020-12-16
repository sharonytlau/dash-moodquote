import pandas as pd
pd.set_option('display.max_columns', None)
import os
from tqdm import tqdm
import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer

import re

cwd = os.getcwd()

## Import dataset of quotes 
df_quotes = pd.read_csv("../data/all_quotes.csv")

## Data cleaning
df_quotes.dropna(subset=['Quote'], inplace=True)
df_quotes.drop_duplicates(subset=['Quote'],keep='first', inplace=True)

## Get sentimental score and polarity of each quote
def get_polarity(dict_sentimental_score):
    if dict_sentimental_score['compound'] >= 0.05:
        polarity = 'positive'
    elif dict_sentimental_score['compound'] <= -0.05:
        polarity = 'negative'
    else:
        polarity = 'neutral'
    return polarity

tqdm.pandas()

vader = SentimentIntensityAnalyzer()
df_quotes['sentimental_score'] = df_quotes['Quote'].progress_apply(vader.polarity_scores)
df_quotes['polarity'] = df_quotes['sentimental_score'].progress_apply(get_polarity)

## Cound words of each quote
def get_sentence_length(quote):
    length = len(re.findall(r'\w+', quote))
    return length

df_quotes['length'] = df_quotes['Quote'].progress_apply(get_sentence_length)

## Export df_quotes to csv
df_quotes.to_csv('../data/all_quotes_w_sentimentalScore.csv', index=False)

#from textblob import TextBlob
#data['polarity'] = data['Quote'].apply(TextBlob)
#text = "So many books, so little time."
#text = "So many books, so little time."
#blob = TextBlob(text)
#blob.tags           # [('The', 'DT'), ('titular', 'JJ'),
#                    #  ('threat', 'NN'), ('of', 'IN'), ...]
#
#blob.noun_phrases   # WordList(['titular threat', 'blob',
#                    #            'ultimate movie monster',
#                    #            'amoeba-like mass', ...])
#for sentence in blob.sentences:
#    print(sentence.sentiment.polarity) 



## %% Detect objects in text
#
#nlp = spacy.load("en_core_web_sm")
#OBJECTS = {"dobj", "dative", "attr", "oprd"}
#doc = nlp("Have enough courage to trust love one more time and always one more time.")
#objects = [tok for tok in doc if (tok.dep_ in OBJECTS)]
#

# %%
#import boto3
#boto3.client("rekognition").detect_labels(Image={"Bytes": encoded_image_string})
#
#tags = list(data['Tags'])
#tags = [str_tags.split(', ') for str_tags in tags if str_tags]
#
#
#
#all = []
#for i in range(len(tags)):
#    all += tags[i]
#all    
#len(all)
#
#unique_tag = pd.DataFrame(sorted(list(set(all))))
#unique_tag.columns = ['tag']
#len(unique_tag)
#unique_tag.head()
#
#unique_tag['emotion'] = unique_tag['tag'].apply(te.get_emotion)
#unique_tag.to_csv('unique_tag.csv')
#
#text = "I'm selfish, impatient and a little insecure. I make mistakes, I am out of control and at times hard to handle. But if you can't handle me at my worst, then you sure as hell don't deserve me at my best."
#te.get_emotion(text)

