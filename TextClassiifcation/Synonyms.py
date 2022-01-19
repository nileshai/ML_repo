'''
Created on Sep 15, 2014

@author: anmol.walia
'''
import csv, nltk, sets, FeatureExtraction, re, collections, operator
from nltk.corpus import wordnet as wn
from scipy.stats import norm
from nltk.stem.wordnet import WordNetLemmatizer

def calcBNSScores(inp_file, out_file, stopword_file):
    
    stopwords=set([])
    for lines in open(stopword_file, 'r'):
        stopwords.add(lines.strip())
    lmtzr = WordNetLemmatizer()
    
    suggestions={}
    
    word_cnts_for_BNS = collections.defaultdict(lambda:collections.defaultdict(lambda:0))
    intents=collections.defaultdict(lambda:0)
    total_docs = 0
    
    for row in open(inp_file,'r'):
        parts = row.split('\t')
        words = set([x for x in parts[1].split() if x not in stopwords])
        
        stemmed_words=set([])
        for word in words:
            pos_tagged = nltk.pos_tag([word])
            stemmed_words.add(lmtzr.lemmatize(word, FeatureExtraction.get_wordnet_pos(pos_tagged[0][1])))
            
        #for word in words:
        #    if word in stopwords:words.remove(word)
        intents[parts[2]]+=1
        intents['total']+=1
        total_docs+=1
        for word in stemmed_words:
            if not suggestions.has_key(word):
                syn = wn.synsets(word)
                synonymys = set([s.name.split('.')[0] for s in syn[:8]])
                if ((synonymys!=None) and (word in synonymys)):synonymys.remove(word)
                
                hypernyms = set([x.name.split('.')[0] for x in s.hypernyms()[:8] for s in syn[:8]])
                if ((hypernyms!=None) and (word in hypernyms)):hypernyms.remove(word)
                
                suggestions[word]=set(list(synonymys)+list(hypernyms))
                
            word_cnts_for_BNS[word][parts[2]]+=1
            word_cnts_for_BNS[word]['total']+=1
            
    #print intents        
    BNS_scores = collections.defaultdict(lambda:collections.defaultdict(lambda:0))
    for word,intent_dict in word_cnts_for_BNS.iteritems():
        for intent, count in intent_dict.iteritems():
            if intent == 'total':continue
            if not intents.has_key(intent):
                print intents.keys()
                raise Exception('Intent not found: '+intent)
            
            tpr = float(count)/intents[intent]
            if tpr==1:tpr=1.00-0.00005
            
            fp = intent_dict['total'] - count
            if fp==0:fpr=0.00005
            else:fpr = float(fp)/(intents['total'] - intents[intent])
            #bns = norm.ppf(norm.cdf(tpr)) - norm.ppf(norm.cdf(fpr))
            bns = norm.ppf(tpr) - norm.ppf(fpr)
            BNS_scores[intent][word]=bns
    
    wr = open(out_file, 'w')
    for intent, word_dict in BNS_scores.iteritems():
        wr.write('\n'+intent+'\n')
        for word, bns_score in sorted(word_dict.iteritems(), key=operator.itemgetter(1),reverse=True):
            wr.write(word+' : '+str(bns_score))
            if suggestions.has_key(word):
                wr.write('  '+str(suggestions[word])+'\n')
        
    wr.close()
    

words=set([])
wr=csv.writer(open('E:\\Data\\CapOne\\Credit_tracker\\syns.csv', 'wb'))
wr.writerow(['word','Part_of_Speech','Synonyms'])
for row in csv.reader(open('E:\\Data\\CapOne\\Credit_tracker\\CreditTracker_SynthData.csv', 'rb')):
    #print row
    if row[1]=='':
        continue
    text = re.sub(r"\?|\!|\(|\)|\[|\]|\"|~|\+|,|{|}|:|;|\*|\|", ' ', row[1].lower())
    text = re.sub(r"\.|<s>|=|/|\-|>|<|`|\\|\^| \' " , ' ', text)
    parts = text.split() 
    
    for word in parts:
        
        if (word in words) or word.startswith('<'):         
            continue 
        word
        pos=nltk.pos_tag([word])
        #if not pos[0][1].startswith('N'):
        #    wr.writerow([word, pos[0][1]])
            #print pos[0][1]
        #    continue
        #syn = wn.synsets(word, pos=FeatureExtraction.get_wordnet_pos(pos[0][1]))
        syn = wn.synsets(word)
        #print word
        synonymys = set([s.name.split('.')[0] for s in syn[:8]])
        if ((synonymys!=None) and (word in synonymys)):synonymys.remove(word)
        
        hypernyms = set([x.name.split('.')[0] for x in s.hypernyms()[:8] for s in syn[:8]])
        if ((hypernyms!=None) and (word in hypernyms)):hypernyms.remove(word)
        
        wr.writerow([word, pos[0][1]]+ list(synonymys)+ list(hypernyms))
            #print syn
        #print '+++++++++++++'
        words.add(word)


    

if __name__ == '__main__':
    calcBNSScores('E:\\Data\\CapOne\\Credit_tracker\\dummy_chat_data', 
                  'E:\\Data\\CapOne\\Credit_tracker\\BNS_scores',
                  #'E:\\Development\\SupportingFiles\\stopwords_dummy.txt')
                  'E:\\Data\\CapOne\\Credit_tracker\\stopwords_chat')