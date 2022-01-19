'''
Created on Feb 19, 2014

@author: anmol.walia
Documentation for using LGS-
https://247inc.atlassian.net/wiki/display/SPSCI/8.+Deploying+Combined+Model+to+LGS+and+Testing+it
'''

import sys, hmac, hashlib, base64, os
import imp
import urllib
import urllib2
from time import gmtime, strftime, sleep
imp.reload(urllib2)

def getAuthorizationParam(environment,grammar_set=None):
    print 'grammar set used = {}'.format(grammar_set)

    clientId,sharedKey = get_client_id_shared_key(environment=environment,grammar_set=grammar_set)
    service='WebLGS'

    tm = strftime("%a, %d %b %Y %X GMT", gmtime())
    data = tm+'\n/'+clientId+'/'+service
    digest = hmac.new( sharedKey, data, digestmod=hashlib.sha256).digest()
    auth = base64.b64encode(digest).decode()
    authorization_string='SharedKeyLite:'+tm+':'+clientId+':'+auth

    return authorization_string

def get_client_id_shared_key(environment,grammar_set=None):
    """
    This function returns the clientId & sharedKey to be used for a specific grammar_set
    """
    clientId = 'tm-dev'
    sharedKey = 'asHTRE#$#Fasef!'

    valid_grammar_sets=['gs1.247inc-speech','gs1.tm-dev', 'pre-res-vx-usa-en-us.amex',None] # None because some requests does not need a grammar_set (eg:requeststatus call)
    if (grammar_set not in valid_grammar_sets):
        raise Exception('specify a valid grammar_set. valid ones are:- ' + ','.join(valid_grammar_sets) )

    if(grammar_set=='gs1.tm-dev'):
        clientId = 'tm-dev'
        sharedKey = 'asHTRE#$#Fasef!'
    elif(grammar_set=='gs1.247inc-speech'):
        clientId = '247inc-speech'
        sharedKey = '87wcbiou}s`M7CL/dkVy'
        if environment=='stable':
            sharedKey='zgs8n~AP&xa8sJYJ}HJZ'
    elif(grammar_set=='pre-res-vx-usa-en-us.amex'):
        clientId = '247inc-speech'
        sharedKey = '87wcbiou}s`M7CL/dkVy'
        if environment=='stable':
            sharedKey='zgs8n~AP&xa8sJYJ}HJZ'        

    return clientId,sharedKey


def update_proxy_info(proxy_url):
    """
    This function updates the urllib to use a proxy server for
    connection if the variable proxy_url is not empty
    """
    if proxy_url!="":
        print 'proxy specified using the same '+ proxy_url
        proxy = urllib2.ProxyHandler({'http': proxy_url})
        opener = urllib2.build_opener(proxy)
        urllib2.install_opener(opener)
    else:
        print 'proxy not specified'


def get_url(environment='stable'):
    """
    This function returns the base url based on the environment
    :environment: can take the values 'stable' or 'prod' or 'dev'
    :returns: environment specific url

    """
    if(environment not in ['stable','prod_webreco','prod']):
        raise Exception('specify a valid environment. Specify either stable,prod_webreco or prod')

    url = 'http://stable-lgs.voice.lb-priv.sv2.247-inc.net/'  #for stable webreco
    if environment=='prod_webreco':
        # url = 'https://largegrammar-cloud.in.tellme.com/'  #for production webreco old one removed
        url = 'https://largegrammar-cloud.api.247-inc.net/'  #for production webreco
    elif environment=='prod':
        # url = 'https://largegrammar.in.tellme.com/'   # for production old url removed
        url = 'https://largegrammar.api.247-inc.net/'   # for production

    return url

def requeststatus(environment,lgs_request_id=None):
    """
    :environment: can take the values 'stable' or 'prod' or 'dev'
    :lgs_request_id: not mandatory, this take lgs request id & returns the same
    """
    url = get_url(environment)+'getrequeststatus'
    update_proxy_info(proxy_url)
    auth_param = getAuthorizationParam(environment=environment)
    params = {'authorization': auth_param
	}

    if lgs_request_id != None:
 	params['lgsrequestid'] = lgs_request_id
    encodedParams = urllib.urlencode(params)


    # get request (post request not allowed for this api)
    url+="?"+encodedParams
    req = urllib2.Request(url)

    response = urllib2.urlopen(req)
    reco = response.read()
    print reco


#-------------------------------------------------------

def deleteGrammar(grammar_alias,environment,email_ids,grammar_set='gs1.247inc-speech'):
    """
    This function is used to delete a grammar in LGS given the lgs id
    :environment: can take the values 'stable' or 'prod' or 'dev'
    """
    url = get_url(environment)+'deletegrammar'
    update_proxy_info(proxy_url)

    auth_param = getAuthorizationParam(environment=environment,grammar_set=grammar_set)
    params = {'grammarset':grammar_set,
              'notificationuri':'mailto:'+email_ids,
              'grammaralias':grammar_alias,
              'authorization': auth_param }


    encodedParams = urllib.urlencode(params)
    req = urllib2.Request(url, encodedParams)

    response = urllib2.urlopen(req)
    reco = response.read()
    print reco

#-------------------------------
## Pre-load a grammar using LGS
def addGrammar(grammar_url, acoustic_model, grammar_aliases,environment,email_ids,grammar_set='gs1.247inc-speech'):
    """
    This function is used to deploy a grammar to LGS.

    :grammar_url:URL to model that needs to be deployed.  Model should be in your public html.
    :acoustic_model
    :grammar_aliases:you can specify multiple aliases separated by space
    :environment: can take the values 'stable' or 'prod' or 'dev'
    :email_ids:email id to send notication to

    """
    url = get_url(environment)+'addgrammar'
    update_proxy_info(proxy_url)
    auth_param = getAuthorizationParam(environment=environment,grammar_set=grammar_set)
    params = {'grammarset':grammar_set,
              'notificationuri':'mailto:'+email_ids,
              'grammaraliases':grammar_aliases,
              'grammar':grammar_url,
              'engineproperty':'tellme.acousticmodel='+acoustic_model,
              'authorization': auth_param }

#               'engineproperty':'tellme.acousticmodel='+acoustic_model,

    encodedParams = urllib.urlencode(params)
    print encodedParams
    req = urllib2.Request(url, encodedParams)

    response = urllib2.urlopen(req)
    reco = response.read()
    print reco

def assign_grammar_alias(existing_grammar_alias, new_grammar_aliases,environment,email_ids,grammar_set='gs1.247inc-speech'):
    """
    This function is for assigning one more alias to an existing grammar.
    If there is another grammar pointing to this new_grammar_alias that will be overwritten and new_grammar_alias will be pointing to this new grammar
    """

    url = get_url(environment)+'assignalias'
    update_proxy_info(proxy_url)
    auth_param = getAuthorizationParam(environment=environment,grammar_set=grammar_set)
    params = {'grammarset':grammar_set,
              'notificationuri':'mailto:'+email_ids,
              'srcgrammaralias':existing_grammar_alias,
              'dstgrammaraliases':new_grammar_aliases,
              'authorization': auth_param }


    encodedParams = urllib.urlencode(params)
    req = urllib2.Request(url, encodedParams)

    response = urllib2.urlopen(req)
    reco = response.read()
    print reco

def remove_grammar_alias(alias_to_delete,environment,email_ids,grammar_set='gs1.247inc-speech'):
    """
    This function is for deleting an alias associated with a grammar.

    Warning: If the existing grammar has only one alias and you remove it, that grammar will be removed.

    Tip: Use the getgrammarlist request to see how many aliases the chosen
    grammar has before you use the removealias request. If you want to
    delete the grammar, use the deletegrammar request, not the removealias request
    """

    url = get_url(environment)+'removealias'
    update_proxy_info(proxy_url)
    auth_param = getAuthorizationParam(environment=environment,grammar_set=grammar_set)
    params = {'grammarset':grammar_set,
              'notificationuri':'mailto:'+email_ids,
              'grammaralias':alias_to_delete,
              'authorization': auth_param }


    encodedParams = urllib.urlencode(params)
    req = urllib2.Request(url, encodedParams)

    response = urllib2.urlopen(req)
    reco = response.read()
    print reco


def get_grammar_list(environment,grammar_alias=None,grammar_set='gs1.247inc-speech'):
    """
    this function is used to get a list of grammars for a grammar set (and a grammar_alias)
    """

    url = get_url(environment)+'getgrammarlist'
    update_proxy_info(proxy_url)
    auth_param = getAuthorizationParam(environment=environment,grammar_set=grammar_set)
    params = {'grammarset':grammar_set,
              'authorization': auth_param }

    if grammar_alias !=None:
        params['grammaralias']=grammar_alias
    encodedParams = urllib.urlencode(params)

    #get request (post request not allowed for this api)
    url+="?"+encodedParams
    req = urllib2.Request(url)

    response = urllib2.urlopen(req)
    reco = response.read()
    print reco

def batchAddGrammar(grammar_file,acoustic_model,environment,email_ids,grammar_set, prefix):

    with open(grammar_file,'r') as infile:
        for line in infile.readlines():
            grammar_alias = line.rstrip()
            addGrammar(grammar_url=prefix+grammar_alias, acoustic_model=acoustic_model, grammar_aliases=grammar_alias,environment=environment,email_ids=email_ids,grammar_set=grammar_set)
            sleep(2)



if __name__ == "__main__":
    proxy_url=''
    # proxy_url = 'http://localhost:3128' # to connect to stable envrionment this proxy had to be used when running this script from laptop
    proxy_url ='http://cache.backside.sv2.tellme.com:3128'
    email_ids='cayley.last@247-inc.com' # this can be a semi colon separated list of email ids
    #For stable environment, the same LGS is used for webreco & telpod. prod is the production LGS environment. prod_webreco is the production webreco environment
    environment='stable' #environment can take value = 'stable'or'prod'or'prod_webreco'.
    grammar_set='pre-res-vx-usa-en-us.amex' # grammar_set can take values = 'gs1.247inc-speech' or 'gs1.tm-dev'
    ### Add grammar examples
    #addGrammar('http://anvil.tellme.com/~jgeorge/amex/us/merchant/slm_test_failure/Fold_1.cfg','en-us.telephonyenhanced','amex_merchant2',environment=environment,email_ids=email_ids) # basic example for adding grammar
    # addGrammar('http://anvil.tellme.com/~jgeorge/amex/us/merchant/slm_test_failure/Fold_1.cfg','en-us.telephonyenhanced','amex_merchant amex_merchant1',environment=environment,email_ids=email_ids) # example with multiple aliases for the same grammar
    # addGrammar('http://anvil.tellme.com/~jgeorge/amex/us/merchant/slm_test_failure/Fold_1.cfg','en-us.telephonyenhanced','amex_merchant amex_merchant1',environment=environment,email_ids=email_ids,grammar_set=grammar_set) # example specifying grammar_set also while adding grammar

    ### Batch add grammars.  use a grammar file with one grammar name per line (e.g. ls > grammar_file.txt) prefix is the path to the grammars
    prefix = "http://anvil.tellme.com/~zbranson/batch_grammars/en_us/"
    grammar_file = "./grammars.txt"
    acoustic_model = "en-us.telephonyenhanced"
    batchAddGrammar(grammar_file=grammar_file,acoustic_model=acoustic_model,environment=environment,email_ids=email_ids,grammar_set=grammar_set,prefix=prefix)

    ### Assign alias example
    #assign_grammar_alias(existing_grammar_alias='amex_merchant2',new_grammar_aliases='amex_merchant',environment=environment,email_ids=email_ids) # example for command to assining a new alias to a grammar
    #assign_grammar_alias(existing_grammar_alias='amex_merchant2',new_grammar_aliases='amex_merchant',environment=environment,email_ids=email_ids,grammar_set=grammar_set) # example specifying grammar_set also for assign_alias request

    ### delete grammar example
    # deleteGrammar('account_summary-voice.grxml',environment=environment,email_ids=email_ids) # example for delete grammar command
    # deleteGrammar('amex_merchant1',environment=environment,email_ids=email_ids,grammar_set=grammar_set) # example for specifying grammar set also for delete grammar command

    ### request status examples
    #requeststatus(environment=environment) # this is to get status of the previous requests in the mentioned environment
    #requeststatus(environment=environment,lgs_request_id='ad03c8ba-0894-11e7-bea3-0050569178dc') # this is to get status of a particular lgs request

    ### get grammar list examples
    #get_grammar_list(environment=environment) # example to get a list of all grammars in the grammarset
    #get_grammar_list(environment=environment,grammar_alias='amex_merchant') # example to get a list of all aliases associated with a grammar
    # get_grammar_list(environment=environment,grammar_alias='amex_merchant',grammar_set=grammar_set) # example to get a list of all aliases associated with a grammar, specifying grammar_set as well

    ### remove grammar alias examples
    #remove_grammar_alias('amex_merchant1',environment=environment,email_ids=email_ids) # an example to remove a grammar alias. Please refer to method documentation before using this
    # remove_grammar_alias('amex_merchant1',environment=environment,email_ids=email_ids,grammar_set=grammar_set) # an example to remove a grammar alias.grammar_set also specified. Please refer to method documentation before using this
