import collections, re, csv

birgam_model=collections.defaultdict(lambda: collections.defaultdict(lambda: 1))
unigram_model = collections.defaultdict(lambda: 1)
alphabet = 'abcdefghijklmnopqrstuvwxyz'

def words(text): return re.findall('[a-z]+', text.lower()) 

def train(features):
    model = collections.defaultdict(lambda: 1)
    for f in features:
        model[f] += 1
    return model

def trainLM(train_file):
        
    for line in open(train_file, 'r'):
        line = '<S> '+line+' <\S>'
        
        words = line.split()
        for i in range(len(words)):
            if words[i] in ['<S>','<\S>']:
                continue
            unigram_model[words[i]] += 1
            birgam_model[words[i]][words[i-1]] += 1


def edits1(word):
    splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes    = [a + b[1:] for a, b in splits if b]
    transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
    replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b]
    inserts    = [a + c + b     for a, b in splits for c in alphabet]
    return set(deletes + transposes + replaces + inserts)

def known_edits2(word):
    return set(e2 for e1 in edits1(word) for e2 in edits1(e1) if e2 in unigram_model)

def known(words): return set(w for w in words if w in unigram_model)

def correct(word):
    #print known(edits1(word))
    #print known_edits2(word)
    candidates = known([word]) or known(edits1(word)) or known_edits2(word) or [word]
    #print candidates    
    return max(candidates, key=unigram_model.get)
    #return candidates

def correct_sentence(sent):
     
    sent = '<S> '+sent+' <\S>'
    words = sent.split()
    
    for i in range(len(words)):
        unigram_candidates = correct(words[i])
        
        bigram_candidates = collections.defaultdict(lambda: 1)
        for j in unigram_candidates:
            if ((j in birgam_model) and ()):
                print 
            
if __name__ == '__main__':
    trainLM('E:\\tmp\\Chats\\spell_checker_train_data')
    out_file = csv.writer(open('E:\\tmp\\Chats\\spellings.csv', 'wb'))
    out_file.writerow(['chat_id','original','correction','chat text'])
    
    corrections = set([])
    for row in csv.reader(open('E:\\tmp\\Chats\\accepted.csv', 'rb')):
        for word in re.findall('[a-z]+', row[1].lower()):
            if word in corrections:
                continue
            corrected = correct(word)
            if (corrected!=word):
                corrections.add(word)
                out_file.writerow([row[0],word,corrected,row[1]])
                #print row[0],word,corrected
            
    
    #print correct('mke')
    