#script for python 2.7 (works with 2.7.12 or newer)
import sys, hmac, hashlib, base64
import urllib,ssl
import urllib2
from time import gmtime, strftime
import argparse


def main():
    env_options = ['dev','prod','qa','stable','stable_gmm','stable_qa','stable_qa_gmm','prod_gmm']
    env_options_desc = ['dev (dev/qa gmm)','prod (production dnn)','qa dnn environment','stable (dsg dnn)','stable_gmm (dsg dnn)','stable_qa (qa dnn)','stable_qa_gmm (qa gmm)','prod_gmm (production gmm)']
    acoustic_model_default='en-us.telephonyenhanced'
    parser = argparse.ArgumentParser(description='This script allows you to get reco results for a single audio file from a combined model deployed in webreco.  This is used for sanity testing your model deployment before doing a batch eval, and for debugging your deployment in the event of an error.  You can test in one of {} environments - {} .  You need to provide the URL to the audio file you want to test and the URL to the wrapper grammar you are using for the test. You can additionally provide the acoustic model, {} will be the default option'.format(len(env_options_desc),env_options_desc,acoustic_model_default))
    parser.add_argument('-a','--audio', help='URL to audio file you wish to use for the test.', required=True)
    parser.add_argument('-g','--grxml', help='URL to wrapper grxml or SLM that you using for the test.', required=True)
    parser.add_argument('-e','--env', help='Environment you wish to test. '+ ' | '.join(env_options_desc), required=True,choices=env_options)
    parser.add_argument('-m','--acoustic_model', help='the acoustic model to use. default value is {}'.format(acoustic_model_default), required=False,default=acoustic_model_default)

    args = vars(parser.parse_args())

    grammar = str(args['grxml'])
    audio = str(args['audio'])
    env = str(args['env'])
    acoustic_model=str(args['acoustic_model'])
    print 'acoustic model used is '+acoustic_model

    ## WebReco Url and credentials

    if env == 'dev':   # dev/qa
        print("Using: " + env)
        clientId = 'tm-dev'
        sharedKey = 'asHTRE#$#Fasef!'
        url = 'https://webreco01.r51.sv2.247-inc.net/reco'

    elif env == 'prod':  #production dnn
        print("Using: production dnn " + env)
        clientId = 'tellme-dev-dnn'
        sharedKey = 'B\\EpA7yVp_QYIsVWBeGn'
        url = 'https://webreco.api.247-inc.net/reco'

    elif env=='qa': #qa dnn environment
        print("Using qa dnn environment")
        clientId='247inc-dnntest'
        sharedKey="ON+7OnAi\'9s5wAltI71w"
        url='http://qa-webreco.api.247-inc.net/reco'

    elif env == 'stable':  #stable dnn environment
        print("Using: stable dnn (dsg)")
        clientId = '247inc-dsg-dnn'
        sharedKey = 'mN8PaFSHqIf$dt?{PAPR'
        # sharedKey = 'h-Cw^Qd9Ko*JwVPIp{9O}'
        url = 'https://stable-webreco.voice.lb-priv.sv2.247-inc.net/reco'
    elif env =='stable_gmm':
        print('using stable gmm environment')
        clientId = '247inc-dsg'
        sharedKey = 'eNCCpQf0JQsC}*B0QMbW'
        # sharedKey = 'x&BnHx\/0iaggK^$dj0d'
        url = 'https://stable-webreco.voice.lb-priv.sv2.247-inc.net/reco'
    elif env =='stable_qa':
        print('using stable qa dnn environment')
        clientId = '247inc-tm-qa'
        sharedKey = 'f-GaCW1/r#1444V3hV?P'
        url = 'https://stable-webreco.voice.lb-priv.sv2.247-inc.net/reco'
    elif env =='stable_qa_gmm':
        print('using stable qa gmm environment')
        clientId = 'tm-dev'
        sharedKey = 'asHTRE#$#Fasef!'
        url = 'https://stable-webreco.voice.lb-priv.sv2.247-inc.net/reco'
    elif env =='prod_gmm': #production gmm
        print("Using production gmm ")
        ##the only difference between gmm production & dnn production is the client id & shared key. The urls are the same
        clientId = 'tm-dev'
        sharedKey = 'asHTRE#$#Fasef!'
        url = 'https://webreco.api.247-inc.net/reco'
    else:
        print("Environment options are: prod|stable|dev|prod_gmm")

    ## Preparing Authorization String
    tm = strftime("%a, %d %b %Y %X GMT", gmtime())
    data = tm+'\n/'+clientId+'/WebReco'
    digest = hmac.new( sharedKey, data, digestmod=hashlib.sha256).digest()
    auth = base64.b64encode(digest).decode()
    auth_param='SharedKeyLite:'+tm+':'+clientId+':'+auth

    ## HTTP request params
    params = { 'grammar1' : grammar,
           'audio': audio,
           #'engineproperty':'tellme.acousticmodel=en-us.search',
           'engineproperty':'tellme.acousticmodel='+acoustic_model,
           'maxnbest' : '10',
           #'sensitivity': '0.5',
           #'completetimeout':'250ms',
           'confidencelevel':'0.0',
           #'speedvsaccuracy':'0.5',
           #'incompletetimeout':'1000ms',
           'requesttimeout':'60s',
           'authorization' : auth_param}

    encodedParams = urllib.urlencode(params)
    # proxy = urllib2.ProxyHandler({'http': 'http://cache.backside.sv2.tellme.com:3128'})
    proxy = urllib2.ProxyHandler({'http': 'http://proxy-grp1.lb-priv.svc.247-inc.net:3128'})
    opener = urllib2.build_opener(proxy)
    urllib2.install_opener(opener)

    request = urllib2.Request(url, encodedParams)
    response = urllib2.urlopen(request,context=ssl._create_unverified_context())
    out = response.read()

    print out

#-------------------------------
if __name__ == "__main__":
     main()
