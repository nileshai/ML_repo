#/!bin/python
import sys,os,codecs
import argparse
'''
This script generates 2 output files, one file in which the tagging will be done if it exactly mathces an utterance present in the reference tagged file.
& 2) A file for which exact match could not be found in the reference file
'''

encoding='utf-8'

parser = argparse.ArgumentParser(description='This script generates 2 output files, one file in which the tagging will be done if it exactly mathces an utterance present in the reference tagged file.& 2) A file for which exact match could not be found in the reference file')
parser.add_argument('-n','--new_file',help='The normalized file which have to be tagged.',required=True)
parser.add_argument('-r','--reference',help='The reference file with existing tags',required=True)
parser.add_argument('-o','--to_tag_output',help='The path of output file to be generated for entries that have to be tagged',required=True)
parser.add_argument('-a','--already_tagged_output',help='The path to output file which have the same text available from the reference tags',required=True)

args = vars(parser.parse_args())

#The new file that have to be tagged
inpfile1 = codecs.open(args['new_file'],'r',encoding=encoding)
#reference file based on which tagging have to be done
inpfile2 = codecs.open(args['reference'],'r',encoding=encoding)
#output file for which tagging have to be done based on classification output
outputfile = codecs.open(args['to_tag_output'],'w',encoding=encoding)
#output file for which the same normalized utterance is available in the reference file
oldtagsfile = codecs.open(args['already_tagged_output'],'w',encoding=encoding)

#mistagging file
mis_tag_filepath = 'mis_tag'
mis_tag_file = codecs.open(mis_tag_filepath,'w')

utts1= []
file_utt = {}


utts_reference={}
details = {}
mis_tag_utts = set()
for line in inpfile2.readlines():
    line = line.strip()
    cols = line.split("\t")
    utt=cols[1]
    granular_tag=cols[3]
    #sometimes there can be mis-tagging also
    if utts_reference.has_key(utt):
        if(utts_reference[utt]!=granular_tag):
            mis_tag_utts.add(utt)

    utts_reference[utt] = granular_tag
    lines_for_utt = details[utt] if details.has_key(utt) else []
    lines_for_utt.append(line)
    details[utt] = lines_for_utt


if( len(mis_tag_utts)>0):
    print "\nsome of the utterances have been tagged with multiple intents, please check the file,\n" + str(os.path.abspath(mis_tag_filepath)) + " \ncorrect these cases and run this script again"
    for utt in mis_tag_utts:
        for line in details[utt]:
            mis_tag_file.write(line+'\n')

#emptying the dictionary
details={}

#iterating through file which have to be tagged
for line in inpfile1.readlines():
    line = line.strip()
    cols = line.split("\t")
    file_name=cols[0]
    utt = cols[1]

    if utt not in utts_reference:
        #putting a random tag now, this will have to be tagged based on the classification output
        outputfile.write(file_name + "\t" + utt + "\t" + "none" + "\t" + "none" + "\n")
    else:
        granular_tag= utts_reference[utt]
        oldtagsfile.write(file_name + "\t" + utt + "\t" + granular_tag  + "\t" + granular_tag +"\n")




outputfile.close()
