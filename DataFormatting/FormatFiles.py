'''
Created on Feb 13, 2014

@author: anmol.walia
'''
import os, sys, csv

## Convert CSV file to text file
def CSVtoTXT(input_file, output_file):
        
    out_file = open(output_file, 'w')
    data = csv.reader(open(input_file))
    
    for row in data:
        #out_file.write('\t'.join(row)+'\n')
        out_file.write(row[0]+'\t'+row[3]+'\t'+row[6]+'\t'+row[6]+'_1\n')
    out_file.close()

def getWordClassNormalizedData(reference_file, raw_transcription_file, output_file):
    
    complete_dataset={}
    
    data = csv.reader(open(reference_file))
    for row in data:
        complete_dataset[row[0]]=row[2]+'\t'+row[3]+'\t'+row[3]+'_1'
    
    raw_file=open(raw_transcription_file, 'r')
    out = open(output_file, 'w')
    for row in raw_file:
        parts=row.split('\t')
        
        if parts[0] in complete_dataset:
            out.write(parts[0]+'\t'+complete_dataset[parts[0]]+'\n')
        else:
            out.write(row)
    out.close()
    raw_file.close()


def findUniqUtts(input_file_array):
    uniq_utts = set([])
    for file in input_file_array:
        file_data = open(file, 'r')
        for line in file_data:
            parts = line.split('\t')
            uniq_utts.add(parts[1])
    print ('total uniq utts: '+str(len(uniq_utts)))
    
    uniq_utt_file = open('E:\\Data\\CapOne\\CapOne_NLData_TagMaster_20131106b\\DatasetDivision_20131106b\\Raw\\40_Intents\\Fold1+HeldOutTS_UniqueUtts', 'w')
    ctr=0
    for utt in uniq_utts:
        if (utt==''):
            continue
        ctr=ctr+1
        uniq_utt_file.write(str(ctr)+'\t'+utt+'\n')
    uniq_utt_file.close()

def findRawUtt(reference_file, WC_Normalized_File, outputFile_1):
    complete_dataset={}
    data = csv.reader(open(reference_file))
    for row in data:
        complete_dataset[row[0]]=row[1]
    
    
    out = open(outputFile_1, 'w')
    WC_normalized_file=open(WC_Normalized_File, 'r')
    
    for line in WC_normalized_file:
        parts = line.split('\t')
        out.write(parts[0]+'\t'+complete_dataset[parts[0]]+'\t'+parts[2]+'\t'+parts[3])
    
    out.close()
    WC_normalized_file.close()

'''
    Replace new word classes in existing folds and held out test set
'''
def replaceWordClassesInFolds(reference_data_file, fold_directory):
    
    complete_dataset={}
    
    ## Reading WC normalized forms and intents from reference file
    data = csv.reader(open(reference_data_file))
    for row in data:
        complete_dataset[row[0]]=[row[3],row[6]]
    
    for i in range(1,6):
        
        file_types = ['train', 'test']
        
        for f in file_types:
            getUtteranceFromRefFile(complete_dataset, fold_directory+f+'_'+str(i), fold_directory+f+'_'+str(i)+'_new')
     
    getUtteranceFromRefFile(complete_dataset, fold_directory+'HeldOutTestSet', fold_directory+'HeldOutTestSet_new')
    
def getUtteranceFromRefFile(reference_map, input_file, output_file):    
    input_file = open(input_file, 'r')
    output_file = open(output_file, 'w')
    for line in input_file:
        parts = line.split('\t')
        output_file.write(parts[0]+'\t'+reference_map[parts[0]][0]+'\t'+reference_map[parts[0]][1]+'\t'+reference_map[parts[0]][1]+'_1\n')
    input_file.close()
    output_file.close()

def formatTestFile(input_file, output_file):
        
    data= csv.reader(open( input_file, 'rb')) 
    out_file= csv.writer(open( output_file, 'wb'))
    row_ctr=0
    file_columns={}
    for line in data:
        
        if row_ctr==0:
            col_ctr=0
            for col in line:
                file_columns[col] = col_ctr
                col_ctr+=1
            row_ctr+=1
            out_file.writerow(line)
            continue
        
        if not '/' in line[file_columns['full_path']]:
            out_file.writerow(line)
            continue
        
        
        utt_id_parts=line[file_columns['full_path']].split('/')      
        utt_id=utt_id_parts[-2]+'_'+utt_id_parts[-1]
        
        out_file.writerow(line[:file_columns['full_path']]+[utt_id]+line[file_columns['confidence']:])

def createSLMData(input_file, output_file):
    
    in_file = open(input_file, 'r')
    out = open(output_file, 'w')

    for line in in_file:
        out.write(line.split('\t')[1]+'\n')
    
    in_file.close()
    out.close()
               
if __name__ == "__main__":
    #if len(sys.argv[1:])!=2:
    #    print "Usage: FormatFiles.py <grammar_url> <audio_file_url>"
    #    sys.exit()
    dir='E:\\Data\\CapOne\\Transcriptions\\C1-NLU_DataMaster_20140515d\\DatasetDivision\\First+SecondResponses+SyntheticData\\SLMData'
    #for i in range(1,6):
    #    CSVtoTXT(dir+'WordClassNormalised_Fold_'+str(i)+'.csv', dir+'test_'+str(i))
    
    for i in range(1,6):
        #getWordClassNormalizedData(dir+'WordClassNormalised_Complete.csv', dir+'train_'+str(i), dir+'train_word_class_normalized'+str(i))
        createSLMData(os.path.join(dir, 'train_'+str(i)), os.path.join(dir, 'SLM_train_'+str(i)))
    
    #findRawUtt('E:\\Data\\CapOne\\CapOne_NLData_TagMaster_20131106b\\CapOne_NLData_TagMaster_20131106b_First_RESPONSES.csv', 
    #           dir + 'HeldOutTestSet_WCNormalized', dir + 'HeldOutTestSet')
    
    #CSVtoTXT('E:\\Data\\CapOne\\CapOne_NLData_TagMaster_20131106b\\CapOne_NLData_TagMaster_20131106b_Second_RESPONSES.csv',
    #         'E:\\Data\\CapOne\\CapOne_NLData_TagMaster_20131106b\\DatasetDivision_20131106b\\Raw\\40_Intents\\SecondResponses')
    
    ##CSVtoTXT(dir+'CapOne_NLData_TagMaster_20131106b_WCNormalized_v2.csv', dir+'Complete_dataset')
    
    #replaceWordClassesInFolds('E:\\Data\\CapOne\\Transcriptions\\CapOne_NLData_TagMaster_20131106b\\CapOne_NLData_TagMaster_20131106b_WCNormalized_v2.csv', 
    #                          dir)
      
    
    #formatTestFile('E:\\Data\\CE_Reco_Test\\Feb19-DSG-Reviewed.csv', 'E:\\Data\\CE_Reco_Test\\Feb19-DSG-Reviewed_correct_path.csv')
    
    ##file_array = [dir+'test_1', dir+'HeldOutTestSet']
    ##findUniqUtts(file_array)
    