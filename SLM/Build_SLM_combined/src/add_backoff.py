import os
import sys

if len(sys.argv)!=2:
    print 'Usage: python src/add_backoff.py <sample_input.arpa>\n'
    sys.exit(1)

input_arpa_file = sys.argv[1]

fp = open(input_arpa_file,'r')
op1 = open('Inter/inter.arpa','w')

flag = 0
gram_flag = 0
max_ngram=3
for i in fp.readlines():
    newline = i.strip()
    fstr = newline.split()
    if(flag>0):
        if(fstr[1]=="</s>"):
            val = float(fstr[0])*2
            val = "%.6f" % val
            op1.write(str(val)+' '+fstr[1]+' 0'+'\n')
            flag = flag-1
            continue;
        elif(fstr[1]=="<s>"):
            op1.write(str(val)+' '+fstr[1]+' 0'+'\n')
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
    if(gram_flag<max_ngram and len(fstr)!=gram_dim and len(fstr)>1):
        op1.write(newline+" 0"+"\n")
    else:
        op1.write(newline+'\n')

fp.close()
op1.close()

