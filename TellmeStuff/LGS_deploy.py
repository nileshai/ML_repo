'''
Created on Feb 19, 2014

@author: anmol.walia

Updated by: Zac Branson
'''

import sys, hmac, hashlib, base64
import imp 
import urllib 
import urllib2
import argparse
from time import gmtime, strftime
imp.reload(urllib2)

def getAuthorizationParam():
    
    clientId = 'tm-dev'
    sharedKey = 'asHTRE#$#Fasef!' 
    #url = 'https://largegrammar-cloud.in.tellme.com/addgrammar'
    
    service='WebLGS'
    
    tm = strftime("%a, %d %b %Y %X GMT", gmtime())
    data = tm+'\n/'+clientId+'/'+service
    digest = hmac.new( sharedKey, data, digestmod=hashlib.sha256).digest()
    auth = base64.b64encode(digest).decode()
    authorization_string='SharedKeyLite:'+tm+':'+clientId+':'+auth

    return authorization_string


def requeststatus(): 
    url='https://largegrammar-cloud.in.tellme.com/getrequeststatus' 
    auth_param = getAuthorizationParam() 
    print "auth_param = " + auth_param
    params = {'authorization': auth_param } 
              
    encodedParams = urllib.urlencode(params) 
    
    #    proxy = urllib2.ProxyHandler({'http': 'http://localhost:3128'})
    proxy = urllib2.ProxyHandler({'http': 'http://cache.backside.sv2.tellme.com:3128'}) # for DNN
    
    opener = urllib2.build_opener(proxy)
    urllib2.install_opener(opener)
    
    req = urllib2.Request(url, encodedParams) 
    
    response = urllib2.urlopen(req) 
    reco = response.read() 
    print reco 

#-------------------------------------------------------

def deleteGrammar(grammar_alias):
    #    url = 'https://largegrammar.in.tellme.com/deletegrammar'  # for production telpod
    url = 'https://largegrammar-cloud.in.tellme.com/deletegrammar'   #for production webreco
    
    auth_param = getAuthorizationParam()
    params = {'grammarset':'gs1.tm-dev',
              'notificationuri':'mailto:zac.branson@247-inc.com',
              'grammaralias':grammar_alias,
              'authorization': auth_param }
              

    encodedParams = urllib.urlencode(params)
    req = urllib2.Request(url, encodedParams)
    
    response = urllib2.urlopen(req)
    reco = response.read()
    print reco

#-------------------------------
## Pre-load a grammar using LGS
def addGrammar(url, grammar_url, acoustic_model, grammar_alias, email):
    

#     tm-dev : previous quota
    auth_param = getAuthorizationParam()    
    params = {'grammarset':'gs1.tm-dev',
              'notificationuri':'mailto:' + email,
              'grammaraliases':grammar_alias,
              'grammar':grammar_url,
              'engineproperty':'tellme.acousticmodel='+acoustic_model,
              'authorization': auth_param }
#             'engineproperty':'tellme.acousticmodel='+acoustic_model,

    encodedParams = urllib.urlencode(params)
    req = urllib2.Request(url, encodedParams)
    
    response = urllib2.urlopen(req)
    reco = response.read()
    print reco

#------------------------------- 

def main():
    parser = argparse.ArgumentParser(description='This script is used to deploy combined models to LGS-Large Grammar Service.  It currently supports deployment to Stable and Production.  You need to provide the URL to the model you want to deploy, it should be somewhere in your public html in fafr.  You need to provide a name for the model as you want it to appear in LGS.  You also need to provide the email address that you want notifications sent to, usually your [24]7 address.')
    parser.add_argument('-m','--model', help='URL to model you which to deploy.  Model should be in your public html.', required=True)
    parser.add_argument('-n','--name', help='Name you want the model to have in LGS.', required=True)
    parser.add_argument('-e','--env', help='Environment you wich to deploy to. stable|prod', required=True)
    parser.add_argument('-@','--email', help='Email address you want the notification mailed to.', required=True)
    args = vars(parser.parse_args())

    model_url = args['model']
    name = args['name']
    email = args['email']

    env = args['env']
    if env == 'prod':
        url = 'https://largegrammar.in.tellme.com/addgrammar'   # for production telpod
        addGrammar(url=url,grammar_url=model_url,acoustic_model='en-us.telephonyenhanced',grammar_alias=name,email=email)

        url = 'https://largegrammar-cloud.in.tellme.com/addgrammar'  #for production webreco
        addGrammar(url=url,grammar_url=model_url,acoustic_model='en-us.telephonyenhanced',grammar_alias=name,email=email)
    elif env == 'stable':    
        url = 'http://stable-lgs.voice.lb-priv.sv2.247-inc.net/addgrammar'  #for stable telpod and webreco    
        addGrammar(url=url,grammar_url=model_url,acoustic_model='en-us.telephonyenhanced',grammar_alias=name,email=email)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
    

