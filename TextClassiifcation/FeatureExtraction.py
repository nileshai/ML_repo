from __future__ import division
from collections import defaultdict
import nltk, sys, csv
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import wordnet
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer, TfidfTransformer
from scipy.sparse import csr_matrix
import scipy.spatial.distance as dist
from nltk.corpus import stopwords
from scipy.cluster.hierarchy import linkage,fcluster, dendrogram
import numpy as np

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

def getTF(text):
    words = text.split()
    max_tf = words.count(max(set(words), key=words.count))
    return {i:words.count(i)/max_tf for i in set(words)}    

if __name__ == '__main__':
    token_dict = {}
    #data = csv.reader(open( 'E:\\tmp\\Chats\\Normalized_final.csv', 'rb'))
    #for chat in data:
    #    token_dict[chat[0]]=chat[2]
    
    id_list=[]
    utt_list=[]
    intent_dict={}
    intents=set([])
    for line in open('E:\\Data\\CapOne\\Credit_tracker\\dummy_chat_data_20141029a', 'r'):
        parts=line.split('\t')
        #token_dict[parts[0]]=parts[1]
        if parts[1].strip()=='':continue
            
        id_list.append(parts[0])
        utt_list.append(parts[1])
        intent_dict[parts[0]]=parts[2]
        intents.add(parts[2])
    print 'inside main'
    print len(utt_list)    
    stemmer = nltk.PorterStemmer()
    lmtzr = WordNetLemmatizer()
    lemmatized_words={}
    
    intent_index_vector = list(intents)
       
    stpwords=['um', 'uh']
    for words in open('E:\\Data\\CapOne\\Credit_tracker\\stopwords_chat', 'r'):
        stpwords.append(words.strip())
    intent_vectors={} 
    cv = CountVectorizer(min_df=1, tokenizer=tokenize, stop_words=stpwords, ngram_range=(1,3), max_features=5000)
    counts = cv.fit_transform(utt_list)
    print counts.shape
    row_ctr=0
    for row in counts:
        
        if intent_vectors.has_key(intent_dict.get(id_list[row_ctr])):
            intent_vectors[intent_dict.get(id_list[row_ctr])] = intent_vectors[intent_dict.get(id_list[row_ctr])] + row
        else:
            intent_vectors[intent_dict.get(id_list[row_ctr])] = row
        row_ctr+=1
    
    wr = csv.writer(open('E:\\Data\\CapOne\\Credit_tracker\\Clusters_20141029a\\Clustering_Output\\vocab.csv', 'wb'))
    for word, freq in cv.vocabulary_.iteritems():
        wr.writerow([word, freq])
    #print len(intent_vectors)
    #print intent_vectors.get('login_ivr-enter_digits').todense()    
    
    intent_count_matrix = csr_matrix((len(intent_index_vector), counts.shape[1]), dtype = 'int64')
    counts=None
    #print range(len(intent_index_vector))
    for intent_index in range(len(intent_index_vector)):
        #print intent_index_vector[intent_index], intent_index
        #print intent_vectors.get(intent).todense()
        intent_count_matrix[intent_index] = intent_vectors.get(intent_index_vector[intent_index])
    
    transformer = TfidfTransformer()
    transformer.fit(intent_count_matrix)
    intent_tf_idf_matrix = transformer.transform(intent_count_matrix)
    
    #print intent_tf_idf_matrix[intent_index_vector.index('login_ivr-enter_digits')].todense()
    
    print intent_tf_idf_matrix.shape
    distances= dist.pdist(intent_tf_idf_matrix.todense(), 'cosine')
    
    print distances.shape
    intent_tf_idf_matrix=None
    intent_vectors=None
    links=linkage(distances, method="average", metric="cosine")
    
    print links.shape
    
    wr = csv.writer(open('E:\\Data\\CapOne\\Credit_tracker\\Clusters_20141029a\\Clustering_Output\\clusters.csv', 'wb'))
    
    for threshold in np.arange(0.5,1,0.05):
        
        clusters = fcluster(links, threshold, criterion='distance')
            
        cluster_population=defaultdict(lambda: set([]))
        
        for intent_index in range(len(clusters)):
            cluster_population[clusters[intent_index]].add(intent_index_vector[intent_index])
        
        wr.writerow([threshold])
        for cluster, items in cluster_population.iteritems():
            wr.writerow([cluster]+list(items))
        wr.writerow([])
            
    #print sorted(cluster_population.items())
    sys.exit()
    
    
    tfidf = TfidfVectorizer(tokenizer=tokenize, stop_words=stpwords, ngram_range=(1,3) ,max_features = 5000)
    tfs = tfidf.fit_transform(utt_list)
    
    
    print tfs.shape
    
    
    #wr=open('E:\\Data\\Amex\\Amex-DefaultMenuNL_DataMaster_20140929c\\WC_v1\\Clusters\\vocab', 'w')
    #for name in tfidf.get_feature_names():
    #    wr.write(name+'\n')
    #wr.close()
    #print tfidf.get_stop_words()
    #print tfs.shape
    sys.exit()
    
    
    idf=defaultdict(int)
        
    tfs={}
    for chat in data:
        #print chat
        words = chat[2].split()
        for word in words:idf[word] += 1 
        tfs[chat[0]]=getTF(chat[2])
        
    feature_vec={word:idf.keys().index(word) for word in idf.keys()}
    
    print len(feature_vec)