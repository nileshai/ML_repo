from flask import Flask, jsonify, request
from flask_cors import CORS
import json
from time import time
#import timeit
import pandas as pd
import aspect_based_sentiment_analysis as absa
import gc
#import keras
#keras.backend.clear_session()
#from numba import cuda
#import torch
#torch.cuda.empty_cache()


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
CORS(app)

gc.collect()
print('starting the absa.load')
nlp = absa.load()
print('absa.load() complete')

#torch.cuda.empty_cache()
#cuda.select_device(0)
#cuda.close()

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
            #print(f'{str(slack.sentiment)} for "{slack.aspect}"')
            #rounded_scores = np.argmax(np.round(slack.scores, decimals=3))
            #rounded_scores = np.round(slack.scores, decimals=3)
            #print(f'Scores (neutral/negative/positive): {rounded_scores}')
        return aspect_sent



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

