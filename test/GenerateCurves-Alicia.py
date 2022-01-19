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
            #writer=csv.writer(open(r'E:\Data\CapOne\Credit_tracker\20150401a_withResponses\Experiments\Subhankar\fixed_flattened\Unambiguous_CT\ROC_curve_'+intent+'.csv','wb'))
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

	    blah=0
            for intent, utts in utt_list.iteritems():
                for utt in utts:
		    blah+=1
                    ## Handling no-inputs and no-matches, double check
                    if utt.text in ['NO INPUT', 'NO MATCH']:
                        if utt.orig_intent in ood_intents:ood_cr+=1
                        else:id_fr_incorrClas+=1
                        #continue
                    else:
                        the_int_lower = utt.classified_intent.lower()
                        the_int_upper = utt.classified_intent.upper()
                        the_int = the_int_lower if intent_thres.has_key(the_int_lower) else the_int_upper
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
    print "Reading " + args.classificationOutput
    for row in csv.reader(open(args.classificationOutput,'rb')):
        # row is a list
        if row_ctr==0:
            col_ctr=0
            for x in row:
                header_colmns[x]=col_ctr
                col_ctr+=1
            row_ctr+=1
            continue
        if (header_colmns.has_key('Raw Recognition')==True):
            utt = utterance(row[header_colmns['Id']],
                        row[header_colmns['Raw Recognition']],
                        row[header_colmns['Manually Tagged Intent']],
                        row[header_colmns['Classified Intent 1']],
                        row[header_colmns['Classification Score 1']] if row[header_colmns['Classification Score 1']]!="" else 0.0)
        else:
            utt = utterance(row[header_colmns['Id']],

                        # row[header_colmns['Utterance']],
                        # row[header_colmns['Original Intent']],

                        ## Required for generating reco-curves
                        row[header_colmns['Utterance']],
                        row[header_colmns['Original Intent']],

                        row[header_colmns['Classified Intent 1']],
                        row[header_colmns['Classification Score 1']] if row[header_colmns['Classification Score 1']]!="" else 0.0)

       #utt.reco_score = float(row[header_colmns['Recognition confidence']]) if row[header_colmns['Recognition confidence']]!="" else 0.0
        utterances[row[header_colmns['Classified Intent 1']]].append(utt)

    #### input intent classifier threshold or use the default 0 ones.
    ## intent_thres = dict.fromkeys([x.upper() for x in utterances.keys()],0.00)
    intent_thres = {'NONE_RU': 0.00}  ## should check if intent_thred has all intents.
    print 'ood_intent'
    if args.ood_intent.split(',') != ['']:
        for the_int in args.ood_intent.split(','):
            intent_thres[the_int] = 0.00

    #intent_thres = {args.ood_intent : 0.00}  # 'NONE_RU'
    with open(args.intent_thred) as f:
        next(f)
        for line in f:
            tmp = line.split(',')[:2]
            intent_thres[tmp[0]] = float(tmp[1])

    ##########################################################
    ########## Specify Out-of-domain intents #################
    ##########################################################
    getRecoCurves(utterances, os.getcwd()+'/curves', args.ood_intent.split(','))
    getCurves(utterances, os.getcwd()+'/curves')

