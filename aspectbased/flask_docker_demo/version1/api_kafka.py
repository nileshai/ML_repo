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



"""
#for Rest API
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
CORS(app)

gc.collect()
print('starting the absa.load')
nlp = absa.load()
print('absa.load() complete')
"""

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



def get_sentiment(inputtext,inputaspect):
    aspect_sent=[]
    numberofaspects=len(inputaspect)
    if numberofaspects==0:
        return("Alert! Aspect not provided")
    if numberofaspects==1:
        inputaspect.append('price')
        slack, price = nlp(inputtext, aspects=inputaspect)
        tmp=[slack.aspect,str(slack.sentiment)]
        return tmp
    if numberofaspects>1:
        for i in inputaspect:
            tmp_list=[i,'price']
            slack, price = nlp(inputtext, aspects=tmp_list)
            tmp=[slack.aspect,str(slack.sentiment)]
            aspect_sent.append(tmp)
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
    #result = signal_analyse(m_dir, input_json)
    text_a=input_json['text']
    aspect=input_json['aspect']
    out = get_sentiment(text_a,aspect)
    result = {
          "Input_text:":text_a,
          "output":out
       }
    result = {str(key): str(value) for key, value in result.items()}


    logger.info('Result: ' + json.dumps(result))
    producer = KafkaProducer(bootstrap_servers=broker_list,
                             value_serializer=lambda x: json.dumps(x).encode('utf-8'))
    producer.send(output_topic, result)
    producer.flush()
    producer.close()
    logger.info('(Sent to kafka)')

if __name__ == '__main__':
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


"""
#For Rest api
@app.route('/incomes')
def get_incomes():
  return jsonify(incomes)


@app.route('/incomes', methods=['POST'])
def add_income():
  input_text=request.get_json()
  text_a=input_text['text']
  aspect=input_text['aspect']
  try:
       out = get_sentiment(text_a,aspect)
       result = {
          "Input_text:":text_a,
          "output":out
       }
       result = {str(key): str(value) for key, value in result.items()}
       return jsonify(result=result)
  except Exception as e:
       print(e)
       return json.dumps({"result":"Model Failed"})


if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5001)

"""
