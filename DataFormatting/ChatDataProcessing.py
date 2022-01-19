'''
Created on Jun 5, 2014

@author: anmol.walia
'''

import csv, re, os, sys

word_frequencies={}

def correctFormatting(input_csv, output_csv):
    
    data = csv.reader(open(input_csv, 'rb'))
    out_file = csv.writer(open(output_csv, 'wb'))
    row_ctr=0
    valid_typers=set(['customer','agent','system'])
    for row in data:
        if row_ctr==0:
            row_ctr+=1
            out_file.writerow(row)
        
        content=[]
        for i in len(row[1:]):
            if row[1:][i] in valid_typers:
                out_file.writerow([row[0]]+[' </S> '.join(content)]+row[1:][i:])
            content.append(row[1:][i])

def getNLfromChat(chat):
    
    NL_questions = ['may I assist you',
                    'can I help you',
                    'may I help you',
                    ]
        
    NL_content=[]
    chat_line_number=-1
    
    for chat_line in chat:
        chat_line_number+=1                
        if chat_line[1]=='agent' and any(x in chat_line[0] for x in NL_questions):
           
            for lines_following_NL_question in chat[chat_line_number+1:]:
                
                if lines_following_NL_question[1]=='customer':
                    
                    if isSentAcceptable(lines_following_NL_question[0]):
                        NL_content.append(lines_following_NL_question[0])
                else:
                    wordFreq(NL_content)
                    return NL_content
            break
        #elif chat_line[1]=='system':
        #    print         
    return []

## Function to reject chat text if more than 60% of it contains numbers (generally the case where user provides his details like SSN, postcode, cardnumber etc.)
## THIS IS A HEURISTIC APPROACH TO REJECT TEXT AND CAN BE SKIPPED
def isSentAcceptable(chat_line):
    without_spaces=re.sub(space_pattern, '', chat_line)
    num_letters=len([c for c in without_spaces if c.isalpha()])
        
    if num_letters<(0.6*len(without_spaces)) or len(chat_line.split())<=3:
        return False
    else: return True
    
## Function to parse chat transcript to retrieve the NL content           
def parseRawChats(input_file):
    
    data = csv.reader(open(input_file, 'rb'))
    accepted = csv.writer( open( os.path.join(output_dir, "accepted.csv"), 'wb' ) )
    
    col_header={}      
    
    row_cntr=0
    current_chat_id=''
    previous_chat_id=None
    chat=[]
    total_chats=0
    chats_with_NL=0
    for row in data:
        if row_cntr==0:
            col_ctr=0
            for col in row:
                col_header[col]=col_ctr
                col_ctr+=1
            row_cntr+=1
            continue
        
        if row[col_header['session_id']]!=current_chat_id:
            
            if previous_chat_id!=None:      
                previous_chat_id = current_chat_id
                total_chats+=1
                NL_content=getNLfromChat(chat)
                
                if len(NL_content)>0:
                    accepted.writerow([previous_chat_id,' <S> '.join(NL_content)])
                    chats_with_NL+=1  
                else:
                    writeChatsWithNoNL(chat, previous_chat_id)          
            else:
                previous_chat_id=row[col_header['session_id']]
            
            chat=[]
            current_chat_id = row[col_header['session_id']]
        
        chat.append((row[col_header['line_text']], row[col_header['who_typed']]))
    print 'total chats: '+str(total_chats)
    print 'chats with NL: '+str(chats_with_NL)
    
    word_frequency_file = csv.writer( open( os.path.join(output_dir, "freq.csv"), 'wb' ) )
    for word,freq in word_frequencies.iteritems():
        word_frequency_file.writerow([word,freq])
    
    
def wordFreq(text):
    words=[]
    for sent in text:
        words += sent.lower().split()
    
    for word in words:
        if word_frequencies.has_key(word):
            word_frequencies[word]+=1
        else:
            word_frequencies[word]=1

 
### Function for normalizing chat text. 
def normalize(text):
       
    ## Fixing ill-formed dates
    for ill_formed_date_regex in ill_formed_dates:
        text = ill_formed_date_regex.sub(r'\1 \2', text)
    
    ## Replacing dates    
    for date_regex in dates_regex:
        text = date_regex.sub('_class_DATE', text)
    
    text = days_regex.sub('_class_DAYS', text)   
    
    ## Replacing money amounts
    text = dollar_amount.sub('_class_DOLLAR_AMOUNT', text)
    
    ## replacing multiple punctuations
    text=multiple_puncts.sub(r'\1', text)

    return text
        
    
    
 
def writeChatsWithNoNL(chat, id):
    for chat_line in chat:
        chatsWithoutNL.writerow([id,chat_line[0],[chat_line[1]]])
    
        
if __name__ == '__main__':
    #correctFormatting('E:\\Data\\CapOne\\Chat_Data\\04_14_Core.csv', 'E:\\Data\\CapOne\\Chat_Data\\04_14_Core_correctly_formatted.csv')
    #sys.exit()
    
    months_without_word_boundaries=['january','february','march','april','may','june','july','august','september','october','november','december','jan','feb','mar','apr','jun','jul','aug','sep','sept','oct','nov','dec']
    months=[r'\bjanuary\b',r'\bfebruary\b',r'\bmarch\b',r'\bapril\b',r'\bjune\b',r'\bjuly\b',r'\baugust\b',r'\bseptember\b',r'\boctober\b',r'\bnovember\b',r'\bdecember\b',r'\bjan\b',r'\bfeb\b',r'\bmar\b',r'\bjun\b',r'\bjul\b',r'\baug\b',r'\bsep\b',r'\bsept\b',r'\boct\b',r'\bnov\b',r'\bdec\b']
    ambiguous_months=[r'\bapr\b',r'\bmay\b']
    days = [r'\bmonday\b',r'\btuesday\b',r'\bwednesday\b',r'\bthursday\b',r'\bfriday\b',r'\bsaturday\b',r'\bsunday\b',r'\bmon\b',r'\btue\b',r'\bwed\b', ]
           
    ## Dates     
    ill_formed_dates = [re.compile(r'('+'|'.join(months_without_word_boundaries)+')(\d{1,4}(?:nd|st|rd|th)?)', re.I),
                        re.compile(r'(\d{1,4}(?:nd|st|rd|th)?)('+'|'.join(months_without_word_boundaries)+')',re.I)]
    
    
    dates_regex = [re.compile(r'(\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?)'),
             ## Problematic dot sign....HACKY regex      
             re.compile(r'((?:'+'|'.join(months+ambiguous_months)+')\.? \d{1,2}(?:nd|th|rd|st)?(?:(?:,| of |, | )\d{2,4})?)', re.I),
             re.compile(r'(\d{1,2}(?:nd|th|rd|st)?(?:,| of |, | )(?:'+'|'.join(months+ambiguous_months)+')(?:(?:,| of |, | )\d{2,4})?)', re.I),
             re.compile(r'((?:'+'|'.join(months)+')(?:(?:,| of |, | )\d{2,4})?|(?:'+'|'.join(ambiguous_months)+')(?:(?:,| of |, | )\d{2,4}))',re.I)]
    
    dollar_amount = re.compile(r'(\$\s?\d*\,?\d*\.?\d{1,2}|\d*\,?\d*\.?\d{1,2}\s?\$)')
    
    days_regex = re.compile(r'('+'|'.join(days)+')',re.I)
    
    ## Substituting multiple punctuations (like ???, !!, $$$) with only one
    multiple_puncts=re.compile(r'(\.|\,|\?|\!|\*|\$)\1{1,}')
    
    space_pattern = re.compile(r'\s+')
    output_dir = 'E:\\tmp\\Chats'
       
    normalized= csv.writer(open(os.path.join(output_dir, 'Normalized.csv'), 'wb'))
    normalized.writerow(['id', 'original utterance', 'normalized utterance', 'normalized?'])
    for row in csv.reader(open(os.path.join(output_dir, 'accepted.csv'), 'rb')):
        nrmlzed=normalize(row[1])
        normalized.writerow(row[:2]+[nrmlzed, nrmlzed==row[1]])
    sys.exit()
    
    chatsWithoutNL= csv.writer(open(os.path.join(output_dir, 'ChatsWithoutNL.csv'), 'wb'))
    parseRawChats('E:\\Data\\CapOne\\Chat_Data\\10_04_to_21_04_Core.csv')

