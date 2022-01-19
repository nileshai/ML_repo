# coding: utf-8

'''
Created on March 24, 2017

@author: sruti.rallapalli
'''

import re, sys
###########################################################
    # This script is to create update a data file based on a list of tag corrections.
    # Matches the WC normalized utt after removing stopwords, against the cannonical utt in the corrections list.
    # Created to update the tags in Ebay UK training data, based on Mike's changes to the inconsistencies.
###########################################################

old_data= open(sys.argv[1],'r')
#old_data= open("/home/sruti.rallapalli/SSI-Experiments/Ebay/20170324-Update/TuningData_WCNormalized",'r')
old_data_lines = old_data.readlines()
corrected_tag_data = open(sys.argv[2],'r')
#corrected_tag_data = open("/home/sruti.rallapalli/SSI-Experiments/Ebay/20170324-Update/20160622c_Corrected_Tags.txt",'r')
new_tag_data = open(sys.argv[3],'w')
#new_tag_data = open("/home/sruti.rallapalli/SSI-Experiments/Ebay/20170324-Update/TuningData_WCNormalized_20170324",'w')
stopwords_file = open(sys.argv[4],'r')
stopwords_file = open("/home/sruti.rallapalli/SSI-Experiments/Ebay/20170324-Update/SupportingFiles/stopwords_temp.txt",'r')


stopwords=[]
for line in stopwords_file.readlines():
    line = line.split("\n")[0]
    line = line.strip()
    stopwords.append(line)

corrected_tags = {}
for line in corrected_tag_data.readlines():
    line = line.split("\n")[0]
    line = line.strip()
    corrected_tags[line.split("\t")[0].strip()] = line.split("\t")[1].strip()
keys = corrected_tags.keys()
for line in old_data_lines:
    line = line.split("\n")[0]
    line = line.strip()
    elements = line.split("\t")
    cannonical_words = elements[1].split()
    cannonical_form_after_stopwords = []
    for word in cannonical_words:
        if word not in stopwords:
            cannonical_form_after_stopwords.append(word)
    cannonical_form = ' '.join(w for w in cannonical_form_after_stopwords)
    print cannonical_form
    if corrected_tags.has_key(cannonical_form) :
        #print cannonical_form, corrected_tags.has_key(cannonical_form), corrected_tags[cannonical_form]
        new_tag_data.write(elements[0] + "\t" + elements[1] + "\t" + corrected_tags[cannonical_form] + "\t" + corrected_tags[cannonical_form] + "\n" )
        #print(elements[0] + "\t" + cannonical_form + "\t" + corrected_tags[cannonical_form] + "\t" + corrected_tags[cannonical_form])
    else:
        new_tag_data.write(line + "\n")
new_tag_data.close()
