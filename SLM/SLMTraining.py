'''
Created on Feb 28, 2014

@author: anmol.walia
'''

import os, sys, re, ConfigParser

def formatDataForSLMTraining( output_file ):
    
    f =  open(config.get('params', 'class_substitutions_file'),'r')
    patterns = f.read().splitlines()
    f.close()
    
    fo = open( output_file, 'w' )
    
    fp = open( config.get('params', 'raw_corpus_file'), 'r' )
    for line in fp.readlines() :
        line = line.strip()
        
        if line=='':
            continue
         
        for p in patterns:
            temp = p.split( ) 
            line = re.sub(temp[0],temp[1],line)
    
        fo.write("<s> " + line + " </s>\n")
    
    fp.close()    
    fo.close()

def modifyARPA( input_arpa_file, output_arpa_file ):

    fp = open( input_arpa_file, 'r' )
    op1 = open( output_arpa_file, 'w' )
    
    flag = 0
    gram_flag = 0
    for i in fp.readlines():
        newline = i.strip()
        fstr = newline.split()
        if(flag>0):
            if(fstr[1]=="</s>"):
                val = float(fstr[0])*2
                val = "%.6f" % val
                op1.write(str(val)+' '+fstr[1]+' 0.0000000'+'\n')
                flag = flag-1
                continue;
            elif(fstr[1]=="<s>"):
                op1.write(str(val)+' '+fstr[1]+' '+fstr[2]+'\n')
                flag = flag-1
                continue;
        if newline.find("1-grams:")==1:
            flag=2
        if newline.find("1-grams:")==1:
            gram_flag=1
        if newline.find("2-grams:")==1:
            gram_flag=2
        if newline.find("3-grams:")==1:
            gram_flag=3
    
        gram_dim = gram_flag + 2
        if(len(fstr)!=gram_dim and len(fstr)>1):
            op1.write(newline+" 0.0000000"+"\n")
        else:
            op1.write(newline+'\n')
    
    fp.close()
    op1.close()

def trainSLM():
    
    ## Checking required files
    #for file in [class_substitutions_file, raw_corpus_file, SRILM_training_Tool, ARPA_2_CFG_tool]:
    for file in [config.get('params', 'raw_corpus_file'), config.get('params', 'class_substitutions_file'), config.get('params', 'raw_corpus_file'),config.get('params', 'SRILM_training_Tool') ]:
        if not os.path.isfile(file):
            raise Exception('Could not find '+file )
    
    
    ## Creating an output directory if it doesn't exist
    if not os.path.isdir(config.get('params', 'output_dir')):
        os.makedirs(config.get('params', 'output_dir'))
    
    base_file_name = os.path.splitext(os.path.basename(config.get('params', 'raw_corpus_file')))[0]
    formatted_corpus = os.path.join(config.get('params', 'output_dir'), base_file_name+'_formatted')
    ARPA_file = os.path.join(config.get('params', 'output_dir'), base_file_name+'.arpa')
    mod_ARPA_file = os.path.join(config.get('params', 'output_dir'), base_file_name+'_mod.arpa')
    #CFG_file = os.path.join(config.get('params', 'output_dir'), base_file_name+'.cfg')
    
    ## Replacing classes with grammar URLs and adding sentence beginning/end markers to each utterance
    formatDataForSLMTraining( formatted_corpus )
    
    ## Training SLM using SRILM
    os.system(config.get('params', 'SRILM_training_Tool') + 
              ' -text '+
              formatted_corpus+
              ' -ndiscount -lm '+
              ARPA_file)
    
    if not os.path.isfile(ARPA_file):
        raise Exception('SRLIM could not train SLM: '+ARPA_file )
        
    ## Modifying output ARPA file to adjust back-off probabilities for sentence beginning marker
    modifyARPA(ARPA_file, mod_ARPA_file)
    
    #os.system(ARPA_2_CFG_tool + ' -i '+
    #          mod_ARPA_file + 
    #          ' -t ARPA -o ' +
    #          CFG_file +
    #          ' -b "<s>" -e "</s>" -l 1033 -r Top -sf W3C -inittag "out={}; out.classsubstitution = gSubstitutions = [];"')
   
    #if not os.path.isfile(CFG_file):
    #    raise Exception('Could not convert ARPA to CFG' )       
    
if __name__ == '__main__':
    if len(sys.argv)!=2:
        print 'Usage: python SLMTraining.py <config_file>\n'
        sys.exit(1)
    
    config = ConfigParser.ConfigParser()
    config.readfp(open(sys.argv[1]))
    trainSLM()