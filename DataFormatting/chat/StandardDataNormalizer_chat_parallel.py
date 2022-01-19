# -*- coding: utf-8 -*-
# Note. Please check if test cases are working after modifying any of the regexes or order of operation
import xlrd, re, csv, sys, os, logging, ConfigParser, codecs, time, collections
# import nltk
from nltk import WordNetLemmatizer,pos_tag
from nltk import word_tokenize
from nltk.corpus import wordnet
import inspect
from logging import Logger
from web2nl_helper import get_normalized_output
from multiprocessing.dummy import Pool as ThreadPool
# from multiprocessing import Pool as ThreadPool
import threading
try:
    import cPickle as pickle
except:
    import pickle

num_threads=1

proxy_url=''

word_class_replacement=None
# word_classes={}
# word_classes_new={}
word_expansions={}
corpus=list()
custom_encoding=""
is_perform_chat_normalization=False

def generate_arpax(lang='en-US'):
        word_classes = word_class_replacement.word_classes
        arpaxFile = codecs.open( os.path.join(config.get('params', 'output_dir'), 'all.arpax'), 'w',encoding=custom_encoding)
        substitutions_file = codecs.open( os.path.join(config.get('params', 'output_dir'), 'substitutions_arpax'), 'w',encoding=custom_encoding)

        arpaxFile.write("<language-model xml:lang=\""+lang+"\" root=\"TopLevelRule\" tag-format=\"semantics/1.0\">\n\n")
        arpaxFile.write("<ngram-rule scope=\"public\" id=\"BasicNGram\" src=\"inter.arpa\">\n")

        for word_class in word_classes.keys():
            arpaxFile.write("\t<ngram-token id=\""+ word_class +"\" type=\"ruleref\" value=\"#"+ word_class + "_1\"/>\n")
            substitutions_file.write(word_class+" <#" + word_class+">\n")

        arpaxFile.write("</ngram-rule>\n\n")

        arpaxFile.write("<rule id=\"TopLevelRule\" scope=\"public\">\n")
        arpaxFile.write("    <tag> out={}; index=0; out.Fragments=FragsGlobal = new Array(); out.classsubstitution = gSubstitutions = [];</tag>\n")
        arpaxFile.write("    <ruleref uri=\"#BasicNGram\"/>\n")
        arpaxFile.write("</rule>\n\n")
        for word_class in word_classes.keys():
            arpaxFile.write("<rule id=\""+ word_class + "_1\" scope=\"public\">\n")
            arpaxFile.write("\t<ruleref uri=\"#"+ word_class +"_2\"/>\n")
            arpaxFile.write("\t<tag> gSubstitutions.push({interpretation: rules.latest(),tokens: meta.latest().text,klass: \""+word_class+"\" }); </tag>\n")
            arpaxFile.write("</rule>\n\n")

        ## grxmls for individual classes
        for word_class in word_classes.keys():
            arpaxFile.write("<rule id=\""+ word_class + "_2\" scope=\"public\">\n")
            arpaxFile.write("\t<one-of>\n")

            for element in word_classes.get(word_class):
                arpaxFile.write("\t    <item>\n")
                arpaxFile.write("\t    "+element+"\n")
                arpaxFile.write("\t    </item>\n")

            arpaxFile.write("\t</one-of>\n")
            arpaxFile.write("</rule>\n\n")
        arpaxFile.write("</language-model>")


def generateGRXMLs(lang='en-US'):

    word_classes = word_class_replacement.word_classes
    substitutions_arpa_file = codecs.open( os.path.join(config.get('params', 'output_dir'), 'substitutions_arpa'), 'w',encoding=custom_encoding)
    ## grxmls for individual classes
    for word_class in word_classes.keys():
        substitutions_arpa_file.write(word_class+" <URL:"+config.get('params', 'grxml_dir_URL') +"/word_classes_root.grxml#" + word_class+">\n")
        generateClassGrammar(word_class,lang=lang)
    ## root GRXML
    generateRootGRXML(lang=lang)

def generateRootGRXML(lang='en-US'):
    word_classes = word_class_replacement.word_classes
    if not os.path.isdir(os.path.join(config.get('params', 'output_dir'),'grxmls')):
        os.makedirs(os.path.join(config.get('params', 'output_dir'),'grxmls'))

    grxml_file = open( os.path.join(config.get('params', 'output_dir'),'grxmls' ,'word_classes_root.grxml'), 'w')

    ## Write grxml meta information
    grxml_file.write( "<?xml version= \"1.0\"?>\n" )
    grxml_file.write( "<grammar tag-format=\"semantics/1.0\" version=\"1.0\" xml:lang=\""+lang+"\" xmlns=\"http://www.w3.org/2001/06/grammar\">\n" )

    for word_class in word_classes.keys():
        grxml_file.write("\t<rule id=\""+word_class+"\" scope=\"public\">\n")
        grxml_file.write("\t\t<item>\n")
        grxml_file.write("\t\t\t<ruleref uri=\""+config.get('params', 'grxml_dir_URL')+"/"+word_class.replace("_class_","")+".grxml\"/>\n")
        grxml_file.write("\t\t</item>\n")
        grxml_file.write("\t\t<tag>gSubstitutions.push({interpretation: rules.latest(),tokens: meta.latest().text,klass: \""+word_class+"\" });\n")
        grxml_file.write("\t\t</tag>\n")
        grxml_file.write("\t</rule>\n")

    grxml_file.write( "</grammar>")

    grxml_file.close()

'''
    Generate grxml files for word classes
'''
def generateClassGrammar(class_name,lang='en-US'):
    word_classes = word_class_replacement.word_classes
    ## Check whether class contains any class elements
    if len(word_classes.get(class_name))==0:
        raise Exception("Class "+class_name+" doesn't contain any class elements!!")
    if not os.path.isdir(os.path.join(config.get('params', 'output_dir'),'grxmls')):
        os.makedirs(os.path.join(config.get('params', 'output_dir'),'grxmls'))

    grxml_file = codecs.open( os.path.join(config.get('params', 'output_dir'),'grxmls', class_name.replace("_class_", "") + '.grxml'),'wb', encoding=custom_encoding)

    ## Write grxml meta information
    grxml_file.write( "<?xml version= \"1.0\"?>\n" )
    grxml_file.write( "<grammar mode=\"voice\" root=\""+class_name.replace("_class_", "")+"\" tag-format=\"semantics/1.0\" version=\"1.0\" xml:lang=\""+lang+"\" xmlns=\"http://www.w3.org/2001/06/grammar\">\n" )
    grxml_file.write( "<!-- Machine generated - DO NOT EDIT -->\n" )
    grxml_file.write( "<!-- "+class_name+" -->\n" )
    grxml_file.write( "\t<rule id=\""+class_name.replace("_class_", "")+"\" scope=\"public\">\n" )
    grxml_file.write( "\t  <item>\n" )
    grxml_file.write( "\t    <one-of>\n" )

    ## Write class elements
    for class_element in word_classes.get(class_name):
        grxml_file.write( "\t      <item>\n" )
        grxml_file.write( "\t        "+class_element+"\n" )
        grxml_file.write( "\t      </item>\n" )

    grxml_file.write( "\t    </one-of>\n" )
    grxml_file.write( "\t  </item>\n" )
    grxml_file.write( "\t</rule>\n" )
    grxml_file.write( "</grammar>" )
    grxml_file.close()

'''
    Function for replacing word-classes in a synthetic data file.
    Each line in the input CSV file should contain synthetic utterances.
'''

def lookup(match):
    return substitutions[match.group(0)]

def createCorpusOfWords(transcription_values):
    count = 0
    for transcription in transcription_values:
        count+=1
        # print (type(transcription))
        if type(transcription)==int or type(transcription)==float:
            continue
        try:
            transcription = transcription.lower()
            words= transcription.split()
            for word in words:
                if "((" not in word and "))" not in word:
                    corpus.append(word) #No inaudible fragments in that word.
        except Exception as e:
            print u'exception occured' + unicode(e)
            # print str(e) + str(transcription) + "count is "+str(count)
    print "Corpus contains ", len(corpus), "number of words"
    print "no of unique words in corpus - {}".format(len(set(corpus)))

def cleanTranscription(transcription):

    dirt_flag= True

    if chat_normalizer.is_perform_case_normalization_first():
        ## converting to lower case
        ## Case required for spell correction
        transcription= transcription.lower()
        # transcription = unicode(str(transcription))
        logging.debug(u" Step 1  : " + transcription)

    ## Check whether the transcription is clean
    if speech_normalizer.concatenated.search(transcription)==None:
        return transcription, dirt_flag
    logging.debug(u"Step 2  : " + transcription)

    ## Handle Cutting Out
    transcription = speech_normalizer.cutting_out.sub(ur'\1\2\3',transcription)
    logging.debug(u"Step 3 : " + transcription)

    ## Clean acoustic quality fragments
    transcription = speech_normalizer.acoustic_quality_indication_1.sub(ur'\1\3', transcription)
    logging.debug(u"Step 4_1 : " + transcription)
    transcription = speech_normalizer.acoustic_quality_indication_2.sub(ur'\2\3', transcription)
    logging.debug(u"Step 4_2 : " + transcription)
    transcription = speech_normalizer.acoustic_quality_indication_3.sub(ur'\1\2\4', transcription)
    #transcription = re.sub(ur'\]', '', transcription, )
    logging.debug(u"Step 4_3 : " + transcription)

    transcription = speech_normalizer.square_brackets_second_term.sub(ur'',transcription)
    logging.debug(u"Step 4_4 : " + transcription)

    #transcription = square_brackets_first_term.sub(ur'\2',transcription)
    #logging.debug(u"Step 4_4 : " + transcription

    #Replace imbalanced parans.
    transcription = re.sub(ur'(\[|\])*','',transcription);
    logging.debug(u"Step 4_4 : " + transcription)

    #Remove multiple white spaces caused in the previous steps.
    transcription= chat_normalizer.remove_additional_space(transcription)
    logging.debug(u"Step 4_5 : " + transcription)

    ## Clean word fragments
    for regexp in speech_normalizer.frag_bracketted_wrds:
        ## Redundant step...find a better way
        if regexp.search(transcription)!=None:
            dirt_flag = False
        transcription = regexp.sub('', transcription)
        logging.debug(u'Step 5 sub steps '+ transcription)
    logging.debug(u"Step 5 : " + transcription)

    ## Inefficient code for concatenating fragments containing hyphens (-)....try using regex '((\s+|$)(-\w+)|(\w*\-))(\s+|$)'
    if '-' in transcription:
        wrds = transcription.split()
        transcription = ' '.join([x for x in wrds if not (x.startswith('-') or x.endswith('-'))])
    logging.debug(u"Step 6 : " + transcription)

    ## Remove other transcription markers like (,~ etc.
    transcription = speech_normalizer.special_characters.sub(lookup, transcription)
    logging.debug(u"Step 7 : " + transcription)

    ##Standard legitimate word check for fragments put together. If the fragment is in single parens, just concatenate without any corpus dip.
    words = transcription.split()
    new_transcription = list()
    for iter in range(0,len(words)):
        word = words[iter]
        legit_words = list()
        if len((word).split(ur'(('))>1:
            fragments = word.split(ur'-')
            legit_fragment_count=0
            fragments_concatenated=u""
            for fragment in fragments:
                fragment= fragment.replace(ur'(',u"")
                fragment = fragment.replace(ur')',u"")
                fragments_concatenated+=fragment
            if fragments_concatenated in corpus:
                new_transcription.append(fragments_concatenated)
        else:
            new_transcription.append(word)

    transcription = u" ".join(x for x in new_transcription)
    logging.debug(u"Step 7_1 : " + transcription)

    #Below line commented by Sruti on 24 Dec, 2015. Adding a new/completely different regex instead.
    #transcription = truncated_Inaudible.sub('',transcription)
    #transcription = truncated_Inaudible_WithoutLegit_Word_Check.sub('',transcription)
    #logging.debug(u"Step 7_1 : " + transcription)

    ## Remove other transcription markers like (,~ etc.
    transcription = speech_normalizer.empty_parans_substitutions.sub('', transcription)
    logging.debug(u"Step 7_3 : " + transcription)

    transcription = speech_normalizer.truncated_parans_substitutions.sub(ur'\2\4',transcription)
    logging.debug(u"Step 7_2 : " + transcription)

    transcription = speech_normalizer.others_substitutions.sub(' ', transcription)
    logging.debug(u"Step 7_4 : " + transcription)
    ## Remove extra spaces
    transcription = chat_normalizer.remove_additional_space(transcription)
    logging.debug(u"Step 8 : " + transcription)

    return transcription, False


def normalizeDataset():
    custom_encoding=config.get('params','encoding')
    wb = xlrd.open_workbook( config.get('params', 'DataMaster') ,encoding_override=custom_encoding)
    input_file = config.get('params','DataMaster')
    sh = wb.sheet_by_name(config.get('params', 'DataSheetName'))
    intent = config.get('params','intent_column_name')
    granular_intent = intent
    if config.has_option('params', 'granular_intent_column_name'):
        granular_intent = config.get('params', 'granular_intent_column_name')
    expected_cols = set(['filename','transcription',intent])
    if config.get('params', 'contains_utt_repititions_as_counts').lower()=="true":
        expected_cols.add('Count')

    transcriptions_output_file = os.path.join(config.get('params','output_dir'), 'Transcriptions_Normalized')
    ## Opening the output file for writing
    writer = codecs.open( transcriptions_output_file, 'wb', encoding=custom_encoding)
    first_response_file = codecs.open( os.path.join(config.get('params', 'output_dir'), 'FirstResponses.csv'), 'wb', encoding=custom_encoding)
    first_response_file.write("Filename" + "\t" + "Utterance" + "\t" + str(intent) + "\t" + "Acoustic Quality" + "\t" + "Original Utterance" + "\n")
    if config.get('params', 'replace_word_classes_in_data').lower()=="true":
        filename=os.path.join(config.get('params', 'output_dir'), 'FirstResponses_WCNormalized')
    else:
        filename=os.path.join(config.get('params', 'output_dir'), 'FirstResponses')

    WC_normalized_first_responses_file = codecs.open( filename, 'wb', encoding=custom_encoding)
    if config.get('params', 'contains_utt_repititions_as_counts').lower()=="true":
        WC_normalized_first_responses_file_with_dup = codecs.open( filename+'_withDups', 'wb', encoding=custom_encoding)

    if config.get('params', 'second_responses_exist').lower()=="true":
        ## Files for Second Responses
        second_response_file = codecs.open( os.path.join(config.get('params', 'output_dir'), 'SecondResponses.csv'), 'wb', encoding=custom_encoding)
        second_response_file.write("Filename" + "\t" + "Utterance" + "\t" + str(intent) + "\t" + "Acoustic Quality" + "\t" + "Original Utterance")
        if config.get('params', 'replace_word_classes_in_data').lower()=="true":
            filename=os.path.join(config.get('params', 'output_dir'), 'Secondresponses_WCNormalized')
        else:
            filename=os.path.join(config.get('params', 'output_dir'), 'Secondresponses')
        WC_normalized_second_responses_file = codecs.open( filename, 'wb', encoding=custom_encoding)

    word_frequency_file = codecs.open( os.path.join(config.get('params', 'output_dir'), 'WordFrequency.csv'), 'wb', encoding=custom_encoding)
    word_frequency_file.write("Word" + "\t" + "Frequency" + "\n")

    bad_quality_utts = codecs.open( os.path.join(config.get('params', 'output_dir'), 'Fragments.csv'), 'wb', encoding=custom_encoding)
    bad_quality_utts.write("Filename" + "\t" + "Raw Utterance" + "\t" + "Normalized Utterance" +"\t"+ str(intent))
    error_utts = codecs.open(os.path.join(config.get('params','output_dir'), 'Rejected_Utts.csv'), 'wb', encoding=custom_encoding)
    error_utts.write('Filename' + '\n')
    col_indices={}
    # word_frequency={}
    word_frequency_counter=collections.Counter()
    filename_unique_set = set()
    rejected = 0
    row_ctr=0
    columns={}
    actual_cols=[]
    ## Read input excel sheet
    for rownum in range(sh.nrows):
        ac_quality = 'Good'
        ## Storing the column names
        if row_ctr==0:
            col_ctr=0
            for i in sh.row_values(rownum):
                col_indices[i]=col_ctr
                col_ctr += 1
            row_ctr+=1
            for i in set(col_indices.keys()):
                actual_cols.append(str(i))
            if not expected_cols.issubset(set(actual_cols)):
                print 'Columns present: ',actual_cols
                print 'Columns expected: ', expected_cols
                raise Exception('Expected columns not in input sheet')
        else:
            break


    logging.debug('done with parsing header of data ')
    ##Create Corpus on the transcription column.
    for colunum in range(sh.ncols):
        if sh.cell_value(rowx=0,colx=colunum)=='transcription':
            transcriptionColNum = colunum
    createCorpusOfWords(sh.col_values(transcriptionColNum))
    logging.debug('done with creating corpus of words')

    row_ctr=0
    ## look through the sheet
    # for rownum in range(sh.nrows):
    #adding header
    ## read the header file
    row=sh.row_values(0)
    ac_quality = 'Good'

    ## read the header file
    if row_ctr==0:
        column_ctr=0
        for column in row:
            columns[column]=column_ctr
            column_ctr+=1
        row_ctr+=1

        if not (columns.has_key('filename') and columns.has_key('transcription')):
            raise Exception(input_file+' does not contain columns filename and transcription')
        writer.write(row[col_indices['filename']]+'\t'+row[col_indices['transcription']]+'\t'+row[col_indices[str(intent)]]+'\n')
    def process_individual_lines(rownum):

        row=sh.row_values(rownum)
        ac_quality = 'Good'

        ## read the header file
        # if row_ctr==0:
            # column_ctr=0
            # for column in row:
                # columns[column]=column_ctr
                # column_ctr+=1
            # row_ctr+=1

            # if not (columns.has_key('filename') and columns.has_key('transcription')):
                # raise Exception(input_file+' does not contain columns filename and transcription')
            # writer.write(row[col_indices['filename']]+'\t'+row[col_indices['transcription']]+'\t'+row[col_indices[str(intent)]]+'\n')
            # #writer.write(str(['filename', 'transcription', intent, 'Normalized utterance', 'Fragments removed?'])+ '\n')
            # #writer.write(str('filename' + '\t'+ 'transcription' + '\t' + intent + '\t' + 'Normalized utterance' + '\t' +'Fragments removed?'+ '\n'))
            # continue
        try:
            #row[columns['transcription']] = row[columns['transcription']].decode(custom_encoding).encode(custom_encoding)
            ## Clean transcription
            logging.debug(" starting line no " + str(rownum) + "********************************************************************************")
            # logging.debug(u"Step 0 : {}" .format(unicode(str(row[columns['transcription']])) ))#.replace('|speech-in-noise','').strip()
            # logging.debug(u"Step 0 : {}" .format(unicode(row[columns['transcription']]) ))#.replace('|speech-in-noise','').strip()
            # transcription = unicode(str(row[columns['transcription']])).replace('|speech-in-noise','').strip()
            transcription = unicode(row[columns['transcription']]).replace('|speech-in-noise','').strip()
            logging.debug(u"Step 0 : {}" .format(transcription ))
            if not is_perform_chat_normalization:
                # performing this operation only for ivr data as some of these special characters are required for chat normalizations, maybe think of a better way to do this. There are some cases with a mix of both types of data
                clean_transcription, ac_quality_flag = cleanTranscription(transcription)
                logging.debug('done with clean_transcription')
                #clean_transcription = clean_transcription.decode(custom_encoding).encode('latin-1')
                ## Write to the output file
                writer.write(unicode(row[col_indices['filename']])+u'\t'+unicode(row[columns['transcription']])+u'\t'+row[col_indices[str(intent)]]+u'\n')
                #writer.write(str([row[col_indices['filename']], row[col_indices['transcription']], row[col_indices[intent]], clean_transcription, ac_quality_flag]) +'\n')
                #writer.write(str(row[col_indices['filename']] + '\t' + row[col_indices['transcription']] + '\t' + row[col_indices[intent]] + '\t' + clean_transcription + '\t' + ac_quality_flag +'\n'))
            else:
                clean_transcription=transcription
                ac_quality_flag=True

            if config.get('params', 'replace_word_classes_in_data').lower()=="true" and is_perform_chat_normalization:
                if is_perform_chat_normalization:
                    WC_normalized_utt = chat_normalizer.perform_normalization(clean_transcription)
                else:
                    #performing only word class replacement (this is for IVR data TODO the chat normalization script probably won't be useful for IVR data)
                    WC_normalized_utt = chat_normalizer.word_class_replacement.replace_word_class(out)
            else:
                ##TODO replace extra for chat data
                WC_normalized_utt=chat_normalizer.chat_extra(clean_transcription)
            logging.debug('done with perform_normalization')
            WC_normalized_utt = chat_normalizer.remove_additional_space(WC_normalized_utt)
            logging.debug('done with remove_additional_space')

            if ac_quality_flag==False:
                ac_quality='Bad'
                bad_quality_utts.write(unicode(row[col_indices['filename']]) + ',' + row[col_indices['transcription']] + ',' + clean_transcription + ',' + row[col_indices[intent]] + '\n')
                logging.debug('done with bad_quality_utts write')

            if config.get('params', 'second_responses_exist').lower()!="true":
                first_response_file.write(unicode(row[col_indices['filename']])+u'\t' + clean_transcription + u'\t'+ row[col_indices[intent]] + u'\t'+ ac_quality + u'\t' + unicode(row[col_indices['transcription']]) + u'\n')
                if config.get('params', 'contains_utt_repititions_as_counts').lower()=="true":
                    if int(row[col_indices['Count']])>1:
                        for rep_cnt in range(int(row[col_indices['Count']])):
                            WC_normalized_first_responses_file_with_dup.write(unicode(row[col_indices['filename']])+'_'+str(rep_cnt)+'\t'+WC_normalized_utt+'\t'+row[col_indices[str(intent)]]+'\t'+row[col_indices[str(granular_intent)]]+'\n')
                    else: WC_normalized_first_responses_file_with_dup.write(unicode(row[col_indices['filename']])+'\t'+WC_normalized_utt+'\t'+row[col_indices[str(intent)]]+'\t'+row[col_indices[str(granular_intent)]]+'\n')
                WC_normalized_first_responses_file.write(unicode(row[col_indices['filename']])+'\t'+WC_normalized_utt+'\t'+row[col_indices[intent]]+'\t'+row[col_indices[granular_intent]]+'\n')
            else:
                ## Writing responses to first AND second response files
                if row[col_indices['cap_level']] == 'firstresp':
                    first_response_file.write(unicode(row[col_indices['filename']]) + '\t' + clean_transcription + '\t' + row[col_indices[str(intent)]] +'\t' + ac_quality + '\t' + row[col_indices[str(granular_intent)]] + '\n')
                    WC_normalized_first_responses_file.write(str(row[col_indices['filename']])+'\t'+WC_normalized_utt+'\t'+row[col_indices[str(intent)]]+'\t'+row[col_indices[str(granular_intent)]]+'\n')
                elif row[col_indices['cap_level']] == 'secondresp':
                    second_response_file.write(unicode(row[col_indices['filename']]) + '\t' + clean_transcription + '\t' + row[col_indices['fulltag']] + '\t' + ac_quality + '\t' + row[col_indices['transcription']] + '\n')
                    WC_normalized_second_responses_file.write(unicode(row[col_indices['filename']])+'\t'+WC_normalized_utt+'\t'+row[col_indices['fulltag']]+'\t'+row[col_indices['topic']]+'\t'+row[col_indices['goal']]+'\t'+row[col_indices[str(intent)]]+'\n')
                else:
                    raise Exception("Utterance has problematic cap_level: "+row[col_indices['cap_level']])

            ##since it's parallel processing we cannot count the words & update the same dict here
            # for word in WC_normalized_utt.split():
                # if word_frequency.has_key(word):
                    # word_frequency[word]+=1
                # else:
                    # word_frequency[word]=1
        except Exception as e:
            print e
            error_utts.write(str(row[col_indices['filename']])+ '\n')

    results = pool.map(process_individual_lines,range(1,sh.nrows))
    print 'total utterances processed: '+str(sh.nrows)
    print 'total utterances rejected: '+str(rejected)
    ## Closing open files
    if config.get('params', 'second_responses_exist').lower()=="true":
        WC_normalized_second_responses_file.close()
    WC_normalized_first_responses_file.close()
    with codecs.open( filename, 'rb', encoding=custom_encoding) as WC_normalized_first_responses_file:
        for line in WC_normalized_first_responses_file:
            line = line.strip()
            cols = line.split('\t')
            unique_id=cols[0]
            if unique_id in filename_unique_set:
                # raise Exception('filenames specified is not unique, please ensure that all the filename(ids) are unique & re-run')
                print('filenames(ids) specified is not unique, please ensure that all the filename(ids) are unique & re-run')
                sys.exit(1)
            filename_unique_set.add(unique_id)
            word_frequency_counter.update(cols[1].split())

    error_utts.close()
    # for word,freq in word_frequency.iteritems():
        # word_frequency_file.write(word + "\t" + str(freq) + "\n")
    for word,freq in word_frequency_counter.most_common():
        word_frequency_file.write(word + "\t" + str(freq) + "\n")

        # row_ctr+=1
    filename_limited=os.path.join(config.get('params', 'output_dir'), 'FirstResponses_WCNormalized_limited_vocab')
    min_freq=config.get('params','min_word_freq')
    with codecs.open(filename_limited, 'wb',encoding=custom_encoding) as limited_vocab_file:
        with codecs.open( filename, 'rb', encoding=custom_encoding) as WC_normalized_first_responses_file:
            for line in WC_normalized_first_responses_file:
                line = line.strip()
                cols = line.split('\t')
                trans=cols[1]
                updated_trans=' '.join([word if word_frequency_counter[word]>=min_freq else '_class_unknown' for word in trans.split() ])
                cols[1]=updated_trans
                limited_vocab_file.write('\t'.join(cols)+'\n')


class WordClassReplacement:

   def __init__(self, word_class_file,custom_encoding='utf-8'):
       """This fucntion requires the filename containing the word classes required for replacements

       word_class_file: the file locations to the word class file

       """
       self.word_classes={}
       self.word_classes_new={}
       self.custom_encoding=custom_encoding
       self.read_word_classes(word_class_file)
       ################## FOR WORD CLASS NORMALIZATION ONLY ###############
       #escaping required if (regex) special characters present in word class
       raw_string=ur'\b(?:'+ur'|'.join([re.escape(x) for x in sorted(self.word_classes_new.keys(), reverse = True)])+ur")'?s?\b"
       self.robj = re.compile(raw_string,flags=re.IGNORECASE)

   def read_word_classes(self,word_classes_file):
       print custom_encoding
       word_class_file = codecs.open(word_classes_file, 'rb', encoding=self.custom_encoding)
       #this map is hold a word as the key & a list of word classes it is associated with as the value, this is just to do a validation. A word should be mapped to only one word class
       word_and_classes = {}

       for line in word_class_file:
           #converting the word classes read into lower case, till now there where no cases where a case sensitive word class was required
           line=line.strip().lower()
           ## Discard blank lines
           if line=="":
               continue
           ## Read class names
           elif line.startswith('_class_'):
               current_word_class = line
               self.word_classes[current_word_class]=set([])
               continue

           list_of_word_classes = word_and_classes[line] if word_and_classes.has_key(line) else []
           list_of_word_classes.append(current_word_class)
           word_and_classes[line] = list_of_word_classes

           self.word_classes[current_word_class].add(line)
           self.word_classes_new[line]=current_word_class

       multiple_entries = {word:classes for word,classes in word_and_classes.iteritems() if len(classes)>1}
       if(len(multiple_entries)>0):
           print 'mulitple entries are present for some words in the word class file , correct them & re-run the script.'
       for word,classes in multiple_entries.iteritems():
           print 'Multiple entries present for the word '+ word + ' .They are in classes :- ' + ','.join(classes)
       print ( "Read "+ str(len(self.word_classes)) +" word classes" )
       #print (str(self.word_classes.keys()))

   def replace_word_class(self, text):
       """
       This fucntion performs word class replacement based on the word class definition file that was provided earlier.
       Provide the sentence on which to perform word class replacement as input

       :text:input sentence to be transformed
       :returns: the sentence with the word classes replaced with the corresponding tag

       """

       out = self.robj.sub(lambda m: self.word_classes_new[m.group(0).lower()] if self.word_classes_new.has_key(m.group(0).lower()) else self.word_classes_new[m.group(0).lower()[:-1].replace(ur"'",ur"")], text)
       print_log_if_diff(text,out)
       return out




def print_log_if_diff(original_text,out,extra_debug_message=u''):
    # if(logging.getLogger().isEnabledFor(logging.DEBUG) and original_text != out):
    if(logging.getLogger().isEnabledFor(logging.DEBUG)):
        logging.debug(extra_debug_message + u' function:- '+ inspect.stack()[1][3] +u'---original text:- ' + original_text + u' ---changed text:- '+ out)


def handle_punctuation(text):
    #removing question mark from the data
    #out = re.sub(ur'(\-|\.|\,|\?|\!|\*|\$|\#|\=|\^|\&|\'|\"|\/){1,}',' ',text)
    #keeping apostrophe separately as word expansion done with it
    # out = re.sub(ur'(\-|\.|\,|\?|\!|\*|\$|\#|\=|\^|\&|\"|\/){1,}',' ',text)
    out = re.sub(ur'(\-|\.|\,|\?|\!|\*|\$|\#|\=|\^|\&|\"|\/|\(|\)){1,}',' ',text)
    #removing question mark from the normalization step
    # out = re.sub(ur'(\-|\.|\,|\!|\*|\$|\#|\=|\^|\&|\"|\/|\(|\)){1,}',' ',text)
    #handling / & - separately for date
    # out = re.sub(ur'(\.|\,|\?|\!|\*|\$|\#|\=|\^|\&|\"){1,}',' ',text)
    print_log_if_diff(text,out)
    return out

def handle_hyphen_slash(text):
    out = re.sub(ur'(\-|\/"){1,}',' ',text)
    print_log_if_diff(text,out)
    return out

def basic_normalization(text):
    # TODO check why colon is not getting replaced with the follwoing regex
    out = re.sub(ur"\?|\!|\(|\)|\[|\]|\"|~|\+|,|{|}|:|;|\*|\|\t|\n|\r|%|@", ' ', text,re.I)
    out = re.sub(ur" _ ", ' ', out)
    out = re.sub(ur":" , ' ', out,re.I)
    print_log_if_diff(text,out)
    return out

def special_char_normalization(text):
    # out = re.sub(ur"\.|<s>|=|;|\/|\-|>|\*|<|`|\\|\^" , ' ', text,re.I)
    out = re.sub(ur"\.|<s>|=|;|\/|\-|>|\*|<|\\|\^" , ' ', text,re.I)
    print_log_if_diff(text,out)
    return out

def special_apostrophe_replace(text):
    out = re.sub(ur"[`|‘|’]" , "'", text,re.I)
    print_log_if_diff(text,out)
    return out

class StemWord:

    def __init__(self,config):
        try:
            # import nltk
            from nltk import WordNetLemmatizer,pos_tag
            # this is used for lemmatization
            from nltk.corpus import wordnet
        except ImportError:
            print "Please install NLTK to use this script!"
            sys.exit()
        import threading
        try:
            import cPickle as pickle
        except:
            import pickle
        # print (nltk.__version__)
        self.lock = threading.Lock()
        self.custom_encoding=config.get('params','encoding')
        is_perform_stemming = config.get('params','is_perform_stemming').strip().lower()=='true'
        stem_exception_filename = config.get('params','stem_exception_file')
        stem_replacement_filename =config.get('params','stem_replacement_file')
        ## Read stem-exception list
        self.stem_excepts = set()
        if stem_exception_filename.strip() and os.path.isfile(stem_exception_filename):
            with codecs.open(stem_exception_filename,encoding=self.custom_encoding) as stem_exception_file:
                self.stem_excepts = set([i.strip() for i in stem_exception_file if i.strip()!=""])
        else:
            print('stem exceptions file not present. Hence ignored')

        # self.lemmatized_words = {'hi':'hello'}
        self.lemmatized_words = {}
        if stem_replacement_filename.strip() and os.path.isfile(stem_replacement_filename):
            with codecs.open(stem_replacement_filename,encoding=self.custom_encoding) as stem_replacement_file:
                self.lemmatized_words = dict([i.strip().split('\t') for i in stem_replacement_file if i.strip()!=""])
        else:
            print('stem replacement file not available. Hence ignored')

        if not os.path.isdir(config.get('params', 'output_dir')):
            os.makedirs(config.get('params', 'output_dir'))
        self.stemming_output_filename = os.path.join(config.get('params', 'output_dir'),'stemming_output')
        # self.stemming_output_file = codecs.open(self.stemming_output_filename,'wb',encoding=self.custom_encoding)
        # self.stemming_output_file = codecs.open(self.stemming_output_filename,'ab',encoding=self.custom_encoding)
        # self.lmtzr = nltk.WordNetLemmatizer()
        self.lmtzr = WordNetLemmatizer()

    def get_stems(self,text):
        '''
        This function would replace the words present in sentence with the lemmatized form.
        This would also update the dictionary file with the stems, so this operation is required even if we just want to store the list of stems
        '''
        # utt_parts = text.split()
        utt_parts = word_tokenize(text)
        stems_dict={}
        for i in range(len(utt_parts)):
            if '_class_' in utt_parts[i]:
                continue
            if self.lemmatized_words.has_key(utt_parts[i]):
                # would have already occured before
                continue

            word = utt_parts[i]
            # pos_tagged = nltk.pos_tag([word])
            pos_tagged = pos_tag([word])
            lemma = self.lmtzr.lemmatize(utt_parts[i], self.get_wordnet_pos(pos_tagged[0][1]))
            if lemma == utt_parts[i]:
                continue
            self.lemmatized_words[utt_parts[i]] = lemma #TODO change for multiprocessing, each process uses a different variable
            #self.lock.acquire()
            #try:
            #    self.lemmatized_words[utt_parts[i]] = lemma
            #finally:
            #    self.lock.release()
            stems_dict[utt_parts[i]]=lemma
        return stems_dict

    def handle_stemming(self,text):
        '''
        This function would replace the words present in sentence with the lemmatized form.
        This would also update the dictionary file with the stems, so this operation is required even if we just want to store the list of stems
        This function also returns the stems dictionary created for this line, this would only have entries created for this line
        '''
        # utt_parts = text.split()
        utt_parts = word_tokenize(text)
        stems_dict={}
        for i,actual_word in enumerate(utt_parts):
            if '_class_' in actual_word:
                continue
            if len(actual_word)<=2: #TODO most 1 or 2 letter words won't require stemming
                continue
            if actual_word.lower() in self.stem_excepts:
                continue
            if self.lemmatized_words.has_key(actual_word.lower()):
                lemma = self.lemmatized_words[actual_word.lower()]
                utt_parts[i]= lemma
                # stems_dict[actual_word.lower()]=lemma
                continue

            #get pos tag for entire sentence will take longer # TODO would be better to use entire sentence for accuracy, but eventually it will be replacement will be with a dictionary, so if a word have noun form it would return 'noun' form as opposed to verb form
            pos_tagged = pos_tag([actual_word])
            lemma = self.lmtzr.lemmatize(actual_word, self.get_wordnet_pos(pos_tagged[0][1],actual_word))
            if lemma.lower() == actual_word.lower():
                continue
            # using original word if replacement is 1 or 2 letters #TODO most of the case with 1 or 2 letters are incorrect
            if len(lemma)<=2:
                lemma=actual_word.lower()
            self.lemmatized_words[actual_word.lower()] = lemma #TODO change for multiprocessing, each process uses a different variable
            stems_dict[actual_word.lower()]=lemma
            # self.stemming_output_file.write('\t'.join([utt_parts[i],lemma])) #TODO
            #self.lock.acquire()
            #try:
            #    self.lemmatized_words[utt_parts[i]] = lemma
            #finally:
            #    self.lock.release()
            utt_parts[i]=lemma
        return u' '.join(utt_parts),stems_dict

    def get_wordnet_pos(self,treebank_tag,word):
        if treebank_tag.startswith('J'):
            return wordnet.ADJ
        elif treebank_tag.startswith('V'):
            return wordnet.VERB
        #elif treebank_tag.startswith('N'):
        #    return wordnet.NOUN
        elif treebank_tag.startswith('R'):
            return wordnet.ADV
        elif 'ing' in word[-4:]:
            return wordnet.VERB #TODO some non verbs would also have ing at the end. Eg:- something
        else:
            return wordnet.NOUN


    def write_stem_list(self):
        '''
        This function should be called only at the end to write the output of the saved stem list
        '''
        with codecs.open(self.stemming_output_filename,'wb',encoding=self.custom_encoding) as stemming_output_file:
            # pickle.dump(self.lemmatized_words, stemming_list)
            for k,v in self.lemmatized_words.iteritems():
                stemming_output_file.write('\t'.join([k,v])+'\n')


class ChatNormalizer:
    # dictionary = enchant.DictWithPWL('en_US', "PWL.txt")
    def __init__(self,config):
        import atexit
        self.custom_encoding=config.get('params','encoding')
        if config.get('params','debug_mode').lower()=='true':
            print "setting debug logs"
            logging.basicConfig(stream=sys.stdout, level = logging.DEBUG)
        else:
            logging.basicConfig(stream=sys.stderr, level = logging.ERROR)
        # self.months_without_word_boundaries=['january','february','march','april','may','june','july','august','september','october','november','december','jan','feb','mar','apr','jun','jul','aug','sep','sept','oct','nov','dec']
        self.months_complete=['january','february','march','april','may','june','july','august','september','october','november','december','jan','feb','mar','apr','jun','jul','aug','sept','sep','oct','nov','dec']
        #TODO also add august to ambiguous months, maybe june,april too as its a name
        self.ambiguous_months=[r'apr',r'may']
        #taking only non ambiguous months
        self.non_ambiguous_months = [month for month in self.months_complete if month not in self.ambiguous_months]
        # self.months=[r'\bjanuary\b',r'\bfebruary\b',r'\bmarch\b',r'\bapril\b',r'\bjune\b',r'\bjuly\b',r'\baugust\b',r'\bseptember\b',r'\boctober\b',r'\bnovember\b',r'\bdecember\b',r'\bjan\b',r'\bfeb\b',r'\bmar\b',r'\bjun\b',r'\bjul\b',r'\baug\b',r'\bsep\b',r'\bsept\b',r'\boct\b',r'\bnov\b',r'\bdec\b']
        # self.ambiguous_months=[r'\bapr\b',r'\bmay\b']
        # self.days = [r'\bmonday\b',r'\btuesday\b',r'\bwednesday\b',r'\bthursday\b',r'\bfriday\b',r'\bsaturday\b',r'\bsunday\b',r'\bmon\b',r'\btue\b',r'\bwed\b', ]
        self.days = [r'monday',r'tuesday',r'wednesday',r'thursday',r'friday',r'saturday',r'sunday',r'mon',r'tue',r'wed', ]
        self.numbers_in_english = ["zero","one","two","three","four","five","six","seven","eight","nine","hundred","ten","eleven","twelve","thirteen","fourteen","fifteen","sixteen","seventeen","eighteen","nineteen","twenty","thirty","forty","fifty","sixty","seventy","eighty","ninety"]
        self.compile_regexes()
        self.custom_encoding=config.get('params','encoding')
        if not os.path.isdir(config.get('params', 'output_dir')):
            os.makedirs(config.get('params', 'output_dir'))
        if config.get('params', 'replace_word_classes_in_data').lower()=="true":
            ## Read word classes
            self.word_class_replacement = WordClassReplacement(config.get('params', 'word_classes_file'))
        self.read_word_expansions(config.get('chat','word_expansions_file'))
        self.output_dir=config.get('params','output_dir')
        if not os.path.isdir(config.get('params', 'output_dir')):
            os.makedirs(config.get('params', 'output_dir'))
        with open(os.path.join(self.output_dir,'suggested_word_expansions.txt'),'a') as word_exp:
            word_exp.write('\n')
        self.thread_local = threading.local()
        self.is_perform_spell_check=config.get('chat','is_perform_spell_check').lower()=='true'
        self.is_perform_heuristic_name_check = config.get('chat','is_perform_heuristic_name_check').lower()=='true'


        self.is_perform_ner_extraction = config.get('chat','is_perform_ner_extraction').lower()=='true'

        if self.is_perform_heuristic_name_check | self.is_perform_ner_extraction:
            #creating a file to store extracted entities,a separate file will be created for each entity & will have 2 columns :- entity value, sentence in which it appeared
            if not os.path.isdir(os.path.join(self.output_dir,'extracted_entities')):
                os.makedirs(os.path.join(self.output_dir,'extracted_entities'))
            self.name_entity_file=codecs.open(os.path.join(self.output_dir,'extracted_entities','name.txt'),'w',encoding=self.custom_encoding)
            self.name_entity_file.write('name\tsentence\n')

        # currently spell check type can have the values - enchant, remote
        self.spell_check_type=config.get('chat.spell_check','spell_check_type').lower()
        if self.is_perform_spell_check:
            if self.spell_check_type=='enchant':
                import enchant
                self.personalized_word_dict=config.get('chat.spell_check','personalized_word_dict')
                if self.personalized_word_dict=='':
                    self.dictionary = enchant.Dict('en_US')
                else:
                    print('using the personalized word dictionary - '+self.personalized_word_dict)
                    self.dictionary = enchant.DictWithPWL('en_US',self.personalized_word_dict)

            elif self.spell_check_type=='remote':
                self.spell_check_model_url=config.get('chat.spell_check','spell_check_model_url')
                if self.spell_check_model_url=='':
                    logger.error('for using web2nl spell checker you will have to give a url for a model with just the spell checker')
                    print ('for using web2nl spell checker you will have to give a url for a model with just the spell checker')
                    print('Existing from program')
                    sys.exit(1)
                print('spell checker model url is - '+self.spell_check_model_url)

        if self.is_perform_ner_extraction:
            from nltk import word_tokenize
            from nltk.tag.stanford import StanfordNERTagger
            from nltk.tokenize.moses import MosesDetokenizer
            self.stanford_ner_model=config.get('chat.ner','stanford_ner_model')
            self.stanford_jar=config.get('chat.ner','stanford_jar')

        self.spell_check_model_url = config.get('chat.spell_check','spell_check_model_url')
        self.personalized_word_dict = config.get('chat.spell_check','personalized_word_dict')
        self.is_perform_stemming = config.get('params','is_perform_stemming').strip().lower()=='true'
        if self.is_perform_stemming:
            self.stem_word = StemWord(config)
        atexit.register(self.exit_handler)
        custom_regex_filename=config.get('chat','custom_regex_file')
        self.is_custom_regex=custom_regex_filename.strip()!=''
        self.custom_regexes=[]
        if self.is_custom_regex and not os.path.isfile(custom_regex_filename):
            print('custum regex file provided is not present. Hence ignoring this operation')
            self.is_custom_regex = False
        if self.is_custom_regex:
            with codecs.open(custom_regex_filename,'rb',encoding=self.custom_encoding) as custom_regex_regex_file:
                regex_no=0
                for line in custom_regex_regex_file:
                    regex_no+=1
                    line = line.strip()
                    if line=='':
                        continue
                    cols=line.split('\t')
                    print('custom regex {} is {} and replacement is {}'.format(regex_no,cols[0],cols[1]))
                    # using a list tuple instead of map as there could be multiple regexes for the same replacement
                    self.custom_regexes.append( (cols[1],re.compile(cols[0],re.I)) )


    def exit_handler(self):
        # self.stem_word.write_stem_list()
        print('exit function')

    def handle_custom_regex_operations(self,text):
        out = text
        for to_replace,custom_regex in self.custom_regexes:
            out = custom_regex.sub(to_replace,out)
        print_log_if_diff(text,out)
        return out

    def compile_regexes(self):
        ## Dates

#handled as part of another regex below
#        self.ill_formed_dates = [
#                                 #Eg:- jan2017 , jan10th
#                                 re.compile(ur'('+'|'.join(self.months_complete)+')(\d{1,4}(?:nd|st|rd|th)?)', re.I),
#                                 #Eg:- 2014jan, 10thjan
#                                 re.compile(ur'(\d{1,4}(?:nd|st|rd|th)?)('+'|'.join(self.months_complete)+')',re.I)]
        self.space_characters = re.compile(ur'\s{2,}',flags=re.IGNORECASE)

        #\xa0 is actually non-breaking space in Latin1 (ISO 8859-1) & for utf-8 it is \xc2\xa0. Refer - https://stackoverflow.com/questions/10993612/python-removing-xa0-from-string
        self.non_breaking_space = re.compile(ur"\xc2\xa0|\xa0",flags=re.IGNORECASE)

        weekdays_regex_string = ur'(?:'+ ur'|'.join(self.days) + ur')'
        weekdays_regex_string_with_boundary = ur'\b(?:'+ ur'|'.join(self.days) + ur')\b'
        #cannot use this standalone as nd etc optional
        days_regex_string = ur'(?:\d{1,2}(?:nd|th|rd|st)?)'
        months_complete_regex_string=ur'(?:'+'|'.join(self.months_complete)+ur')'
        months_complete_regex_string_with_booundary=ur'\b(?:'+'|'.join(self.months_complete)+ur')\b'
        year_regex_string =ur'(?:\d{4}|\d{2})'
        year_day_combined_regex = ur'(?:\d{4}|\d{1,2}(?:nd|th|rd|st)?)'
        date_sep = ur'\s*(?:[\s,\/\.-]|of)\s*'
        def get_date_regex_comb1():
            # this is a combination of month, day, year in all possible combinations, along with optional weekday in the beginning & end
            # Eg;- 20th jan,2017 or 20/jan/17 etc
            # l_comb = [
                 # [year_regex_string,days_regex_string,months_complete_regex_string],
                 # [year_regex_string,months_complete_regex_string,days_regex_string],
                 # [days_regex_string,months_complete_regex_string,year_regex_string],
                 # [days_regex_string,year_regex_string,months_complete_regex_string],
                 # [months_complete_regex_string,year_regex_string,days_regex_string]
                 # [months_complete_regex_string,days_regex_string,year_regex_string]
                 # ]
            # the separator still needs to be there in between these regexes, otherwise could use {2} for repetitions
            l_comb = [
                 [year_day_combined_regex,year_day_combined_regex,months_complete_regex_string],
                 [year_day_combined_regex,months_complete_regex_string,year_day_combined_regex],
                 [months_complete_regex_string,year_day_combined_regex,year_day_combined_regex]
                 ]
            comb = ur'(?:'+ weekdays_regex_string + date_sep + ')?' + ur'(?:'+ ur'|'.join([ur'(?:' + date_sep.join(l) + ur')' for l in l_comb]) + ur')' + ur'(?:'+ date_sep + weekdays_regex_string + ur')?'
            # print 'date_regex_comb1 ' + comb
            return comb

        def get_date_regex_comb2():
            # this is a combination of month, day, year in all possible combinations, along with optional weekday in the beginning & end
            #this is for the case where the there is no separation between these
            # Eg;- 20thjan2017 or 20jan17 etc

            # the separator still needs to be there in between these regexes, otherwise could use {2} for repetitions
            l_comb = [
                 [year_day_combined_regex,months_complete_regex_string,year_day_combined_regex],
                 [months_complete_regex_string,year_day_combined_regex],
                 [year_day_combined_regex,months_complete_regex_string]
                 ]
            comb = ur'(?:'+ weekdays_regex_string + date_sep + ')?' + ur'(?:'+ ur'|'.join([ur'(?:' + ''.join(l) + ur')' for l in l_comb]) + ur')' + ur'(?:'+ date_sep + weekdays_regex_string + ur')?'
            # print 'date_regex_comb1 ' + comb
            return comb

        def get_date_regex_comb3():
            # month & year/day combo with weekdays as optional in the beginning & end
            # Eg:- jan/12 or  20th jan
            l = [days_regex_string,year_regex_string]
            comb=ur'(?:'+ weekdays_regex_string + date_sep + ')?' + ur'(?:(?:' + year_day_combined_regex + date_sep + months_complete_regex_string + ur')|(?:'+months_complete_regex_string + date_sep + year_day_combined_regex + ur'))(?:'+date_sep+weekdays_regex_string+ ur')?'
            # print 'date_regex_comb2 ' + comb
            return comb

        # get_date_regex_combs()

        # check test cases after modifying any of the regexes
        self.dates_regex = [
                            # this regex is for handling cases like 10-10-17, 10-10-2017, 10/10/17 , 10/10/2017, 10.10.17 , 10 10 17 , 10 10 2017
                            # patterns like 27.12 are not handled. Conflicts with numbers like 200.00
                            re.compile(ur'(?:\d{1,2}\s*[\s/\.-]\s*\d{1,2}\s*[\s/\.-]\s*(?:\d{4}|\d{2}))',flags=re.IGNORECASE),
                            re.compile(get_date_regex_comb1(), re.I),
                            re.compile(get_date_regex_comb2(),re.I),
                            re.compile(get_date_regex_comb3(), re.I),
                            # Regex for incomplete date regex should be after complete regexes
                            # Eg:- 10/17, 10/2017 , 10.2017 TODO "10.2017" because numbers are generally ends with 2 decimal places.Might have to remove. Excluding 10 - 17, 10 - 2017, 10.17 as could occur for regular numbers
                            re.compile(ur'(?:\d{1,2}\s*[/]\s*(?:\d{4}|\d{2}))|(?:\d{1,2}\s*[\.]\s*\d{4})',flags=re.IGNORECASE),

                            #the following is a combination of date with the follwoing components in the order - weekday month day year, where weekday & year kept optional
                            # Eg:- monday,jan 20th or jan 20th or jan 20th,2017 or jan-20th-2017,jan2017,jan20th TODO need to look for negative cases later & improve this regex if required
                            # re.compile(ur'(?:(?:'+ weekdays_regex_string + '\s*[,/\.-]?\s*)?' + months_complete_regex_string +'\s*[,/\.-]?\s*' + days_regex_string + '(?:\s*(?:[,/\.-]|of)?\s*'+year_regex_string+')?)', re.I),

                            # re.compile(ur'(?:(?:'+ weekdays_regex_string+ '\s*[,/\.-]?\s*)?' + days_regex_string +'\s*(?:[,/\.-]|of)?\s*' + months_complete_regex_string + ur'(?:\s*(?:[,/\.-]|of)?\s*'+ year_regex_string +')?)', re.I),
                            #The following would handle cases where users mention just the month
                            re.compile(ur'\b(?:'+'|'.join(self.non_ambiguous_months)+ ur')\b',re.I),
                            #TODO delete re.compile(ur'((?:'+'|'.join(self.non_ambiguous_months)+ ur')(?:'+ date_sep + year_day_combined_regex + ur')?|(?:'+'|'.join(self.ambiguous_months)+')(?:'+ date_sep + year_day_combined_regex +  '))',re.I),
                            #old regex, removing as there is a separate one to handle months with alphabets
                            # re.compile(ur'((?=\d{4})\d{4}|(?=[a-zA-Z]{3})[a-zA-Z]{3}|\d{2})((?=\/)\/|\-)((?=[0-9]{2})[0-9]{2}|(?=[0-9]{1,2})[0-9]{1,2}|[a-zA-Z]{3})((?=\/)\/|\-)((?=[0-9]{4})[0-9]{4}|(?=[0-9]{2})[0-9]{2}|[a-zA-Z]{3})',re.I)
                            ]
        self.masked_dates = [re.compile(ur'(?:\s*X{1,2}\s*\/)(\s*X{2,4}\s*\/)(\s*X{2}\d{2}|\s*\d{4})',flags=re.IGNORECASE)]
        # self.dollar_amount = re.compile(ur'(\$\s?\d*\,?\d*\s\.?\s?\d{1,2}|\d*\,?\d*\.?\d{1,2}\s?\$)') #Old regex.
        #self.dollar_amount = re.compile(ur'(\$\s?\d*(\s?\,?\s?)\d*(\s?\.?\s?)\d{1,2}|\d*(\s?\,?\s?)\d*(\s?\.?\s?)\d{1,2}\s?\$)',flags=re.IGNORECASE)
        #modified regex to handle masked dollar amounts as well. including format XX / XXXX
        # currency_part = ur'(?:(?:(?:X|x|\d)+[\s,\.\/\-]*)+\b|(?:X|x|\d)+)'
        currency_symbols=[u'\$',u'£',u'€',u'¥']
        currency_words=['dollar','euro']
        currency_symbols_joined=ur'(?:'+ '|'.join(currency_symbols) + ')'
        currency_words_joined=ur'(?:'+ '|'.join(currency_words) + ')s?'
        currency_word_symbols=ur'(?:' + currency_symbols_joined + '|' + currency_words_joined + ')'
        # currency_part1 = ur'(?:(?:\d|x){1,5}\s*[,\.\/\-]\s*(?:\d|x){1,5})+'
        #keeping only x instead of x or X because we are ignoring case in the regex replace
        #the following regex have been updated to reduce the complexity of regex checking, please check test case before modifying
        currency_part1 = ur'(?:[x\d]{2}[x\d,\.\/\-]+)'
        # currency_part2 = ur'(?:\d|x)+'
        self.currency_amounts = [
                                #this will handle cases like $ xxx or $ xxx,xxx,xxx etc
                                re.compile(currency_word_symbols + ur'\s*'+currency_part1 ,flags=re.IGNORECASE),
                                #this will handle cases like xxx $ or xxx,xxx,xxx $ etc
                                re.compile(currency_part1 + ur'\s*' + currency_word_symbols,flags=re.IGNORECASE),
                                # re.compile(currency_word_symbols + ur'\s*'+currency_part2 ,flags=re.IGNORECASE),
                                # re.compile(currency_part2 + ur'\s*' + currency_word_symbols,flags=re.IGNORECASE)
                            ]
        self.currency_regex = re.compile(currency_word_symbols,flags=re.IGNORECASE)
        #added for optus
        self.masked_account_numbers = re.compile(ur'\s?\d{0,4}(X|x){1,4}-*(X|x){1,4}\d{0,4}\s?', flags=re.IGNORECASE)
        #The following regex is for handling time
        #Eg: 10:10 am, 2300hrs
        self.time = re.compile(ur"(?:\d{1,2}\s*:?\s*)?\d{1,2}\s*(?:am|pm|hrs|hours)", re.I)
        self.url = re.compile(ur"(http|ftp|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?|((mailto\:|(news|(ht|f)tp(s?))\://){1}\S+)|/^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/|^[a-zA-Z0-9\-\.]+\.(com|org|net|mil|edu|COM|ORG|NET|MIL|EDU)$",flags=re.IGNORECASE)
        #self.url = re.compile(ur"(http|ftp|https):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&amp;:/~\+#(?:\s*X{1,2}\s*\/)(\s*X{2,4}\s*\/)(\s*X{2}\d{2}|\s*\d{4})]*[\w\-\@?^=%&amp;/~\+#])?|((mailto\:|(news|(ht|f)tp(s?))\://){1}\S+)|/^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/|^[a-zA-Z0-9\-\.]+\.(com|org|net|mil|edu|COM|ORG|NET|MIL|EDU)$")
        print "url regex ", self.url
        self.days_regex = re.compile(weekdays_regex_string_with_boundary,re.I)
        self.percentages = [
                        re.compile(ur'(?:(?:'+'|'.join(self.numbers_in_english)+')?\s?(?:'+'|'.join(self.numbers_in_english)+')+\s?(?:%|percent(?:age|ile)?))',flags=re.IGNORECASE),
                        #TODO generally when people mention numbers in percetage length would be 1 to 3. so we needn't keep this check with more count for numbers here. Since it for the offline one it is fine
                        re.compile(ur'[0-9]+\.[0-9]*\s?(?:%|percent(?:age|ile)?)',flags=re.IGNORECASE),
                        #TODO generally when people mention numbers in percetage length would be 1 to 3. so we needn't keep this check with more count for numbers here. Since it for the offline one it is fine
                        re.compile(ur'[0-9]+\s?(?:%|percent(?:age|ile)?)',flags=re.IGNORECASE)
                        ]
        self.number_regexes = [
                    #handle cases where users mention number in english text #TODO handle consecutive mentions as a single _class_number entry. Eg:- 'one two'
                    re.compile(ur'(?:\b(?:'+'|'.join(self.numbers_in_english)+')\b)',re.IGNORECASE),
                    #handle cases like Eg:- 100 or 100.90 or 100.100.100 or 100,100,100 or 10th etc
                    re.compile(ur"\b[0-9]+(?:\s*[\.,]\s*[0-9]+)*(?:\s*(?:nd|th|rd|st))?\b", re.I),
                    # TODO will have to modify the _class_number_ref regex to match case where user mentions only #. So should exclude abc#abc & abc# & #abc
                    re.compile(ur"#(?=[^a-zA-Z0-9])",re.I)
                ]
        # this regex handle_words_with_numbers would generally be only useful at the beginning of a project
        #this is kept to identify cases where users give details like account number & all. But there could be spelling mistakes where user may not put a space between word & number
        # Eg:- abc123abc , abc_123, abc-123 etc
        self.special_word_regex = re.compile(ur"\b[a-zA-Z0-9_-]*[0-9]+[a-zA-Z0-9_-]*\b",flags=re.I)

        ## removing single quotes if they aren't used in prepositions
        self.apostrophe_preposition = re.compile(ur"\'[^a-zA-Z]|[^a-zA-Z]\'|'$|^'", re.I)

        #regex for handling emails
        self.email_regex = re.compile(ur'(([\w_\.-])+@([\d\w\.-])+\.([a-z\.]){2,6})',re.I)
        #self.email_regex = re.compile(ur'([\w\-\.]+@(\w[\w\-]+\.)+[\w\-]+)',re.I)
        #regex for handling urls
        #self.url_regex =re.compile(ur"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",re.I)
        self.url_regex =re.compile(ur"https?:\/\/(www\.)?[\-a-zA-Z0-9@:%._\+~#=\/]+", re.I)
        #regex to remove some html encoding in urls
        self.html_encoding_regex = re.compile("%[0-9]+",re.I)

        #regexes for phone number
        self.phone_number_regexes = [
                    re.compile(ur"\b\(?([0-9]{3})?[-.\s)]*[0-9]{3}[-.\s]*[0-9]{4}\b",re.I),
                    re.compile(ur"\b[0-9]{5}[\s.-]?[0-9]{5}\b",re.I)
                ]

        # masked entities are generally represented using x & - TODO might have to remove #
        self.masked_entity_regex = re.compile(ur"[xX#-]{2,}[0-9]*",re.I)

        ### Name heuristics regex, keeping group one as the sentence like 'my name is' & group 2 the actual replacement
        #Eg:-my name's Abc Bcd Cde , my name is Abc Bcd Cde
        self.name1 = re.compile(ur"([mM]y name\s*(?:is|'?s|:))((\s*[A-Z][A-Za-z]+){1,3})")
        #Eg:-my name's abc, my name is abc
        self.name2 = re.compile(ur"([mM]y name\s*(?:is|'?s|:))\s*([A-Za-z]+)")
        #Eg:-i'm Abc Bcd Cde, i am Abc Bcd Cde
        self.name3= re.compile(ur"([iI]\s*(?:am|'?m))((?:\s*[A-Z][A-Za-z]+){1,3})")
        #Eg:-        self.name6= re.compile(ur"[iI]\s*am(\s*[A-Z][A-Za-z]+){1,3}")
        #Eg:-i'm abc. Removing this regex for now. As it would mathccases like "i'm not"
        # self.name4=re.compile(ur"([iI](?:\\s*am|'?m))\\s*([A-Za-z]+)")
        ####The following regexes have been added for sirius xm. Here there was a node where we asked for user's name
        #In most of the cases when user gives his the 1st letter of the word is capital & most of cases had 2 word names.
        #Some general sentences also start with a word with 1st letter capital, so we shouldn't match those cases. Trying to match 2 or 3 letter names. Also separation kept as space & not full stop
        #Also trying to avoid cases with less than 3 letters for the name.i.e trying to avoid cases like - "Hi I need"
        #Eg:-Abc Bcd Cde
        # self.name8 = re.compile(ur"^([A-Z][a-z]{2,}\s*){2,3}")
        self.name5 = re.compile(ur"^(?!.*\b(?:Thanks?|The|For|Yet|You|Service|Morning|Afternoon|Evening|Service)\b|(?:Thanks?The|For|Not|Yet|You)\b)([A-Z][a-z]{2,}\s*){2,3}")
        #Some user give their names in all caps
        #Most of the names have 1 or 2 word. This regex is to match all cases where name is specified with 2 all caps words.
        #In some cases users type the entire sentence in capital, so we shouldn't match those cases
        #Eg:- ABC BCD blah blah & do not match - ABC BCD THIRDWORDNOTCAPITAL
        #Also trying to avoid cases with less than 3 letters for the name.
        # self.name9 = re.compile(ur"^([A-Z]{3,})\s+([A-Z]{3,})(?!\s*[A-Z]+\b)")
        self.name6 = re.compile(ur"^(?!.*\b(?:THANKS?|THE|FOR|YET|YOU|MORNING|AFTERNOON|EVENING)\b|(?:THANKS?|THE|FOR|NOT|YET|YOU)\b)([A-Z]{3,})\s+([A-Z]{3,})(?!\s*[A-Z]+\b)")

    def chat_regex_pre_word_class(self,text):
        text = self.handle_emails(text)
        text = self.handle_urls(text)
        #handling of html encoding should be after the url handling, because there are certain urls with html encoding & those will become split & result in extra words
        text = self.handle_html_encoding(text)
        text = self.handle_date(text)
        text = self.handle_time(text)
        text = self.handle_percentage(text)
        text = self.handle_currency(text)
        text = self.replace_word_expansions(text)
        text = self.handle_apostrophe_words_additional(text)
        text = self.handle_custom_regex_operations(text)
        # text = self.handle_radio_id(text)
        # text = self.handle_esn(text)
        #for optus
        # text = self.handle_masked_account_model_numbers(text)
        text = self.handle_phone(text)
        #removing spell check before word class replacement as certain words present in word class file were automatically changed by spell check
        # text = simple_spell_check(text)
        return text

    def chat_extra(self,text):
        text = self.chat_regex_pre_word_class(text)
        text = self.chat_regex_post_word_class(text)
        text = basic_normalization(text)
        #text = handle_question_mark(text)
        text = handle_punctuation(text)
        text = special_char_normalization(text)
        return text

    def chat_regex_post_word_class(self,text):
        #there were certain word classes which identified the class using model no, so number handling regex needs to be done after the word class replacement
        text = self.handle_numbers(text)

        # the function handle_words_with_numbers would generally be only useful at the beginning of a project
        # text = self.handle_words_with_numbers(text)
        # the function handle_masked_entities would be useful at the beginning of a project & later we will have to identify what each particular length of masked entity represents
        # text = self.handle_masked_entities(text)
        if self.is_perform_stemming:
            #replacing with stemmed version only if the option for stemming is set as true in the file
            stemmed_text,stems_dict = self.stem_word.handle_stemming(text)
            text = stemmed_text

        #keeping these after all the replacements as some normalizations use these special characters
        text = basic_normalization(text)
        #text = handle_question_mark(text)
        text = handle_punctuation(text)
        text = special_char_normalization(text)


        text = self.remove_additional_space(text)
        return text

    def perform_normalization(self,text,case_normalization=True):
        #uncomment this line to do additional word class substitutions
        out = self.chat_regex_pre_word_class(text)

        out = self.word_class_replacement.replace_word_class(out)

        if self.is_perform_heuristic_name_check:
            #TODO performing name heuristic before word class replacement as there were some vehicle names available as part of the name for Sirius XM
            out = self.handle_name_heuristics(out)

        if self.is_perform_ner_extraction:
            out = self.perform_ner_extraction(out)

        # chat_regex_post_word_class contains expressions to perform normalizations, this is kept before spell correction because for some cases incorrect spell correction was done for words with special characters. Eg:- stop/terminate
        out = self.chat_regex_post_word_class(out)

        if self.is_perform_spell_check:
            logging.debug('before spell checking')
            out = self.perform_spell_check(out)
            logging.debug('after spell checking')
            #doing word class replacement again after spell correction
            out = word_class_replacement.replace_word_class(out)

        if case_normalization:
            # perform case normaliztion after spell check. Currently the operations which require sentence case to be maintained are performed before this operation
            out = out.lower()
        # print_log_if_diff(text,out)
        return out


    def simple_spell_check(self,text):
            newWords = []
            words = text.split()
            for i in range(len(words)):
                word = words[i]
                if word.startswith('_class_'):
                    newWords.append(word)
                    continue
                if self.dictionary.check(word):
                    #print "found in dictionary"
                    newWords.append(word)
                elif self.dictionary.suggest(word) != []:
                    #print "first suggestion " + dictionary.suggest(word)[0]
                    newWords.append(self.dictionary.suggest(word)[0]) #Considering the very first suggestion from enchant.
                else: newWords.append(word)
            out = ' '.join(word for word in newWords)
            print_log_if_diff(text,out)
            return out


    def perform_spell_check(self,text):
        out = text
        if text!=u"":
            if self.spell_check_type=='enchant':
                out  = self.simple_spell_check(text) # adding spell check after the word class normalization as there are certain cases present in word class which got corrected
            elif self.spell_check_type=='remote':
                try :
                    out,_ = get_normalized_output(text,self.spell_check_model_url,'n1')
                    max_retries = 5 #keeping max retries to stop the code from running forever
                    count = 1
                    sleep_time=0.1
                    while( out==u'' and text!=u'' and count<=max_retries):
                        time.sleep(sleep_time)
                        out,_ = get_normalized_output(text,self.spell_check_model_url,'n1')
                    if out==u'' and text!=u'':
                        print u'unable to get the remote spell correction to work for the utterance {}. Taking original text as the transformed text'.format(text)
                        out = text

                except Exception as e:
                    print 'exception occurred for spell correction {} . using original text itself {}.Try reducing number of parallel hits'.format(e,text)
                    out = text

        # out = out.lower() # spell check was coverting some cases to Capital case
        print_log_if_diff(text,out)
        return out

    def is_perform_case_normalization_first(self):
        # currently spell check & name heuristics are the operations which require the case of the sentenence to be maintained. If these 2 are not required
        # then we can keep case normalization upfront
        return (not self.is_perform_spell_check) and (not self.is_perform_heuristic_name_check)

    def read_word_expansions(self,word_expansions_file_path):
        print self.custom_encoding
        word_expansions_file = codecs.open(word_expansions_file_path, 'rb', encoding=self.custom_encoding)

        for line in word_expansions_file:
            # converting to lower case
            line=line.strip().lower()
            cols = line.split('\t')
            word_expansions[cols[0]]=cols[1]


    def replace_word_expansions(self,text):
        out = special_apostrophe_replace(text)
        words = out.split()
        outl = []
        for word in words:
            to_add=word
            logging.debug(u'before word exp replacment for word ')
            logging.debug(word)
            if(word_expansions.has_key(word.lower())):
                logging.debug('word exp contains word')
                to_add=word_expansions.get(word.lower())
            outl.append(to_add)

        result = ' '.join(outl)
        print_log_if_diff(text,out)
        return result

    def getWordIndices(self, startChIndex, endChIndex, text):
        part1 = text[0:startChIndex]
        part2 = text[0:endChIndex+1]
        startWordIndex = len(part1.split())
        endWordIndex = len(part2.split())-1
        return (startWordIndex, endWordIndex)

    def get_stanford_ner_tagger(self):
        # http://stackoverflow.com/questions/32652725/importerror-cannot-import-name-stanfordnertagger-in-nltk
        stanford_ner_tagger = getattr(self.thread_local,'stanford_ner_tagger',None)
        if stanford_ner_tagger ==None:
            stanford_ner_tagger = StanfordNERTagger(self.stanford_ner_model, self.stanford_jar)
            self.thread_local.stanford_ner_tagger=stanford_ner_tagger
        return stanford_ner_tagger


    def perform_ner_extraction(self,text):
        # word_tokens = word_tokenize(text)
        word_tokens = text.split()
        tag_class = {'PERSON':'_class_name', 'LOCATION':'_class_location', 'ORGANIZATION':'_class_organization'}
        tags = self.get_stanford_ner_tagger().tag(word_tokens)
        replaced_words = [ tag_class.get(ner,token) for token,ner in tags]
        # detokenizer = MosesDetokenizer()
        # out = detokenizer.detokenize(replaced_words, return_str=True)
        out = ' '.join(replaced_words)
        print_log_if_diff(text,out)
        return out

    def handle_html_encoding(self,text):
        out = self.html_encoding_regex.sub(u' ',text)
        return out

    def handle_emails(self,text):
        out = self.email_regex.sub(' _class_email ', text)
        print_log_if_diff(text,out)
        return out

    def handle_urls(self,text):
        out = self.url_regex.sub(' _class_url ',text)
        print_log_if_diff(text,out)
        return out

    def handle_phone(self,text):
        out = text
        for phone_regex in self.phone_number_regexes:
            out = phone_regex.sub(u' _class_phone_number ',out)
        print_log_if_diff(text,out)
        return out

    def handle_masked_entities(self,text):
        out = self.masked_entity_regex.sub("_class_masked_entity",text)
        print_log_if_diff(text,out)
        return out

    def handle_question_mark(self,text):
        out = re.sub(ur'\?'," _class_question ",text)
        print_log_if_diff(text,out)
        return out

    def handle_numbers(self,text):
        out = text
        for number_regex in self.number_regexes:
            out = number_regex.sub('_class_number',out)
        print_log_if_diff(text,out)
        return out

    def handle_words_with_numbers(self,text):
        # the function handle_words_with_numbers would generally be only useful at the beginning of a project
        #this is kept to identify cases where users give details like account number & all. But there could be spelling mistakes where user may not put a space between word & number
        # Eg:- abc123abc , abc_123, abc-123 etc
        #TODO exclude words starting with _class_
        out = self.special_word_regex.sub('_class_special_word',text)
        print_log_if_diff(text,out)
        return out


    def handle_name_heuristics(self,text):
        #These regexes rely on capital cases letters, so don't convert all words to lowercase before this operation
        # name_regexes = [self.name1,self.name2,self.name3,self.name4,self.name5,self.name6,self.name7,self.name8,self.name9]
        # name_regexes = [self.name1,self.name2,self.name3,self.name4,self.name5,self.name6,self.name8,self.name9]
        name_regexes = [self.name1,self.name2,self.name3]
        out = text
        for no,regex in enumerate(name_regexes):
            intermediate = regex.sub(ur'\1 _class_name ',out)
            # self.name_entity_file.write()
            print_log_if_diff(out,intermediate,u'name heuristics step no {}'.format(no))
            out=intermediate

        out = self.remove_additional_space(out)
        print_log_if_diff(text,out)
        return out

    def handle_date(self,text):
        ## Replacing dates
        out=text
        # for date_regex in self.ill_formed_dates:
            # out = date_regex.sub('_class_date',out)
        for date_regex in self.dates_regex:
            out = date_regex.sub('_class_date', out)
        for masked_date_regex in self.masked_dates:
            out = date_regex.sub('_class_date',out)
        out = self.days_regex.sub('_class_date', out)

        print_log_if_diff(text,out)
        return out

    def handle_time(self,text):
        out = self.time.sub('_class_time',text)
        print_log_if_diff(text,out)
        return out

    def handle_currency(self,text):
        out = text
        for currency_amount in self.currency_amounts:
            # there isn't a space between _class_number & _class_currency, as in web2nl model there can't be a space in replacement word for word class replacement
            # added space for speech data replacement
            out = currency_amount.sub(' _class_number _class_currency ', out)
        out = self.currency_regex.sub('_class_currency',out)
        print_log_if_diff(text,out)
        return out


    def handle_masked_account_model_numbers(self,text):
        out = self.masked_account_numbers.sub(' _class_masked_acc_or_model_number ', text)
        print_log_if_diff(text,out)
        return out

    def handle_radio_id(self,text):
        out = re.sub(ur"\b(?=[a-z]{0,7}[0-9]{1,8})([a-zA-Z0-9]{8})\b","_class_radio_id",text,re.I)
        print_log_if_diff(text,out)
        return out

    def handle_esn(self,text):
        out = re.sub(ur"\b[OoSs0-9]{12}\b","_class_esn",text,re.I)
        print_log_if_diff(text,out)
        return out

    def handle_percentage(self,text):
        out = text
        for percentage in self.percentages:
            out = percentage.sub('class_percentage',out)
        print_log_if_diff(text,out)
        return out

    def handle_apostrophes(self,text):
        ## removing single quotes if they aren't used in prepositions
        # out = re.sub(ur"\'[^a-zA-Z]|[^a-zA-Z]\'|'$|^'", ' ', text)
        out = self.apostrophe_preposition.sub(' ', text)
        print_log_if_diff(text,out)
        return out

    def handle_apostrophe_words_additional(self,text):
        out = special_apostrophe_replace(text)
        out = self.handle_apostrophes(out)
        print_log_if_diff(text,out)
        text = out
        with open(os.path.join(self.output_dir,'suggested_word_expansions.txt'),'a') as word_exp:
            for word in text.split():
                if "'" in word:
                    word_exp.write(word+'\t'+word.split("'")[0]+'\n')
        ##TODO HACK. Replacing cases ending with 's with is
        out = re.sub(ur"'s\b"," is",text)
        print_log_if_diff(text,out)
        return out

    def remove_additional_space(self,text):
        text = self.replace_non_breaking_space(text)
        out = self.space_characters.sub(' ', text).strip()
        print_log_if_diff(text,out)
        return out

    def replace_non_breaking_space(self,text):
        out = self.non_breaking_space.sub(' ',text)
        print_log_if_diff(text,out)
        return out

class Normalizer:
    def __init__(self,config):
        self.compile_regexes()

    def compile_regexes(self):
        print('hi')

class SpeechNormalizer:
    def __init__(self,config):
        self.compile_regexes()


    def compile_regexes(self):
        ## Regex to handle cutting-out
        self.cutting_out=re.compile(ur'([^\s]*)-\s\(([^\s]*)\)-([^\s]*)',flags=re.IGNORECASE)

        ## Regular Expressions for cleaning a transcription
        ## Match acoustic quality, anything within a square bracket for eg [side_speech], [noise] etc.
        #acoustic_quality_indication = re.compile(ur'\[.*?\]')
        # This line replaces only the <[tag> . The closing bracket has to be replaced elsewhere.
        self.acoustic_quality_indication_1 = re.compile(ur'(\[)(other_language|speech_in_noise|noise|side_speech|echo_prompt|echo_speech|other_language)(\s*)',flags=re.IGNORECASE)
        self.acoustic_quality_indication_2 = re.compile(ur'(other_language|speech_in_noise|noise|side_speech|echo_prompt|echo_speech|other_language)(\s*)(\])',flags=re.IGNORECASE)
        self.acoustic_quality_indication_3 = re.compile(ur'(\[)(.*?)(other_language|speech_in_noise|noise|side_speech|echo_prompt|echo_speech|other_language)(.*?)',flags=re.IGNORECASE)
        self.square_brackets_second_term = re.compile(ur'\[(other_language|speech_in_noise|noise|side_speech|echo_prompt|echo_speech|other_language)\]',flags=re.IGNORECASE)
        #square_brackets_first_term = re.compile(ur'\[([a-zA-Z0-9\'-]*)\s(.*)')
        #acoustic_quality_indication_2 = re.compile(ur'(\[)(speech_in_noise(^\s)*|noise(^\s)*|side_speech(^\s)*|echo_prompt(^\s)*|echo_speech(^\s)*|other_language(^\s)*)*(?:(speech_in_noise(^\s)*|noise(^\s)*|side_speech(^\s)*|echo_prompt(^\s)*|echo_speech(^\s)*|other_language(^\s)*))')
        #acoustic_quality_indication_3 = re.compile(ur'((speech_in_noise(^\s)*|noise(^\s)*|side_speech(^\s)*|echo_prompt(^\s)*|echo_speech(^\s)*|other_language(^\s)*))(?:\])')

        ## Match word fragments, such as -aymnent, paymen-, paym-(()), paymen-()
        #frag_bracketted_wrds = [ re.compile(ur'[^\s]*-(?:\s|$)',flags=re.IGNORECASE),
        #                        re.compile(ur'(?:\s|^)-[^\s]*',flags=re.IGNORECASE),
        #                        re.compile(ur'[^\s]*-\(\(\)\)(?:\s|$)',flags=re.IGNORECASE),
        #                        re.compile(ur'[^\s]*-\(\)(?:\s|$)',flags=re.IGNORECASE)]

        ## Match word fragments, such as -aymnent, paymen-, paym-(()), paymen-(), (()) , () , every case with ()
        ## updated this to exclude date cases for chat
        self.frag_bracketted_wrds = [
                                #for cases like paymen-
                                re.compile(ur'[a-zA-Z]+-(?:\s|$)',flags=re.IGNORECASE),
                                #for casese like -ayment
                                re.compile(ur'(?:\s|^)-[a-zA-Z]+',flags=re.IGNORECASE),
                                #for cases like paym-(())
                                re.compile(ur'[a-zA-Z]+-\(\(\)\)(?:\s|$)',flags=re.IGNORECASE),
                                #for cases like paym-()
                                re.compile(ur'[a-zA-Z]+-\(\)(?:\s|$)',flags=re.IGNORECASE),
                                #for cases like (()) or () or even cases with non matching paranthesis also. For all cases with atleast one opening & closing paranthesis
                                re.compile(ur'[\(]{1,2}[\)]{1,2}',flags=re.IGNORECASE)
                                ]

        ## A regex, just for checking whether the utterance has any special character occurs
        self.concatenated = re.compile(ur'\[.*?\]|\*|\(.*?\)|~|\*|\-|\?|\s{2,}',flags=re.IGNORECASE)

        ## Match special character which form valid words, such as pay-(ment)
        #substitutions = {'~':'', ')':'', '(':'', '-':'', '*':'', '?': '' }
        substitutions = {'~':'', '*':'', '?': '' }
        # global special_characters
        self.special_characters = re.compile('|'.join(map(re.escape, substitutions)),flags=re.IGNORECASE)

        # global empty_parans_substitutions
        self.empty_parans_substitutions = re.compile(ur'(\(\))(-[^ ]*)',flags=re.IGNORECASE)
        # global truncated_parans_substitutions
        self.truncated_parans_substitutions = re.compile(ur'(\()([a-zA-Z]*)(\))-([^ ]*)',flags=re.IGNORECASE)
        #for chat this can be done only at the end, as some cases can have paranthesis & hyphen-
        self.others_substitutions = re.compile(ur'(\(|\)|-)',flags=re.IGNORECASE)

if __name__=='__main__':
    start_time = time.time()
##    if len(sys.argv)!=2:
##        print 'Usage: python prepare_dataset.py <config_file>\n'
##        sys.exit(1)
    sys.argv=['StandardDataNormalizer.py','StandardDataNormalizer_chat-Config.cfg']
    config_file_path=sys.argv[1]
    config = ConfigParser.ConfigParser()
    config.read(config_file_path)
    custom_encoding=config.get('params','encoding')
    grxml_lang= config.get('params','grxml_lang')
    print "Set mode to DEBUG (lines 161-162) for step by step logs, else set to ERROR to read only error messages."
    if config.get('params','debug_mode').lower()=='true':
        print "setting debug logs"
        logging.basicConfig(stream=sys.stdout, level = logging.DEBUG)
    else:
        logging.basicConfig(stream=sys.stderr, level = logging.ERROR)

    print sys.argv[1]
    ## Check if the file exists
    if not os.path.isfile(sys.argv[1]):
        raise Exception(sys.argv[1]+' is not a file!')
    if not os.path.isdir(config.get('params', 'output_dir')):
        os.makedirs(config.get('params', 'output_dir'))

    if config.get('params', 'replace_word_classes_in_data').lower()=="true":
        ## Read word classes
        word_class_replacement = WordClassReplacement(config.get('params', 'word_classes_file'))
        generateGRXMLs(lang=grxml_lang)
        ##generate arpax
        generate_arpax(lang=grxml_lang)

    is_perform_chat_normalization = config.get('chat','is_perform_chat_normalization').lower()=='true'
    chat_normalizer = ChatNormalizer(config)
    speech_normalizer = SpeechNormalizer(config)

    num_threads=int(config.get('params','no_of_parallel_executions'))
    pool = ThreadPool(num_threads)
    normalizeDataset()
    print 'please check the output file for entities - _class_special_word & _class_masked_entity . These are generic entities, so might have to find the exact pattern & break it down'
    end_time=time.time()
    print "Total execution time : " + str(end_time-start_time)

    #truncated_Inaudible = re.compile(ur'([a-zA-Z]*-?\(\(.*\)\))-*(-?[a-zA-Z]*-?\(\(.*\)\))*')
    #-?[a-zA-Z]*
    ##Below line commented on 24th Dec, Sruti.
    ##truncated_Inaudible= re.compile(ur"([a-zA-Z\']*-*)(\(\([a-zA-Z0-9]*\)\))(-*[a-zA-Z\']*)") -- This should've been as below line anyway!
    ##truncated_Inaudible = re.compile(ur"([a-zA-Z]*-?\(\([a-zA-Z0-9]*\)\))-*(-?[a-zA-Z]*-?\(\([a-zA-Z0-9]*\)\))*")

    ##Added on 24th Dec, 2015, for Ebay. - Unused after the legit word check got added.
    #truncated_Inaudible_WithoutLegit_Word_Check=re.compile(ur"([a-zA-Z]*-?\(\([a-zA-Z0-9]*\)\))(-?[a-zA-Z]*)")

    #truncated_Inaudible= re.compile(ur'((^\s)*-*)\(\(.*\)\)(-*(^\s)*)')

    ## Hack for space character matching
