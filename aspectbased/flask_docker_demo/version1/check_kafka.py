from kafka import KafkaConsumer
from kafka import KafkaProducer
import json

# Single File
f = open('/home/nilesh/asbsa/flask_docker_demo/message.json')
data = json.load(f)
print(data)
print('Done Reading json')
consumer = KafkaConsumer('sentiment_producer',bootstrap_servers='ip-10-0-0-4.us-east-2.compute.internal:9094')
print('Consumer')
producer = KafkaProducer(bootstrap_servers='ip-10-0-0-4.us-east-2.compute.internal:9094',value_serializer=lambda v: json.dumps(v).encode('utf-8'))
print('producer')
producer.send('sentiment_consumer', data)
print('Sending the Data')
print('Started Reading Msg From Consumer')
for msg in consumer:
    print(msg.value)
    consumer.close()
print('Completed Reading Msg From Consumer')
