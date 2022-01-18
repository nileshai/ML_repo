from flask import Flask, jsonify, request
from flask_cors import CORS
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
#import multiprocessing as mp

from torch.multiprocessing import Pool, Process, set_start_method
try:
    set_start_method('spawn',force=True)
except RuntimeError:
    pass

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

print("GPUs: ", len(tf.config.experimental.list_physical_devices('GPU')))

#os.system('export CUDA_VISIBLE_DEVICES=""')
#os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
#os.environ["CUDA_VISIBLE_DEVICES"]=""
#


#for kafka
config = configparser.ConfigParser()
config_file = os.getenv('CONFIG_FILE', './config.ini')
config.read(config_file)
defaults = config['defaults']
input_topic = defaults['INPUT_TOPIC']
output_topic = defaults['OUTPUT_TOPIC']
broker_list = defaults.get('KAFKA_BROKER_LIST', 'localhost:9092')
# Init Kafka Properties
#input_topic = os.getenv('INPUT_TOPIC', 'sentiment_consumer')
#output_topic= os.getenv('OUTPUT_TOPIC', 'sentiment_producer')
#broker_list= os.getenv('KAFKA_BROKER_LIST','ip-10-0-0-4.us-east-2.compute.internal:9094')

logger = logging.getLogger('uniphore.sentiment')
logger.setLevel(os.getenv('LOG_LEVEL', 'INFO').upper())
logger.addHandler(logging.StreamHandler())
logger.addHandler(logging.FileHandler(os.getenv('LOG_FILE','./sentiment.log')))

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
        tmp=[slack.aspect,str(slack.sentiment)]
        print('1 aspect',tmp)
        return tmp
    if numberofaspects>1:
        for i in inputaspect:
            tmp_list=[i,'price']
            print('aspect more than 1')
            slack, price = nlp(inputtext, aspects=tmp_list)
            rounded_scores = np.round(slack.scores, decimals=3)
            max_score=max(rounded_scores)
            tmp_dict={'word':slack.aspect,'confidence':max_score,'sentiment':str(slack.sentiment)}
            #tmp=[slack.aspect,str(slack.sentiment),max_score]
            aspect_sent.append(tmp_dict)
        return aspect_sent



# Init Kafka Consumers
consumer = KafkaConsumer(bootstrap_servers=broker_list,
                         auto_offset_reset='latest',
                         enable_auto_commit=True,
                         max_in_flight_requests_per_connection=100,
                         value_deserializer=lambda x: json.loads(x.decode('utf-8')))
consumer.subscribe(input_topic)

# Init Kafka Producer
# producer = KafkaProducer(bootstrap_servers=broker_list,
#                         value_serializer=lambda x: json.dumps(x).encode('utf-8'))

pool = concurrent.futures.ProcessPoolExecutor((os.cpu_count() or 1))
loop = asyncio.get_event_loop()


def process_aspect(input_json):
    text_a=input_json['text']
    aspect=input_json['aspect']
    out = get_sentiment(text_a,aspect)
    result = {
          "Input_text:":text_a,
          "output":out
       }
    print('resu',result)
    result = {str(key): str(value) for key, value in result.items()}


    logger.info('Result: ' + json.dumps(result))
    producer = KafkaProducer(bootstrap_servers=broker_list,
                             value_serializer=lambda x: json.dumps(x).encode('utf-8'))
    producer.send(output_topic, result)
    producer.flush()
    producer.close()
    logger.info('(Sent to kafka)')

if __name__ == '__main__':
    #mp.set_start_method('spawn', force=True)
    logger.info('Starting Aspect Based Sentiment service')

    while True:
        for message in consumer:
            try:
                msg = message.value
                logger.info('Request: ' + json.dumps(msg))
                loop.run_in_executor(pool, process_aspect,msg)
                # result = signal_analyse(model_dir, msg)
                # producer.send(output_topic, result)
            except Exception as e:
                logger.exception(f'{e}')


