from typing import Union, Dict, Tuple, List

import json
from flask import Response, request

from logos.api import app, http_get_transcript, bad_request
#from logos.logos.api import app, http_get_transcript, bad_request
import predict_sentiment

#for kafka service
import asyncio
import concurrent
import configparser
import os
import logging
from kafka import KafkaConsumer, KafkaProducer
#import multiprocessing as mp

from torch.multiprocessing import Pool, Process, set_start_method
try:
    set_start_method('spawn',force=True)
except RuntimeError:
    pass

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

#print("GPUs: ", len(tf.config.experimental.list_physical_devices('GPU')))

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
    req_data=input_json
    aspect=input_json['aspect']
    print('input received',aspect)
    valid, transcript = http_get_transcript({'transcript': req_data})
    if not valid:
        #app.logger.error("Invalid request format.")
        print('bad request')
    try:
        pred = req_data#predict_sentiment.predict(transcript, aspects)
        print('')
        js_data = json.dumps(pred, indent=4, sort_keys=True)
        #resp = Response(js_data, status=200, mimetype='application/json')
    except Exception as e:
        #app.logger.error(f"{e}")
        print('bad request')

    logger.info('Result: ' + js_data)
    producer = KafkaProducer(bootstrap_servers=broker_list,
                             value_serializer=lambda x: json.dumps(x).encode('utf-8'))
    producer.send(output_topic, js_data)
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
                #logger.exception(f'{e}')
                print('Error')


