import collections, math, argparse

if __name__ == '__main__':
    ## Parse input arguments
    parser = argparse.ArgumentParser(description='Create dataset for with specified number of utterances for each intent.')
    parser.add_argument("-i", dest="inp_data", required=True, help="Input dataset", metavar="Input-dataset")
    parser.add_argument("-o", dest="out_data", required=True, help="Output dataset", metavar="Output-dataset")
    parser.add_argument("-n", dest="total_utts_per_intent", help="Number of utterances per intent",type=int, required=True, metavar="Total-utterances-per-intent")
    args = parser.parse_args()
    args = parser.parse_args()
    
    #tot_utts = args.total_utts_per_intent
    dataset = collections.defaultdict(lambda:collections.defaultdict(lambda:0))
    
    ##Read the input file 
    for i in open(args.inp_data,'r'):
        parts=i.split('\t')
        dataset[parts[2]][parts[1].strip()]+=1
    
    ## Adjust the utterance frequencies in each intent according to the distribution of the dataset
    for intent, utts in dataset.iteritems():
        freq_sorted_utts = sorted(utts.items(), key=lambda x:x[1], reverse=True)
        
        ## Number of unique utterances exceed the number of utts required for the intent
        if args.total_utts_per_intent<len(utts):
            q=collections.defaultdict(int)
            for i in range(args.total_utts_per_intent):
                q[freq_sorted_utts[i][0]]+=1
            dataset[intent]=q
            continue
        
        ## Adjust utterance frequencies by maintaining proportions
        tot = sum(utts.values())       
        for utt, freq in utts.iteritems():
            utts[utt] = math.ceil((float(freq)/tot)*args.total_utts_per_intent) if (float(freq)/tot)*args.total_utts_per_intent<1.0 else math.floor((float(freq)/tot)*args.total_utts_per_intent)          
        
        ## Adjust rounding up/down of proportions       
        utt_diff = sum(utts.values()) - args.total_utts_per_intent
        if utt_diff>0:     
            while utt_diff>0:
                for i in freq_sorted_utts:
                    if utt_diff==0:break
                    if utts[i[0]]>1.0:
                        utts[i[0]]-=1
                        utt_diff-=1
        else:
            while utt_diff<0:
                for i in reversed(freq_sorted_utts):
                    if utt_diff==0:break
                    utts[i[0]]+=1
                    utt_diff+=1
    
    ## Write the output
    o = open(args.out_data, 'w')
    utt_ctr=1
    for intent, utts in dataset.iteritems():
        for utt, freq in sorted(utts.items(), key=lambda x:x[1]):
            for i in range(int(freq)):
                o.write('utt_'+str(utt_ctr)+'\t'+utt+'\t'+intent+'\t'+intent+'_1\n')
                utt_ctr+=1