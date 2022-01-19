'''
Created on Jul 24, 2014

@author: anmol.walia
'''
import re, csv, os, sets, string, sys, collections, enchant, nltk

class ChatNormalizer:
    months_without_word_boundaries=['january','february','march','april','may','june','july','august','september','october','november','december','jan','feb','mar','apr','jun','jul','aug','sep','sept','oct','nov','dec']
    months=[r'\bjanuary\b',r'\bfebruary\b',r'\bmarch\b',r'\bapril\b',r'\bjune\b',r'\bjuly\b',r'\baugust\b',r'\bseptember\b',r'\boctober\b',r'\bnovember\b',r'\bdecember\b',r'\bjan\b',r'\bfeb\b',r'\bmar\b',r'\bjun\b',r'\bjul\b',r'\baug\b',r'\bsep\b',r'\bsept\b',r'\boct\b',r'\bnov\b',r'\bdec\b']
    ambiguous_months=[r'\bapr\b',r'\bmay\b']
    days = [r'\bmonday\b',r'\btuesday\b',r'\bwednesday\b',r'\bthursday\b',r'\bfriday\b',r'\bsaturday\b',r'\bsunday\b',r'\bmon\b',r'\btue\b',r'\bwed\b', ]
    domestic_locations=[]
    international_locations=[]
    
    def compileRegexes(self, word_class_file, substitutions_file):
        ## Dates     
        self.ill_formed_dates = [re.compile(r'('+'|'.join(self.months_without_word_boundaries)+')(\d{1,4}(?:nd|st|rd|th)?)', re.I),
                                 re.compile(r'(\d{1,4}(?:nd|st|rd|th)?)('+'|'.join(self.months_without_word_boundaries)+')',re.I)]
        
        self.dates_regex = [re.compile(r'(\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?)'),
                            ## Problematic dot sign....HACKY regex      
                            re.compile(r'((?:'+'|'.join(self.months+self.ambiguous_months)+')\.? \d{1,4}(?:nd|th|rd|st)?(?:(?:,| of |, | )\d{2,4})?)', re.I),
                            re.compile(r'(\d{1,2}(?:nd|th|rd|st)?(?:,| of |, | )(?:'+'|'.join(self.months+self.ambiguous_months)+')(?:(?:,| of |, | )\d{2,4})?)', re.I),
                            re.compile(r'((?:'+'|'.join(self.months)+')(?:(?:,| of |, | )\d{2,4})?|(?:'+'|'.join(self.ambiguous_months)+')(?:(?:,| of |, | )\d{2,4}))',re.I)]
    
        self.dollar_amount = re.compile(r'(\$\s?\d*\,?\d*\.?\d{1,2}|\d*\,?\d*\.?\d{1,2}\s?\$)')
        self.time = re.compile(r"\d{1,2}\s*(?:(?:am|pm)|(?::\d{1,2})\s*(?:am|pm)?)", re.I)
        self.url = re.compile(r"https?\:\/\/\S*", re.I)
        self.days_regex = re.compile(r'('+'|'.join(self.days)+')',re.I)
    
        ## Substituting multiple punctuations (like ???, !!, $$$) with only one
        self.multiple_puncts=re.compile(r'(\.|\,|\?|\!|\*|\$)\1{1,}')      
        
        self.substitutions={}
        
        self.text_based_WC_substitutions=collections.defaultdict(lambda:[])
        self.text_based_WC_substitutions_compiled_regexes={}
        
        self.readWordClasses(word_class_file)
        self.readSubstitutions(substitutions_file)
        self.substitutions_regex = re.compile(r'\b'+'|'.join(sorted(self.substitutions.keys(), reverse = True)).replace('|', r'\b|\b')+r'\b')
        self.int_loc = re.compile(r'\b'+'|'.join(sorted(self.international_locations, reverse = True)).replace('|', r'\b|\b')+r'\b')
        self.dom_loc = re.compile(r'\b'+'|'.join(sorted(self.domestic_locations, reverse = True)).replace('|', r'\b|\b')+r'\b')
                
    def readWordClasses(self,word_classes_file):
                    
        for line in open(word_classes_file, 'r').readlines():
            line=line.strip()
            
            ## Discard blank lines
            if line=='':continue
            ## Read class names
            elif line.startswith('_class_'):
                current_word_class = line
                #substitutions[current_word_class]=set([])
                continue
            if current_word_class=='_class_location_international':self.international_locations.append(line)
            elif current_word_class=='_class_location_domestic':self.domestic_locations.append(line)
            #self.substitutions[line]=current_word_class
            self.text_based_WC_substitutions[current_word_class].append(line)
        
        for i,j in self.text_based_WC_substitutions.iteritems():
            self.text_based_WC_substitutions_compiled_regexes[i]=re.compile(r'\b(?:'+'|'.join(sorted(j, reverse = True))+r')\'?s?\b',re.I)
        
        #print ( "Read the following word classes:" )
        #print set(self.substitutions.values())

    def readSubstitutions(self, substitutions_file):
        
        for line in open(substitutions_file, 'r').readlines():
            if line.startswith('-') or line.strip()=='':continue
            parts = line.strip().split(',')
            self.substitutions[parts[0].strip()]=parts[1].strip()
    
    def replaceClasses(self, text):
        
        ## Fixing ill-formed dates
        for ill_formed_date_regex in self.ill_formed_dates:
            text = ill_formed_date_regex.sub(r'\1 \2', text)
        
        ## Replacing dates    
        for date_regex in self.dates_regex:
            text = date_regex.sub(' _class_date ', text)
        
        text = self.days_regex.sub(' _class_date ', text)   
        
        ## Replacing money amounts
        text = self.dollar_amount.sub(' _class_number _class_currency ', text)
        
        ##Replacing the remaining numbers - HACKY
        text = re.sub(r'\b\d+\b', ' _class_number ', text)
        return text
                   
    ### Function for normalizing chat text. 
    
    def normalize(self, text):
        
        classes_found={}
        
        ## Replacing emails
        text = re.sub(r"[\w\.-]+@[\w\.-]+", '_class_email ', text)

        ## Replacing times
        text = self.time.sub('_class_time ', text)

        
        ## Replacing URLs
        text = self.url.sub('_class_url ', text)
        
        ## Removing extraneous symbols
        text = re.sub(r"\?|\!|\(|\)|\[|\]|\"|~|\+|,|{|}|:|;|\*|\|", ' ', text)
        
        ## removing single quotes if they aren't used in prepositions
        text = re.sub(r"\'[^a-zA-Z]|[^a-zA-Z]\'|'$|^'", ' ', text)
                
        text = self.replaceClasses(text)
        
        ## replacing multiple punctuations
        text = self.multiple_puncts.sub(r'\1', text)
                
        ## Removing punctuations before word class replacements --- HACK
        text = re.sub(r"\.|<s>|=|/|\-|>|<|`|\\|\^| \' " , ' ', text.lower())
        #text = re.sub(r" \' |\' | \'" , ' ', text)
        
        for i in self.dom_loc.findall(text):
            #print self.domestic_locations
            #print text+" : "
            #print self.dom_loc.findall(text)            
            classes_found[i]=self.substitutions[i] 
        for i in self.int_loc.findall(text):
            #print text
            #print self.int_loc.findall(text)
            classes_found[i]=self.substitutions[i]        
        
        ## Replacing word classes_found
        text = self.substitutions_regex.sub(lambda m: self.substitutions[m.group(0)], text)
    
        for WC,WC_regex in self.text_based_WC_substitutions_compiled_regexes.iteritems():
            text = WC_regex.sub(WC, text)
    
        ## HACK - replacing dollars and numbers
        text = re.sub(r'\$', ' _class_currency ', text)
        text = re.sub(r'\#',' number ', text)
        text = re.sub(r'\bno\.\b',' number ', text)
        text = re.sub(r'%', ' percent ', text)
        text = re.sub(r'&', ' and ', text)
        text = re.sub(r'@', ' at ', text)
                        
        ## remove extra spaces
        text = re.sub(r'\s{2,}', ' ', text)
                      
        return text, classes_found

class SpellChecker():
    #def __init__(self):        
    #    self.bigram_model = collections.defaultdict(lambda: collections.defaultdict(lambda: 0))
    #    self.unigram_model = collections.defaultdict(lambda: 0)
    #    self.dictionary = enchant.Dict('en_US')
    #    self.corrections={}

    def __init__(self, personal_word_list):        
        self.bigram_model = collections.defaultdict(lambda: collections.defaultdict(lambda: 0))
        self.unigram_model = collections.defaultdict(lambda: 0)
        self.dictionary = enchant.DictWithPWL('en_US', personal_word_list)
        self.corrections={}

    def loadLM(self, LM_file):
        lm_file = open(LM_file, 'r')
        for line in lm_file.readlines():
            parts = line.split()
            if len(parts)==3:
                self.bigram_model[parts[0]][parts[1]]=int(parts[2])
            elif len(parts)==2:
                self.unigram_model[parts[0]] = int(parts[1])
            else: continue
        lm_file.close()
    
    def saveLM(self, LM_file):
        lm_file = open(LM_file,'w')
        for context, words in self.bigram_model.iteritems():
            for word, count in words.iteritems():
                lm_file.write(context+'\t'+word+'\t'+str(count)+'\n')
            
        for word,count in self.unigram_model.iteritems():
            lm_file.write(word+'\t'+str(count)+'\n')
        lm_file.close()
                
    def trainLM(self, train_file):

        train_data = open(train_file, 'r').readlines()
        for line in train_data:
            #line = '<S> '+line+' <\S>'
            words = line.split()
            for i in range(len(words)):                
                if i==0:
                    self.unigram_model[words[i]] += 1
                    self.bigram_model['<S>'][words[i]] += 1
                elif i==(len(words)-1):
                    self.unigram_model[words[i]] += 1
                    if i-1>=0:
                        self.bigram_model[words[i-1]][words[i]] += 1
                    self.bigram_model[words[i]]['<\S>'] += 1
                else:
                    self.unigram_model[words[i]] += 1
                    self.bigram_model[words[i-1]][words[i]] += 1

    def getUnigramCounts(self, word):
        if self.unigram_model.has_key(word):
            return self.unigram_model[word]
        return 0

    def getBigramCounts(self, context, word):
        
        if self.unigram_model.has_key(context) and self.bigram_model[context].has_key(word):
            return self.bigram_model[context][word]        
        return 0
    
    def getCount(self, context, word):
        
        bigram_count = self.getBigramCounts(context, word)
        if bigram_count==0: return self.getUnigramCounts(word)*0.1
        else: return bigram_count
           
    def addSpellingExceptions(self, txt_file):
        for words in open(txt_file, 'r').readlines():
            self.corrections[words.strip()]=words.strip()

    def correctSentence(self, text):

        words = text.split()
        
        spell_corrected=[]
        for i in range(len(words)):
            
            if words[i].startswith('_class'):
                spell_corrected.append(words[i])
                continue
            
            ## Check in already spell_corrected words 
            if self.corrections.has_key(words[i]):
                spell_corrected.append(self.corrections[words[i]])
                continue
            #print self.dictionary
            ## Check whether word exists in enchant dictionary 
            if self.dictionary.check(words[i]) or self.dictionary.check(words[i][0].upper()+words[i][1:]):
                spell_corrected.append(words[i])
                self.corrections[words[i]]=words[i]
                continue
            
            ## Get suggestions from enchant
            suggestions = self.dictionary.suggest(words[i])
            
            suggestions = [l.lower() for l in suggestions]
            
            ## Multiple word suggestions not handled by SLM
            if len(suggestions)>0 and ' ' in suggestions[0]:                
                self.corrections[words[i]]=suggestions[0]
                spell_corrected.append(suggestions[0])
                continue
            
            ## Select the most probable suggestion from the top 5
            suggestion_length = 8 if len(suggestions)>8 else len(suggestions)
            best_correction=words[i]
            best_freq=0         
            for j in range(suggestion_length):
                                
                #if len(suggestions)==j:break
                if i==0:context='<S>'
                else:context=words[i-1]
                word_count = self.getCount(context, suggestions[j])                
                if word_count>best_freq:
                    best_freq=word_count
                    best_correction = suggestions[j]
                        
            self.corrections[words[i]]=best_correction
            spell_corrected.append(best_correction)
                
        return ' '.join(spell_corrected)

def detectNameAndIssueLine(line):
    #d = enchant.Dict('en_US')
    corrector = SpellChecker()
    corrector.loadLM('E:\\tmp\\Chats\\SLM_Stats')
    names=set([i.strip().lower() for i in open('E:\\tmp\\Chats\\first_names', 'r')])
    for word in line.lower().split():
        suggestions = corrector.dictionary.suggest(word)
        
        print word, suggestions[:3]
        if (not corrector.getUnigramCounts(word)>10) and (not any([i for i in suggestions[:3] if corrector.getUnigramCounts(i)>10])):
            print word, corrector.dictionary.check(word[0].upper()+word[1:])
        
        if word in names:
            print word+' : common name'    
        
            
def removeNonAscii(s): return "".join(i for i in s if ord(i)<128)
   
if __name__ == '__main__':
    
    #detectNameAndIssueLine('this is anmol')
    #sys.exit()
    
    #working_dir = 'E:\\tmp\\Chats\\'
    working_dir = 'E:\\Data\\CapOne\\Credit_tracker\\'
    output_dir = os.path.join(working_dir,'20150206c_withResponses\\Credit_tracker_synth_Data_with_WC_plurals')
    #output_dir = os.path.join('E:\\Data\\IR\\')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    normalizer= ChatNormalizer()
    normalizer.compileRegexes(os.path.join( working_dir, 'Word_Classes_without_Plurals'),os.path.join( working_dir, 'substitutions'))
    #normalizer.compileRegexes(os.path.join( working_dir, 'Word_Classes_dummy'),os.path.join( working_dir, 'substitutions'))
    
    #reader = csv.reader(open( os.path.join( working_dir, 'accepted.csv'), 'rb'))
    reader = csv.reader(open( os.path.join( working_dir, 'formatted_synthData_20150206c_withResponses_WC_withPlurals.csv'), 'rb'))
    #reader = csv.reader(open( os.path.join( output_dir, 'formatted_synth.csv'), 'rb'))
    
    SLM_data_writer = open(os.path.join( output_dir, 'SLM_data'), 'w')
        
    orig_intents={}
    nmlzed_utts = {}
    originals = {}
    for row in reader:
        nmlzed,classes_found = normalizer.normalize(removeNonAscii(row[1]).encode('utf-8',errors='ignore'))
        SLM_data_writer.write(nmlzed+'\n')
        nmlzed_utts[row[0]]=nmlzed
        originals[row[0]] = row[1]
        orig_intents[row[0]]=row[2]
    SLM_data_writer.close()
   
    corrector = SpellChecker(os.path.join( working_dir, 'PWL'))
    corrector.trainLM(os.path.join( output_dir, 'SLM_data'))
    ##corrector.addSpellingExceptions(os.path.join( working_dir, 'PWL'))
    
    corrector.saveLM(os.path.join( output_dir, 'SLM_Stats'))

    spell_checked= csv.writer(open(os.path.join( output_dir, 'Normalized_final.csv'), 'wb'))
    spell_checked.writerow(['Id','Raw','Normalized'])
    spell_checked_for_classification = open(os.path.join( output_dir, 'dummy_chat_data'), 'w')

    for id, chat in nmlzed_utts.iteritems():
        corrected_utt = normalizer.replaceClasses(corrector.correctSentence(chat))              
        spell_checked.writerow([id, originals[id], corrected_utt])
        #spell_checked_for_classification.write(id+'\t'+corrected_utt+'\tNONE_RU\tNONE_RU\n')
        spell_checked_for_classification.write(id+'\t'+corrected_utt+'\t'+orig_intents[id]+'\t'+orig_intents[id]+'_1\n')
    spell_checked_for_classification.close()
            
    corrections_file= csv.writer(open(os.path.join( output_dir, 'SpellingCorrections.csv'), 'wb'))
    for word,correction in corrector.corrections.iteritems():
        if word!=correction:
            corrections_file.writerow([word, correction]+corrector.dictionary.suggest(word))
        
        