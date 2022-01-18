from flask import Flask
from time import time
import timeit
import pandas as pd
import aspect_based_sentiment_analysis as absa
import gc
from transformers import BertTokenizer
import keras
keras.backend.clear_session()
from numba import cuda
import torch
torch.cuda.empty_cache()

app = Flask(__name__)


@app.route('/post', methods=['POST'])
def post_route():
    if request.method == 'POST':

        data = request.get_json()

        print('Data Received: "{data}"'.format(data=data))
        return "Request Processed.\n"



#def hello():
#	return "welcome to the flask tutorials"

print('starting the absa.load')
nlp = absa.load()
print('absa.load() complete')
gc.collect()

torch.cuda.empty_cache()
cuda.select_device(0)
cuda.close()

def get_sentiment(inputtext,inputaspect):
    numberofaspects=len(inputaspect)
    if numberofaspects==0:
        return("Alert! Aspect not provided")
    if numberofaspects==1:
        inputaspect.append('price')
        slack, price = nlp(inputtext, aspects=inputaspect)
        print(f'{str(slack.sentiment)} for "{slack.aspect}"')
        #rounded_scores = np.argmax(np.round(slack.scores, decimals=3))
        rounded_scores = np.round(slack.scores, decimals=3)
        print(f'Scores (neutral/negative/positive): {rounded_scores}')
    if numberofaspects>1:
        for i in inputaspect:
            tmp_list=[i,'price']
            slack, price = nlp(inputtext, aspects=tmp_list)
            print(f'{str(slack.sentiment)} for "{slack.aspect}"')
            #rounded_scores = np.argmax(np.round(slack.scores, decimals=3))
            rounded_scores = np.round(slack.scores, decimals=3)
            print(f'Scores (neutral/negative/positive): {rounded_scores}')


if __name__ == "__main__":
	app.run(host ='0.0.0.0', port = 5001, debug = True)
