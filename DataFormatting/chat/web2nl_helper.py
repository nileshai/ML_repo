# -*- coding: utf-8 -*-
import sys,os,time,json,ConfigParser,urllib,urllib2,codecs
#import pandas as pd

def getClassificationAPIResponse(params, modelUrlName,req_no):
    #inputFile = open(params['inputFile'],'r')
    #inputSentence = inputFile.readline()
    inputSentence=params['inputSentence']
    modelFileUrl = params[modelUrlName]
    inputSentence = urllib.quote_plus(inputSentence)
    queryString = '%20'.join(inputSentence.split(" "))
    '''queryParams = {
                'q' : queryString,
                'modelUrl' : urllib.quote_plus(modelFileUrl),
                'maxIntents': params['maxIntents'],
                'verbose' : 'true',
                }

    '''
    #new url
    requestUrl='http://stable.api.sv2.247-inc.net/v1/classifier/intents?'+"q="+queryString+"&"+"modelurl="+modelFileUrl+"&"+"maxintents="+params['maxIntents']+"&"+"verbose="+str(verbose).lower()+"&api_key=vDL86ZYsZqGBMGrj"
    #old url...this will also work
    #requestUrl="http://web2nl-stable.api.247-inc.net:80/v1/intents?"+"q="+queryString+"&"+"modelurl="+modelFileUrl+"&"+"maxintents="+params['maxIntents']+"&"+"verbose="+"true"+"&api_key=vDL86ZYsZqGBMGrj"
    #validations url
    #requestUrl="http://web2nl-stable.api.247-inc.net:80/v1/classifier/validations?"+"modelurl="+modelFileUrl+"&api_key=vDL86ZYsZqGBMGrj"
    headers={'User-agent' : 'Mozilla/5.0',
         'X-TFS-SessionId':'web2nl',
         'X-TFS-RequestId':'web2nl_request'+str(req_no),
         'X-TFS-LogString':'api request to web2nl line no'+str(req_no)
    }
    if(proxy_url!=""):
        proxy = urllib2.ProxyHandler({'http': proxy_url})
        opener = urllib2.build_opener(proxy)
        urllib2.install_opener(opener)

    request = urllib2.Request(requestUrl,None,headers)

    responseString=''
    retry=True
    max_retries=5
    count=0
    exception_thrown=''
    while(retry and (count<max_retries)):
        try:
            time.sleep(.1)
            count+=1
            response = urllib2.urlopen(request,timeout=4)
            responseString = response.read()
            retry=False
        except urllib2.URLError as e:
            failure_message_file = open('failure_message.txt','a')
            failure_message_file.write('connection failed due to ' + str(e)+"\n")
            failure_message_file.close()
            print str(req_no) +' connection failed due to ' + str(e) +' *******************************\n'
            exception_thrown=e
            time.sleep(20)
        except Exception as e:
            failure_message_file = open('failure_message.txt','a')
            failure_message_file.write('connection failed due to ' + str(e)+"\n")
            failure_message_file.close()
            print str(req_no) +' connection failed due to '+ str(e) +' *******************************\n'
            exception_thrown=e
            time.sleep(20)
    #print 'response String ' + responseString
    if(count==max_retries):
        print 'exceeded max retry attempts for web2nl hit, check if the web2nl api is working properly and the string being passed for classification is valid'
        raise exception_thrown
    response = json.loads(responseString)
    return response


def compare_workbench_web2nl(workbench_output,web2nl_output,comparison_output):
    df = pd.read_csv(workbench_output, sep=',', header=0)
    df2=pd.read_csv(web2nl_output, sep=',', header=0)
    web2nl = df2[['Id','Classified Intent 1','Classification Score 1']]
    web2nl.columns=['Id','web2nl_classified','web2nl_score']
    m = (df.merge(web2nl,on='Id'))
    m['is_same'] = m['Classified Intent 1']==m['web2nl_classified']
    m['score_diff']= abs(m['Classification Score 1']-m['web2nl_score'])
    m['diff_large'] = m['score_diff']>.01
    m.to_csv(comparison_output, sep=',', index_label=False,index=False,encoding='utf-8')

def get_headers(is_hierarchy):
    output_cols=['Id','Utterance','Original Intent','Original Granular Intent','Final Processed String','Classified Intent 1','Classification Score 1','Classified Intent 2','Classification Score 2','Diff between Top Intents','Recognition Source','Correct Classification','Is crossed threshold','is correct and crossed threshold']
    if is_hierarchy:
        output_cols=['Id','Utterance','Original Intent','Original Granular Intent','Final Processed String','ClassifiedRUIntent','ClassificationScoreRU','Classified Intent 1','Classification Score 1','Classified Intent 2','Classification Score 2','Diff between Top Intents','Recognition Source','Correct Classification','Is crossed threshold','is correct and crossed threshold']
    return output_cols

def get_classified_output(params,cols,intent_model_url,root_intent,out_of_domain,line_no,is_hierarchy,custom_encoding):
    intent_index=3
    utt_index=1
    params['model_url']=intent_model_url[root_intent]
    intent_line = cols[utt_index]
    verbose_out=''

    diff = 0.0
    granular_intent1 = out_of_domain
    granular_intent1_score= 0.0
    granular_intent2 = ""
    granular_intent2_score= 0.0
    reco_source = "web2nl"
    first_level_intent = ''
    first_level_score= ''
    last_input_string=''
    output_cols=[]
    output_cols.append(cols[0])
    output_cols.append(cols[utt_index])
    output_cols.append(cols[2])
    output_cols.append(cols[3])
    #TODO might have to pass empty strings also for classification & check the output
    if(intent_line.strip()):
        intent_line_encoded = intent_line.encode(custom_encoding)
        #the normalization is done only if a normalized model is provided
        normalized_input,verbose_out_normalization = get_normalized_output(intent_line_encoded,normalization_model,line_no)
        params['inputSentence']=normalized_input

        first_level_response = getClassificationAPIResponse( params, 'model_url',line_no)
        if(verbose_out_normalization!=""):
            verbose_out= verbose_out_normalization
        verbose_out += '\t' +str(first_level_response)
        LAST_INPUT='lastInput'
        INTENTS = 'intents'
        CLASSNAME = 'className'
        SCORE ='score'
        last_input_string=first_level_response[LAST_INPUT]
        intents= first_level_response[INTENTS]
        first_level_intent = intents[0][CLASSNAME]
        first_level_score= intents[0][SCORE]

        if (first_level_intent in intent_model_url):
            #calling the 2nd model
            params['model_url'] = intent_model_url[first_level_intent]
            api_response = getClassificationAPIResponse( params, 'model_url',line_no)
            verbose_out+='\t' + str(api_response)
            last_input_string=api_response[LAST_INPUT]
            intents= api_response[INTENTS]
            granular_intent1 = intents[0][CLASSNAME]
            granular_intent1_score = intents[0][SCORE]
            if len(intents)>1:
                granular_intent2 =intents[1][CLASSNAME]
                granular_intent2_score = intents[1][SCORE]
        else:
            #this is the case in which a 2nd model is not called. i.e either the intent is not divided further or  it's the non- hierarchical case
            granular_intent1 = first_level_intent
            granular_intent1_score = first_level_score
            if len(intents)>1:
                granular_intent2= intents[1][CLASSNAME]
                granular_intent2_score= intents[1][SCORE]

    verbose_out=verbose_out.encode(custom_encoding)
    diff = granular_intent1_score-granular_intent2_score
    is_correct = (cols[intent_index]==granular_intent1)
    threshold = get_intent_threshold(granular_intent1)
    is_crossed_threshold =float(granular_intent1_score)>threshold
    is_correct_and_crossed_threshold= is_correct and is_crossed_threshold
    output_cols.append(last_input_string)
    if(is_hierarchy):
        #if it's a hierarchical model then the RU intent & the score is also added to the classification output file
        output_cols.append(first_level_intent)
        output_cols.append(str(first_level_score))
    output_cols.append(granular_intent1)
    output_cols.append(str(granular_intent1_score))
    output_cols.append(granular_intent2)
    output_cols.append(str(granular_intent2_score))
    output_cols.append(str(diff))
    output_cols.append(reco_source)
    output_cols.append(str(is_correct))
    output_cols.append(str(is_crossed_threshold))
    output_cols.append(str(is_correct_and_crossed_threshold))
    return output_cols, verbose_out

def get_normalized_output(intent_line,normalization_model,req_no,proxy_url='',encoding='utf8',verbose=False):
    normalized_output = intent_line.encode(encoding)
    intent_line = normalized_output
    verbose_out=''
    if(normalization_model.strip()!=""):
        #have to perform normalization
        inputSentence = urllib.quote_plus(intent_line)

        queryString = '%20'.join(inputSentence.split(" "))
        requestUrl='http://stable.api.sv2.247-inc.net/v1/classifier/normalizations?'+"q="+queryString+"&"+"modelurl="+normalization_model+"&"+"verbose="+str(verbose).lower()+"&api_key=vDL86ZYsZqGBMGrj"
        headers={'User-agent' : 'Mozilla/5.0',
             'X-TFS-SessionId':'web2nl',
             'X-TFS-RequestId':'web2nl_request'+str(req_no),
             'X-TFS-LogString':'normalization api request to web2nl line no'+str(req_no)
        }
        if(proxy_url!=""):
            proxy = urllib2.ProxyHandler({'http': proxy_url})
            opener = urllib2.build_opener(proxy)
            urllib2.install_opener(opener)

        request = urllib2.Request(requestUrl,None,headers)

        responseString=''
        retry=True
        max_retries=5
        count=0
        exception_thrown=''
        while(retry and (count<max_retries)):
            try:
                time.sleep(.1)
                count+=1
                response = urllib2.urlopen(request,timeout=4)
                responseString = response.read()
                retry=False
            except urllib2.URLError as e:
                failure_message_file = open('failure_message.txt','a')
                failure_message_file.write('connection failed due to ' + str(e)+"\n")
                failure_message_file.close()
                print str(req_no) +' connection failed due to ' + str(e) +' for normalization model *******************************\n'
                exception_thrown=e
                time.sleep(20)
            except Exception as e:
                failure_message_file = open('failure_message.txt','a')
                failure_message_file.write('connection failed due to ' + str(e)+"\n")
                failure_message_file.close()
                print str(req_no) +' connection failed due to ' + str(e) +' for normalization model *******************************\n'
                exception_thrown=e
                time.sleep(20)
        #print 'response String ' + responseString
        if(count==max_retries):
            print 'exceeded max retry attempts for web2nl hit, check if the web2nl api is working properly and the string being passed for classification is valid'
            raise exception_thrown
        response = json.loads(responseString)
        normalized_output=response['lastInput']
        verbose_out = str(response)
    return normalized_output,verbose_out


def write_web2nl_output(input_file_path,output_dir,intent_model_url,root_intent,out_of_domain,custom_encoding):
    output_file_path=os.path.join(output_dir,'Classification_Output.csv')
    output_file_verbose=os.path.join(output_dir,'Classification_Output_verbose.csv')
    is_hierarchy = len(intent_model_url)>1
    out_of_domain='none-none'
    params = {}
    params['model_url']=intent_model_url[root_intent]
    params['maxIntents']='3'

    sep='\t'
    output_sep=','
    fin=codecs.open(input_file_path,'r',encoding=custom_encoding)
    of = codecs.open(output_file_path,'w+',encoding=custom_encoding)
    if(verbose):
        fout_verbose=codecs.open(output_file_verbose,'w+',encoding=custom_encoding)
    #of = open(output_file_path,'a')
    line_no=1
    reco_source='web2nl'
    utt_index=1
    intent_index=2
    try:
        for line in fin:
            #print line_no
            line=line.rstrip('\n')
            line=line.rstrip('\r')
            cols = line.split(sep)
            output_cols=[]
            output_string=''
            if(line_no==1):
                output_cols=get_headers(is_hierarchy)

                output_string = (output_sep).join(output_cols) +'\n'
                of.write(output_string)
                #line_no+=1
                #continue


            output_cols, verbose_output = get_classified_output(params,cols,intent_model_url,root_intent,out_of_domain,line_no,is_hierarchy,custom_encoding)
            output_string = (output_sep).join(output_cols)+'\n'
            of.write(output_string)
            if(verbose):
                fout_verbose.write(str(output_cols[0])+'\t' + str(verbose_output)+'\n')
            line_no+=1
            if(line_no%100==0):
                print "completed line " + str(line_no)
    except Exception as e:
        print "error occured for line " + str(line_no)
        ##commented because sometimes priting this error would cause issues. uncomment if you are tryig to debug
        print e
    of.close()
    fin.close()


def get_intent_threshold(intent_name):
    return intent_thresholds[intent_name] if intent_thresholds.has_key(intent_name) else 0.0

if __name__=="__main__":
    start_time = time.time()
    config_file = 'web2nl-Config.cfg'
    if len(sys.argv)!=2:
        print 'Usage: python web2nl.py <config_file>'
        print 'Using default location for config file '
    else:
        config_file = sys.argv[1]
    print 'config file location is - ' + os.path.abspath(config_file)
    if(not os.path.exists(config_file)):
        print 'unable to find file at ' + os.path.abspath(config_file)
        print 'please create a config file '+config_file + ' by referring to the config template file - web2nl-Config_template.cfg'
        sys.exit()
    config = ConfigParser.ConfigParser()
    config.readfp(open(config_file))

    custom_encoding=config.get('params','encoding')

    input_file = config.get('params','inp_data')
    output_dir=config.get('params','output_dir')
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)


    model_url = config.get('params','root_model_url')
    out_of_domain_intent = config.get('params','out_of_domain_intent')
    root_intent=''
    intent_model_url={}
    intent_hierarchy_file = config.get('params','intent_hierarchy_file')
    model_base_url= model_url[:model_url.rindex('/')]
    if(intent_hierarchy_file=="" or not os.path.exists(intent_hierarchy_file)):
        print 'flat model case'
        end_index = len(model_url) if('.' in model_url)  else model_url.rindex('.')
        model_name=model_url[model_url.rindex('/'):end_index]
        root_intent = model_name
        intent_model_url[model_name]=model_url
    else:
        for line in open(intent_hierarchy_file):
            model_name = line[:line.index(':')]
            if(root_intent==''):
                #the first line is taken as the root intent
                root_intent = model_name
            intent_model_url[model_name] = model_base_url+'/'+model_name + '.model'

    intent_thresholds_file = config.get('params','intent_thresholds_file')
    intent_thresholds = {}
    if(intent_thresholds_file!="" and os.path.exists(intent_thresholds_file)):
        print 'using the provided intent thresholds file- '+intent_thresholds_file
        for line in open(intent_thresholds_file):
            line=line.strip()
            parts = line.split(',')
            intent_name=parts[0]
            intent_thres=float(parts[1])
            intent_thresholds[intent_name]=intent_thres
    else:
        print 'intent threshold file not found. using default threshold of 0.0 for all intents'


    normalization_model= config.get('params','normalization_model_url')
    if(normalization_model.strip()!=""):
        print 'normalization model url provided, hence will call this model before calling the classification model. url - ' +  normalization_model
    verbose = False
    if(config.get('params','verbose').strip().lower()=='true'):
        verbose=True

    #proxy_url = 'webproxy.cell.sv2.tellme.com'
    #proxy_url = 'http://cache.backside.sv2.tellme.com:3128'
    proxy_url = config.get('params','proxy')
    write_web2nl_output(input_file,output_dir,intent_model_url,root_intent,out_of_domain_intent,custom_encoding)
    #compare_workbench_web2nl(workbench_output,web2nl_output_file_path,compare_workbench_web2nl)
    end_time = time.time()
    print "Total execution time : " + str(end_time-start_time) + " secs"



