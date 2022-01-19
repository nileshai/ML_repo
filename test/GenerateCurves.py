'''
Created on Apr 14, 2015

@author: anmol.walia, modified by alicia.jin on Sep 1, 2016

@run example:
    python GenerateCurves.py -c <ClassificationOutput.csv> -i <Intent_thresholds_list.txt>  -o 'ood_intent'
    python GenerateCurves.py -c <ClassificationOutput.csv> -i <Intent_thresholds_list.txt>  -o ''
    python GenerateCurves.py -c <ClassificationOutput.csv> -i <Intent_thresholds_list.txt>  -o 'ood_intent1','ood_intent2'
@logic: in readme.txt


'''
import csv, os, collections, decimal
import argparse
parser = argparse.ArgumentParser(description='choosing reco threshold, intent threshold')
parser.add_argument('-c', '--classificationOutput', help = 'Input file: ClassificationOutput.csv')
parser.add_argument('-i', '--intent_thred', help = "Input file: Intent thresholds list txt")
parser.add_argument('-o', '--ood_intent', help = "Input string: ood Intent. If no ood_intent, pass ''. If multiple, sep = ',', no space")
args = parser.parse_args()

class utterance:
    def __init__(self,id,text,orig_intent,classified_intent,conf):
        self.id=id
        self.text=text
        self.orig_intent=orig_intent
        self.classified_intent=classified_intent
        self.classification_confidence_score=float(conf)
        self.reco_score=0.0

def getCurves(utt_list, output_directory):
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        for intent, utts in utt_list.iteritems():
            writer=csv.writer(open(os.path.join(output_directory, 'ROC_curve_'+intent+'.csv'),'wb'))
            writer.writerow(['Threshold','CA','CA-rate','FA','FA-rate','FR','FR-rate'])
            for i in range(0,100):
                thresh=0.01*i
                ca=0
                fa=0
                fr=0
                for utt in utts:
                    #print intent,utt.classification_confidence_score, thresh,utt.classification_confidence_score>thresh
                    if utt.classification_confidence_score>thresh:
                        if utt.orig_intent==utt.classified_intent:ca+=1
                        else:fa+=1
                    else:fr+=1
                total=float(ca+fa+fr)
                writer.writerow([thresh,ca,str(round(decimal.Decimal((float(ca)/total)*100),2))+'%',
                                fa,str(round(decimal.Decimal((float(fa)/total)*100),2))+'%',
                                fr,str(round(decimal.Decimal((float(fr)/total)*100),2))+'%'])


def getRecoCurves(utt_list, output_directory, ood_intents):
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        writer=csv.writer(open(os.path.join(output_directory, 'Reco_curves.csv'),'wb'))
        #writer=csv.writer(open(os.path.join(output_directory, args.output_recoFile),'wb'))
        writer.writerow(['reco_threshold','ood_CR','ood_CR_rate(/all)', 'ood_FA','ood_FA_rate(/all)', 'id_CA','id_CA_rate', 'id_FA', 'id_FA_rate',
                         'id_FR_correctClassified','id_FR_correctClassified_rate', 'id_FR_incorrectClassified', 'id_FR_incorrectClassified_rate', 'id_FR', 'id_FR_rate'])

        for i in xrange(0,100):
            thresh=0.01*i
            ood_cr, ood_fa = 0, 0
            id_ca, id_fa, id_fr_corrClas, id_fr_incorrClas, id_fr = 0, 0, 0, 0, 0

            for intent, utts in utt_list.iteritems():
                for utt in utts:
                    ## Handling no-inputs and no-matches, double check
                    if utt.text in ['NO INPUT', 'NO MATCH']:
                        if utt.orig_intent in ood_intents:ood_cr+=1
                        else:id_fr_incorrClas+=1
                        #continue
                    else:
                        the_int = utt.classified_intent.upper()
                        if utt.orig_intent in ood_intents:
                            if utt.reco_score < thresh: ood_cr += 1
                            else:
                                if utt.classified_intent != utt.orig_intent and utt.classification_confidence_score >= intent_thres[the_int]: ood_fa += 1
                                else : ood_cr += 1

                        else:
                            if utt.reco_score >= thresh:
                                if utt.classified_intent == utt.orig_intent and utt.classification_confidence_score >= intent_thres[the_int]: id_ca += 1
                                elif utt.classified_intent != utt.orig_intent and utt.classification_confidence_score >= intent_thres[the_int]: id_fa += 1
                                elif utt.classified_intent == utt.orig_intent and utt.classification_confidence_score < intent_thres[the_int]: id_fr_corrClas += 1
                                else: id_fr_incorrClas += 1
                                ## if utt.classified_intent != utt.orig_intent and utt.classification_confidence_score < intent_thres[the_int]: id_fr_incorrClas += 1

                            else:
                                if utt.classified_intent == utt.orig_intent: id_fr_corrClas += 1
                                else: id_fr_incorrClas += 1
                total = float(ood_cr + ood_fa + id_ca + id_fa + id_fr_corrClas + id_fr_incorrClas)
                id_fr = float(id_fr_corrClas+id_fr_incorrClas)
            writer.writerow([thresh, ood_cr, str(round(decimal.Decimal((float(ood_cr)/total)*100),2))+'%',
                             ood_fa, str(round(decimal.Decimal((float(ood_fa)/total)*100),2))+'%',
                             id_ca, str(round(decimal.Decimal((float(id_ca)/total)*100),2))+'%',
                             id_fa, str(round(decimal.Decimal((float(id_fa)/total)*100),2))+'%',
                             id_fr_corrClas, str(round(decimal.Decimal((float(id_fr_corrClas)/total)*100),2))+'%',
                             id_fr_incorrClas, str(round(decimal.Decimal((float(id_fr_incorrClas)/total)*100),2))+'%',
                             id_fr, str(round(decimal.Decimal((float(id_fr)/total)*100),2))+'%'])


if __name__ == '__main__':

    utterances=collections.defaultdict(lambda:[])
    header_colmns={}
    row_ctr=0
    is_generate_reco_curve = True
    intent_list=set()
    for row in csv.reader(open(args.classificationOutput,'rb')):
        # row is a list
        if row_ctr==0:
            col_ctr=0
            for x in row:
                header_colmns[x]=col_ctr
                col_ctr+=1
            row_ctr+=1
            #If the user gives classification output from just the SSI experiment, then the assumtion is that the user only want to generate ROC curves & the reco curves will not be generated
            #So this check is to identify whether Classification output is from SLM + SSI expt or just the SSI experiment
            is_generate_reco_curve = 'Raw Recognition' in header_colmns
            continue
        ## The raw recognition column is required for generating reco-curves. This is not required for generating ROC curves. for the case with just SSI classification output taking the utterance column instead
        transcription = row[header_colmns['Raw Recognition']] if is_generate_reco_curve else row[header_colmns['Utterance']]
        ##Output generated by SLM +SSI experiment & SSI experiment have different header names, eventhough both of them are actually the same
        original_intent = row[header_colmns['Manually Tagged Intent']] if is_generate_reco_curve else row[header_colmns['Original Intent']]
        intent_list.add(original_intent.upper())
        classified_intent = row[header_colmns['Classified Intent 1']]
        utt = utterance(row[header_colmns['Id']],
                        transcription,
                        original_intent,
                        classified_intent,
                        row[header_colmns['Classification Score 1']] if row[header_colmns['Classification Score 1']]!="" else 0.0)

        if is_generate_reco_curve:
            utt.reco_score = float(row[header_colmns['Recognition confidence']]) if row[header_colmns['Recognition confidence']]!="" else 0.0
        utterances[classified_intent].append(utt)

    #### input intent classifier threshold or use the default 0 ones.
    ## intent_thres = dict.fromkeys([x.upper() for x in utterances.keys()],0.00)
    intent_thres = {}
    ood_intent = args.ood_intent.split(',')
    print 'ood_intents ' + str(ood_intent)
    if ood_intent != ['']:
        for the_int in ood_intent:
            #setting the threshold as 0.0 for out of domain intents
            print 'setting the threshold as 0.0 for out of domain intent'
            intent_thres[the_int.upper()] = 0.00
    else:
        print 'out of domain intent is not specified, taking NONE_RU as the default out of domain intent'
        intent_thres = {'NONE_RU': 0.00}

    if(args.intent_thred and os.path.exists(args.intent_thred)):
        print 'taking threshold values from specified threshold file- ' + args.intent_thred
        with open(args.intent_thred) as f:
            next(f)
            for line in f:
                tmp = line.split(',')[:2]
                intent_thres[tmp[0].upper()] = float(tmp[1])
        intent_missing = intent_list.difference(intent_thres.keys())
        if(len(intent_missing)>0):
            print 'threshold for the following intents are missing from the intent threshold file ' + str(intent_missing)
        intent_extra_in_file = set(intent_thres.keys()).difference(intent_list)
        if(len(intent_extra_in_file)>0):
            print 'intent specified in thresholds file not present in classification output- ' + str(intent_extra_in_file)
    else:
        print 'Assuming the classification output file specified have all the intents for the model & taking default value of 0.0 as threshold for all these intents'
        intent_thres=dict.fromkeys(intent_list,0.0)

    if (is_generate_reco_curve):
        print 'generating reco curves'
        getRecoCurves(utterances, os.getcwd()+'/curves', ood_intent)
    else:
        print 'Skipping generation of reco curves as only SSI classification output was specified. Specify SLM + SSI classification output to get reco curves'
    getCurves(utterances, os.getcwd()+'/curves')


