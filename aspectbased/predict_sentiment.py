import re
from typing import Dict, List, Union
import numpy as np
# from sklearn.externals import joblib
import joblib
import pickle
from logos.logos.ingest.transcript import Transcript
import json
from time import time
#import timeit
import pandas as pd
import aspect_based_sentiment_analysis as absa
import gc
#for kafka service
import asyncio
import concurrent
import configparser
import os
import logging
from kafka import KafkaConsumer, KafkaProducer
import tensorflow as tf
import numpy as np

'''
from torch.multiprocessing import Pool, Process, set_start_method
try:
    set_start_method('spawn',force=True)
except RuntimeError:
    pass

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

print("GPUs: ", len(tf.config.experimental.list_physical_devices('GPU')))
'''

#CLASS_MAPPING = {0: 'NEGATIVE', 1: 'POSITIVE', 2: 'NEUTRAL'}  ## TODO: REMOVE!!! Should be in the model.
#LABEL_VALUES = {'POSITIVE': 1, 'NEGATIVE': -1, 'NEUTRAL': 0}

gc.collect()
print('starting the absa.load')
nlp = absa.load()
print('absa.load() complete')



def get_sentiment(inputtext,inputaspect):
    aspect_sent=[]
    numberofaspects=len(inputaspect)
    print('get_sentiment:',inputtext,inputaspect,numberofaspects)
    if numberofaspects==0:
        return("Alert! Aspect not provided")
    if numberofaspects==1:
        inputaspect.append('price')
        slack, price = nlp(inputtext, aspects=inputaspect)
        rounded_scores = np.round(slack.scores, decimals=2)
        max_score=str(max(rounded_scores))
        tmp_dict={'word':slack.aspect,'confidence':max_score,'sentiment':str(slack.sentiment)}
        return tmp_dict
    if numberofaspects>1:
        for i in inputaspect:
            tmp_list=[i,'price']
            print('aspect more than 1')
            slack, price = nlp(inputtext, aspects=tmp_list)
            rounded_scores = np.round(slack.scores, decimals=2)
            max_score=str(max(rounded_scores))
            tmp_dict={'word':slack.aspect,'confidence':max_score,'sentiment':str(slack.sentiment)}
            aspect_sent.append(tmp_dict)
        return aspect_sent

def correct_aspect(text,aspects):
    tmp=[]
    for i in aspects:
        if i in text:
            tmp.append(i)
    return tmp

def predict(transcript: Transcript, aspects) -> Dict:
    """"""
    print('Entered predict')
    texts_raw = [turn.text() for turn in transcript]
    texts = [re.sub(r'(^|\s)\.(\s|$)', ' ', t).strip() for t in texts_raw]
    tmp_list=[]
    for text in texts:
        print(text)
        aspects1=correct_aspect(text,aspects)
        print(aspects1)
        turn_asba = get_sentiment(text, aspects1)
        print(turn_asba)
        tmp_list.append(turn_asba)
    print(tmp_list)
    turns = []
    for i, t in enumerate(transcript):
        turn = {
            'order': t.order,
            'speaker': t.speaker,
            'startOffset': t.start_offset,
            'endOffset': t.end_offset,
            'aspectResult': tmp_list[i]
        }
        turns.append(turn)

    # overall = predict_overall_sentiment(transcript)

    res = {
        'sessionId': transcript.session_id,
        'startTime': transcript.start_time,
        'lang': transcript.lang,
        'status': "success",
        'aspects': aspects,
        'turns': turns,
    }
    return res


# def predict_sentiment(texts: List[str]) -> List[Dict]:
#     feat = featurizer(texts)
#     x = vectorizer.transform(feat)
#     y_pred = model.predict_proba(x)
#     pred = np.argmax(y_pred, axis=1)
#     confidence = [y_pred[i][j] for i, j in enumerate(pred)]
#     return [{'value': CLASS_MAPPING[int(pred)], 'confidence': conf} for pred, conf in zip(pred, confidence)]
#
#
# def predict_overall_sentiment(transcript: Transcript) -> Dict:
#     """"""
#     overall = {
#         'sentiment': {
#             'customerSentiment': call_sentiment_customer(transcript),
#             'agentSentiment': "NEUTRAL"
#         }
#     }
#     return overall


''' ===== Unit test ===== '''


def test_predict():
    """
    """
    pass
