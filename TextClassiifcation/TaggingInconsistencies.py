# -*- coding: utf-8 -*-
import re, collections, sys, ConfigParser,codecs,os,logging
#from logging import Logger

class utt:
    def __init__(self, id, orig, ru_intent,granular_intent):
        self.id=id
        self.orig_transcript=orig
        self.ru_intent=ru_intent
        self.granular_intent=granular_intent


class trans_csv_input:
    def __init__(self,filename,row_id,trans,ru,granular,encoding='utf-8'):
        '''
        This class is for maintaining the input columns header names
        '''
        self.filename=filename
        #this is the row id header
        self.row_id=row_id
        #this is the transcription column header
        self.trans=trans
        #this is the ru col header
        self.ru=ru
        #this is the granular column header
        self.granular=granular
        self.encoding=encoding
        self.sep='\t'

        self.f = codecs.open(filename, 'r',encoding=custom_encoding)
        header = self.f.readline()
        cols = header.split(self.sep)
        INIT_VAL=-1
        r_i,t_i,ru_i,g_i = INIT_VAL,INIT_VAL,INIT_VAL,INIT_VAL
        for i,col in enumerate(cols):
            col = col.strip()
            r_i = i if row_id==col else r_i
            t_i = i if trans==col else t_i
            ru_i = i if ru==col else ru_i
            g_i = i if granular==col else g_i
        if(r_i==INIT_VAL or t_i==INIT_VAL or ru_i== INIT_VAL or g_i== INIT_VAL):
            logging.error("Expected columns not present in the input file")
            sys.exit()
        self.r_i=r_i
        self.t_i=t_i
        self.ru_i=ru_i
        self.g_i=g_i

    def __iter__(self):
        return self


    def next(self):
        #next method is supposed to throw StopIteration() exception at the end of file.
        # The next() method of file object does this . Hence calling it instead of the readline() method
        header = self.f.next()
        header = header.strip()
        #if (header == ""):
        #   raise StopIteration()
        cols = header.split(self.sep)
        o = [cols[self.r_i],cols[self.t_i],cols[self.ru_i],cols[self.g_i]]
        return o


def get_input_data(config):
    in_file = config.get('params','inp_data')
    row_id_column = config.get('params','row_id_column')
    transcription_column = config.get('params','transcription_column')
    intent_column = config.get('params','intent_column')
    granular_intent_column = config.get('params','granular_intent_column')
    custom_encoding=config.get('params','encoding')

    in_file = trans_csv_input(in_file,row_id_column,transcription_column,intent_column,granular_intent_column,encoding=custom_encoding)
    return in_file


# def read_filler(inp_file):
#
#     fil=sorted(set([i.strip() for i in open(inp_file)]),key=lambda z:(len(z.split()),z), reverse=True)
#     fil_regex = re.compile(r'\b(?:'+'|'.join(fil)+r")'?s?\b")

def cannonicalize_utt(in_utt):
    '''
        Function to normalize input text by performing the following:
        1. Remove duplicate words, i.e. multiple occurences of the same word next to each other
        2. Remove filler words and phrases
        3. Stem - using NLTK wordnet
        4. Remove filler words and phrases again
    '''
    if in_utt.strip()=="":return ""

    ## Replace word classes
    if config.get('params','word_class_replacement').strip().lower()=='true':
        in_utt = word_class_regex.sub(lambda m: word_classes[m.group(0)] if word_classes.has_key(m.group(0)) else word_classes[m.group(0)[:-1].replace("'", "")], in_utt)

    ## Remove duplicate words
    in_utt = dup_wrds.sub(r"\1", in_utt)
    in_utt = ' '.join(in_utt.split())

    ## Remove filler
    if(is_stopword_removal()):
        in_utt = fil_regex.sub('', in_utt)
    utt_parts=in_utt.split()

    # Stemming
    for i in range(len(utt_parts)):
        if lemmatized_words.has_key(utt_parts[i]):
            utt_parts[i]=lemmatized_words[utt_parts[i]]
            continue

        word = utt_parts[i]
        pos_tagged = nltk.pos_tag([word])
        lemma = lmtzr.lemmatize(utt_parts[i], get_wordnet_pos(pos_tagged[0][1]))
        lemmatized_words[utt_parts[i]] = lemma
        utt_parts[i]=lemma

    # stopword removal
    in_utt = ' '.join(utt_parts)
    if(is_stopword_removal()):
        in_utt = fil_regex.sub('', in_utt)

    return ' '.join(in_utt.split())

def find_inconsistencies(config):
    in_file = config.get('params','inp_data'),
    out_file=config.get('params','out_file')
    custom_encoding=config.get('params','encoding')

    ## Dataset, with canonical utt as the key and list of utterances as the first value and intent-distribution as the other value
    utts = collections.defaultdict(lambda:[[],collections.defaultdict(lambda:0)])

    ## Read input utterances and cannonicalize them
    fin = get_input_data(config)
    for parts in fin:
        try:
            id = parts[0]
            transcription = parts[1]
            ru_tag=parts[2]
            granular_tag=parts[3]

            can_form = cannonicalize_utt(transcription)
            #utts[can_form][0].append(utt(id,transcription,ru_tag))
            utts[can_form][0].append(utt(id,transcription,ru_intent=ru_tag,granular_intent=granular_tag))
            #utts[can_form][1][ru_tag]+=1
            utts[can_form][1][granular_tag]+=1
        except Exception as e:
            print e

    wr = codecs.open(out_file, 'wb',encoding=custom_encoding)
    wr.write('Id,Input utterance,Canonical-form,Original RU intent,Original Granular Intent,Suggested_granular_Intent,is_different(if original and suggested intent differs),group_id(all utterances with same can form have same group id),Other_intents_with_same_form\n')
    group_id=1
    for can_form,j in utts.iteritems():
        try:
            #if there are multiple intents in this list it means tagging is inconsistent, continuing further only if tagging inconsistent
            if len(j[1])<2:continue

            suggested_intent=""

            ## Guessing intent based on the intent-distribution
            l_count=-1
            other_intents=set()
            for a,b in j[1].iteritems():
                if float(b)/sum(j[1].values())>(float(config.get('params','intent_majority_threshold'))/100):
                    if (b>l_count):
                        #finding the intent with maximum count for this particular cannonical form, if the threshold values are low(50 or less),then there could be multiple intents with a given cannonical form, so taking the best out of it
                        l_count=b
                        suggested_intent=a
                other_intents.add(a)

            for x in j[0]:
                    wr.write(x.id+","+x.orig_transcript+","+can_form+","+x.ru_intent+','+x.granular_intent +','+ suggested_intent+','+str(x.granular_intent!=suggested_intent)+','+str(group_id)+','+' \t'.join(other_intents)+"\n")
        except Exception as e :
            print e
        group_id+=1
    wr.close()

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

def readWordClasses(word_classes_file,encoding='utf-8'):

    for line in codecs.open(word_classes_file, 'r',encoding=encoding):
        line=line.strip()
        ## Discard blank lines
        if line=="":continue

        ## Read class names
        elif line.startswith('_class_'):
            current_word_class = line
            continue

        if current_word_class!=None:word_classes[line]=current_word_class
        else: raise Exception('Empty word-class member found: '+line)

def is_stopword_removal():
    return config.get('params','stopword_removal').strip().lower()=='true'

if __name__ == '__main__':
    try:
        import nltk
        from nltk.corpus import wordnet
    except ImportError:
        print "Please install NLTK to use this script!"
        sys.exit()
    #setting a default value for config location (same as the location of the terminal from which it is being run)
    config_file = 'TaggingInconsistencies-Config.cfg'
    if len(sys.argv)!=2:
        print 'Usage: python TaggingInconsistencies.py <config_file>'
        print 'Using default location for config file '
    else:
        config_file = sys.argv[1]
    print 'config file location is - ' + os.path.abspath(config_file)
    #setting the logger level
    logging.basicConfig(stream=sys.stderr, level = logging.ERROR)

    config = ConfigParser.ConfigParser()
    config.readfp(open(config_file))
    custom_encoding=config.get('params','encoding')

    ## Read filler phrases and stopwords and generating regexes.
    if(is_stopword_removal()):
        fil=sorted(set([i.strip() for i in codecs.open(config.get('params','stop_words_or_phrases_file'),'r',encoding=custom_encoding) if i.strip()!=""]),key=lambda z:(len(z.split()),z), reverse=True)
        fil_regex = re.compile(r'\b(?:'+'|'.join(fil)+r")'?s?\b")

    ## Read stem-exception list
    stem_excepts = list(set([i.strip() for i in codecs.open(config.get('params','stem_exception_file'),encoding=custom_encoding) if i.strip()!=""]))
    lemmatized_words = dict(zip(stem_excepts,stem_excepts))

    lmtzr = nltk.WordNetLemmatizer()

    ## regex to remove duplicate words - that appear twice or more times, contiguously
    dup_wrds = re.compile(r"\b([a-z]+)(\s+\1\b(?!'))+", re.I)

    if config.get('params','word_class_replacement').strip().lower()=='true':
        word_classes={}
        readWordClasses(config.get('params','word_class_file'),encoding=custom_encoding)
        raw_string=r'\b(?:'+'|'.join(sorted(word_classes.keys(), reverse = True))+r")'?s?\b"
        word_class_regex = re.compile(raw_string)

    find_inconsistencies(config)
    out_file=config.get('params','out_file')

    print "Output file is " + out_file
    print "filter by column 'is_different..' = TRUE, to find the lines which have a different suggested intent"

