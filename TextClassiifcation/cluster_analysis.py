# -*- coding: utf-8 -*-
from __future__ import division
from collections import defaultdict
import nltk, sys, csv, collections, os, subprocess, glob, time, logging,codecs,re
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import wordnet
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer, TfidfTransformer
from scipy.sparse import lil_matrix
import scipy.spatial.distance as dist
from nltk.corpus import stopwords
from scipy.cluster.hierarchy import linkage,fcluster, dendrogram
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from logging import Logger

custom_encoding="utf-8"

# defining regexes for replacing
to_remove = re.compile(u"\[speech_in_noise")
#this is right quot mark
r1 = re.compile(u"’")
#this is non breaking space
r2 = re.compile(u"\xa0")

them = re.compile(u"'em")
def clean_transcription(utt):
    #the replacements done here are after checking the data. more replacements will have to be added in the future
    #there are programs to automatically replace the unicode character with similar ascii character, but we are not using them here
    utt = to_remove.sub("",utt)
    utt = r1.sub("'",utt)
    utt = r2.sub(u" ",utt)
    utt = them.sub("them",utt)
    return utt

def stem_tokens(tokens, stemmer):
    stemmed = []
    for item in tokens:
        stemmed.append(stemmer.stem(item))
    return stemmed

def get_wordnet_pos(treebank_tag):

    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    #elif treebank_tag.startswith('N'):
    #    return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN

def tokenize(text):

    lemmatized=[]
    for word in text.split():
        if lemmatized_words.has_key(word):
            lemmatized.append(lemmatized_words[word])
            continue

        pos_tagged = nltk.pos_tag([word])
        lemma = lmtzr.lemmatize(word, get_wordnet_pos(pos_tagged[0][1]))
        lemmatized_words[word] = lemma
        lemmatized.append(lemma)

    #pos_tagged = nltk.pos_tag(text.split())
    #for tup in pos_tagged:
    #    lemmatized.append(lmtzr.lemmatize(tup[0], get_wordnet_pos(tup[1])))

    return lemmatized

#def tokenize(text):
    #tokens = nltk.word_tokenize(text)
    #tokens = text.split()
    #stems = stem_tokens(tokens, stemmer)
#    return lemmatize_tokens(text.split())

def calcCosineSimForIntents(tf_idf_matrix, output_csv_file):

    sim_string=''

    wr_1 = csv.writer(open(output_csv_file, 'wb'))
    sorted_intents=[value for (key, value) in sorted(intent_vector_indices.items())]
    wr_1.writerow([""]+sorted_intents)

    intents_traversed=set(sorted_intents)
    row_ctr=0
    for row in intent_tf_idf_matrix:
        #similarity_matrix = cosine_similarity(row, intent_tf_idf_matrix)
        similarities = []
        similarities.append(sorted_intents[row_ctr])
        #print "cosine similarity output dimensions",cosine_similarity(row, intent_tf_idf_matrix).shape
        intent_ctr=0
        for x in cosine_similarity(row, intent_tf_idf_matrix)[0]:
            similarities.append(x)
            if (x>0.5 and (sorted_intents[row_ctr] in intents_traversed) and row_ctr!=intent_ctr):
                sim_string+= sorted_intents[row_ctr].name+","+sorted_intents[intent_ctr].name+","+str(x)+"\n"
            intent_ctr+=1
        intents_traversed.remove(sorted_intents[row_ctr])

        wr_1.writerow([sorted_intents[row_ctr]] + [x for x in cosine_similarity(row, intent_tf_idf_matrix)[0]])
        row_ctr+=1

    return sim_string

def getTF(text):
    words = text.split()
    max_tf = words.count(max(set(words), key=words.count))
    return {i:words.count(i)/max_tf for i in set(words)}

def writeClusters(threshold):
    clusters = fcluster(links, threshold, criterion='distance')
    cluster_population=defaultdict(lambda: set([]))
    biggest_cluster=''
    biggest_cluster_utt_freq=0
    print len(clusters)
    for intent_index in range(len(clusters)):
        cluster_population[clusters[intent_index]].add(intent_vector_indices[intent_index])
        wr.writerow([threshold])
        if not os.path.exists(os.path.join(cluster_data_dir,'Thresh_'+str(threshold))):os.makedirs(os.path.join(cluster_data_dir,'Thresh_'+str(threshold)))
        data_writer=open(os.path.join(cluster_data_dir,'Thresh_'+str(threshold),"data_file"), 'w')
        clustering_info_writer = open(os.path.join(cluster_data_dir,'Thresh_'+str(threshold),"cluster_definition"), 'w')
        for cluster, items in cluster_population.iteritems():
            total_cluster_utts=0
            for x in items:
                total_cluster_utts+=x.getUttFreq()
                for utt in x.utts:
                    data_writer.write(utt.id+'\t'+utt.text+'\t'+'Clust_'+str(cluster)+'\t'+x.name+'\n')
                    wr.writerow([cluster,total_cluster_utts]+[x.name for x in items])
                    if total_cluster_utts>biggest_cluster_utt_freq:
                            biggest_cluster='Clust_'+str(cluster)
                            biggest_cluster_utt_freq=total_cluster_utts
                clustering_info_writer.write('Clust_'+str(cluster)+'\t'+str([x.name for x in items])+'\n')

    wr.writerow([])
    data_writer.close()
    clustering_info_writer.close()

class intent:

    def __init__(self,name):
        self.name=name
        self.utts=[]
        self.total_feature_count_vector=None

    def getUttFreq(self):
        return len(self.utts)

    def addUtt(self,utt):
        self.utts.append(utt)

class utterance:
    text=None
    intent=None
    def __init__(self,id):
        self.id=id

if __name__ == '__main__':

    input_data = 'FirstResponses_WCNormalized'
    output_dir = 'Cluster_set'
    stop_words_file='SupportingFiles/stopwords_v2.txt'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    logger_file= codecs.open(os.path.join(output_dir,'Log_'+str(time.time()).replace('.','')),'w',encoding=custom_encoding)
    stemmer = nltk.PorterStemmer()
    lmtzr = WordNetLemmatizer()
    lemmatized_words={}
    intents={}
    intent_vector_indices={}
    utterance_vector_indices={}
    data_row_ctr=0

    for line in codecs.open(input_data, 'r',encoding=custom_encoding):
        parts=line.strip().split('\t')
        #token_dict[parts[0]]=parts[1]
        if parts[1]=='':continue

        if not intents.has_key(parts[2]):
            intents[parts[2]]=intent(parts[2])
            intent_vector_indices[len(intents)-1]=intents[parts[2]]

        utt_object=utterance(parts[0])
        utt_object.intent=intents[parts[2]]
        utt_object.text=parts[1]
        intents[parts[2]].addUtt(utt_object)
        utterance_vector_indices[data_row_ctr]=utt_object
        data_row_ctr+=1

    stpwords=['um', 'uh']
    for words in codecs.open(stop_words_file, 'r',encoding=custom_encoding):
        stpwords.append(words.strip())

    cv = CountVectorizer(min_df=1, tokenizer=tokenize, stop_words=stpwords, ngram_range=(1,3), max_features=None)
    counts = cv.fit_transform([utterance_vector_indices[x].text for x in range(len(utterance_vector_indices))])

    print "Count matrix shape",counts.shape
    for utt_index,utt_obj in utterance_vector_indices.iteritems():
        if utt_obj.intent.total_feature_count_vector==None:utt_obj.intent.total_feature_count_vector=counts[utt_index]
        else:utt_obj.intent.total_feature_count_vector=utt_obj.intent.total_feature_count_vector+counts[utt_index]

    wr = csv.writer(codecs.open(os.path.join(output_dir,'vocab.csv'), 'wb',encoding=custom_encoding))
    for word, freq in cv.vocabulary_.iteritems():
        wr.writerow([word, freq])
    intent_count_matrix = lil_matrix((len(intent_vector_indices), counts.shape[1]), dtype = 'int64')
    for intent_index,utt_obj in intent_vector_indices.iteritems():
        intent_count_matrix[intent_index] = utt_obj.total_feature_count_vector

    transformer = TfidfTransformer()
    transformer.fit(intent_count_matrix)
    intent_tf_idf_matrix = transformer.transform(intent_count_matrix)
    print "intent_tf_idf_matrix",intent_tf_idf_matrix.shape

    logger_file.write( calcCosineSimForIntents(intent_tf_idf_matrix, os.path.join(output_dir,'cosine_similarity.csv')))
    logger_file.flush()

    distances= dist.pdist(intent_tf_idf_matrix.todense(), 'cosine')

    intent_tf_idf_matrix=None
    intent_vectors=None
    links=linkage(distances, method="average", metric="cosine")
    clustersfile = open(os.path.join(output_dir,'clusters.csv'), 'wb')
    wr = csv.writer(clustersfile)

    cluster_data_dir=os.path.join(output_dir,'Clustered_Data')
    if not os.path.exists(cluster_data_dir):os.makedirs(cluster_data_dir)

    for threshold in np.arange(0.5,1,0.05):
        #writeClusters(threshold)
        clusters = fcluster(links, threshold, criterion='distance')
        cluster_population=defaultdict(lambda: set([]))
        biggest_cluster=''
        biggest_cluster_utt_freq=0

        for intent_index in range(len(clusters)):
            cluster_population[clusters[intent_index]].add(intent_vector_indices[intent_index])
        wr.writerow([threshold])
        if not os.path.exists(os.path.join(cluster_data_dir,'Thresh_'+str(threshold))):os.makedirs(os.path.join(cluster_data_dir,'Thresh_'+str(threshold)))
        data_writer=codecs.open(os.path.join(cluster_data_dir,'Thresh_'+str(threshold),"data_file"), 'w',encoding=custom_encoding)
        clustering_info_writer = codecs.open(os.path.join(cluster_data_dir,'Thresh_'+str(threshold),"cluster_definition"), 'w',encoding=custom_encoding)
        cluster_def_string=''
        cluster_def_string_temp=''
        root_clust_intent=set()
        clust_count=0
        cluster_new_name_old={}
        for cluster, items in cluster_population.iteritems():
            total_cluster_utts=0
            cluster_name=''
            is_in_root= len(items)==1
            for x in items:
                total_cluster_utts+=x.getUttFreq()
                for utt in x.utts:
                    if(is_in_root):
                        data_writer.write(utt.id+'\t'+utt.text+'\t'+x.name+'\t'+x.name+'\n')
                        root_clust_intent.add(x.name)
                    else:
                        cluster_old_name='Clust_'+str(cluster)
                        if(not cluster_new_name_old.has_key(cluster_old_name)):
                            clust_count+=1
                            cluster_new_name_old[cluster_old_name]='clust_'+str(clust_count)

                        cluster_name=cluster_new_name_old[cluster_old_name]
                        data_writer.write(utt.id+'\t'+utt.text+'\t'+cluster_name+'\t'+x.name+'\n')
                        root_clust_intent.add(cluster_name)
            wr.writerow([cluster,total_cluster_utts]+[x.name for x in items])
            if total_cluster_utts>biggest_cluster_utt_freq:
                biggest_cluster='Clust_'+str(cluster)
                biggest_cluster_utt_freq=total_cluster_utts
            if not is_in_root:
                cluster_def_string_temp += cluster_name+':'+','.join([x.name for x in items])+'\n'
        temp = list(root_clust_intent)
        temp.sort()
        cluster_def_string='root_intent:'+','.join(temp)+'\n'+cluster_def_string_temp
        clustering_info_writer.write(cluster_def_string)
        wr.writerow([])
        data_writer.close()
        clustering_info_writer.close()
    clustersfile.close()


##    writeClusters(threshold)

##        if len(cluster_population)>5:
##
##            config_writer= open(os.path.join(cluster_data_dir,'Thresh_'+str(threshold),'Config.cfg'),'w')
##            for line in open(r'E:\Data\CapOne\Credit_tracker\20150123a_withoutResponses_Incomplete\Credit_tracker_synth_Data\Config_template.cfg','r'):
##                if ('#' not in line):
##                    if 'output_folder' in line:
##                        line=line.replace('<PLACE_HOLDER>',os.path.join(cluster_data_dir,'Thresh_'+str(threshold),'SSI').replace('\\','\\\\'))
##                    elif 'data_file' in line:
##                        line=line.replace('<PLACE_HOLDER>',os.path.join(cluster_data_dir,'Thresh_'+str(threshold),"data_file").replace('\\','\\\\'))
##                    elif 'out_of_domain_intent' in line:
##                        line=line.replace('<PLACE_HOLDER>',biggest_cluster)
##                    config_writer.write(line)
##            config_writer.close()
##            jar_file='E:\\Development\\SSI_mod.jar'
##
##
##            os.chdir(os.path.join(cluster_data_dir,'Thresh_'+str(threshold))) # change to our test directory
##            #print 'C:\\Program/ Files/ (x86)\\Java\\jre7\\bin\\java.exe -Xms1096M -Xmx1096M -jar '
##            logger_file.write( 'Performing SSI experiment for Thresh_'+str(threshold)+' having '+str(len(cluster_population))+' clusters')
##            logger_file.flush()
##            subprocess.call(['C:\\Program Files (x86)\\Java\\jre7\\bin\\java.exe','-Xms1096M', '-Xmx1096M', '-jar',jar_file])
##
##            Log_files=glob.glob(os.path.join(cluster_data_dir,'Thresh_'+str(threshold),'SSI','Log_*'))
##
##            if len(Log_files)==0:
##                print 'No Log file found'
##                continue
##
##            log_file=max(Log_files,key=os.path.getctime)
##            for log in open(log_file, 'r'):
##                if '[SSI_mod] INFO - Average Weighted' in log:
##                    logger_file.write( log.strip()+'\n')
##                    logger_file.flush()
##                elif '[SSI_mod] INFO - Average Accuracy' in log:
##                    logger_file.write( log.strip()+'\n')
##                    logger_file.flush()
##
##        #os.chdir(startingDir) # change back to where we started
##    logger_file.close()


