import os
import sys
import re

if len(sys.argv)<4:
    print 'Usage: python src/norm_corpus.py <input_corpus> <norm_corpus> <class_flag(1/0)>\n'
    sys.exit(1)

input_corpus = sys.argv[1]    
norm_corpus = sys.argv[2]
class_flag = int(sys.argv[3])

if(class_flag==1):
    if len(sys.argv)!=5:
        print 'Usage: python src/norm_corpus.py <input_corpus> <norm_corpus> <class_flag(1/0)> <substitutions_file>\n'
        sys.exit(1)
    subs_file = sys.argv[4]

    strnew = str.replace
    f =  open(subs_file,'r')
    patterns = f.read().splitlines()
    f.close()

fo = open(norm_corpus,'w')
fp = open(input_corpus,'r')

for line in fp.readlines() :
    line = line.strip()
    wds = line.split()
    if(class_flag==1):
        for p in patterns:
            temp = p.split() 
            find = r'\b'+temp[0]+r'\b'
            replace = temp[1]
            line = re.sub(find,replace,line)
        
    if(len(wds)>=2):
        if(wds[0]=="<s>" and wds[len(wds)-1]=="</s>"):
            fo.write(line+"\n")
            continue;
#    fo.write("<s> " + line + " </s>\n")
    fo.write(line + "\n")


fp.close()    
fo.close()
