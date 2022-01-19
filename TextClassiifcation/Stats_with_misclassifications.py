import collections, csv, glob, os, numpy, sys, ConfigParser, time
from shutil import copyfile

def calc_cost_sensitive_stats(cost_matrix, in_file, out_file):
    
    intents=collections.defaultdict(lambda:{"tp":0.0,"fp":0.0,"fn":0.0})
    
    for i in open(in_file, 'r'):
        row=i.strip().split(',')
        if row[2]=="PredictedIntent":continue
        elif row[0]==row[1]=="":
            classified_intents=dict(enumerate(row))            
            continue
                
        for i in range(len(row[2:])):
            if row[1]==classified_intents[i+2]:intents[row[1]]['tp']+=float(row[i+2])
            else:                
                if not (cost_matrix.has_key(classified_intents[i+2]) and cost_matrix[classified_intents[i+2]].has_key(row[1])):                    
                    intents[classified_intents[i+2]]['fp']+=float(row[i+2])                    
                    intents[row[1]]['fn']+=float(row[i+2])                    
                else:                    
                    intents[classified_intents[i+2]]['fp']+=float(row[i+2])*cost_matrix[classified_intents[i+2]][row[1]]
                    #intents[classified_intents[i+2]]['tp']+=float(row[i+2])*(1.0 - misclassification_cost[classified_intents[i+2]][row[1]])
                    intents[row[1]]['fn']+=float(row[i+2])*cost_matrix[classified_intents[i+2]][row[1]]
                    intents[row[1]]['tp']+=float(row[i+2])*(1.0 - cost_matrix[classified_intents[i+2]][row[1]])
    
    tot_utts=sum([j['tp']+j['fn'] for i,j in intents.iteritems()])
                    
    out_stats_file = csv.DictWriter(open(out_file, 'wb'),fieldnames=['Intent','tp','fp','fn','precision','recall','f-score','intent-frequency'])
    out_stats_file.writeheader()
    
    for i,j in intents.iteritems():
        if j['tp']==0:j['precision']=j['recall']=j['f-score']=0.0
        else:
            j['precision']=round(j['tp']/(j['tp']+j['fp']),4)
            j['recall']=round(j['tp']/(j['tp']+j['fn']),4)        
            j['f-score']=round(2.0*j['precision']*j['recall']/(j['precision']+j['recall']), 4)
        j['intent-frequency']=round(((j['tp']+j['fn'])/tot_utts)*100,4)
        row= {'Intent':i}
        row.update(j)                
        out_stats_file.writerow(row)
    
    return intents 
    
if __name__ == '__main__':
    
    if len(sys.argv)!=2:
        print 'Usage: python Stats_with_misclassifications.py <config_file>'
        sys.exit()
        
    config = ConfigParser.ConfigParser()
    config.readfp(open(sys.argv[1]))    
    
    if not os.path.exists(config.get('params','output_folder')):os.makedirs(config.get('params','output_folder'))
    copyfile(sys.argv[1], os.path.join(config.get('params','output_folder'),'config_'+time.strftime("%Y%m%d%H%M%S")))
    copyfile(config.get('params','misclassification_cost_file'), os.path.join(config.get('params','output_folder'),'misclassification_cost_'+time.strftime("%Y%m%d%H%M%S")+'.csv'))
        
    cost_matrix=collections.defaultdict(lambda:{})
    for i in csv.DictReader( open(config.get('params','misclassification_cost_file'), 'rb') ):        
        cost_matrix[i['classified-intent']][i['orig-intent']]=float(i['mis-classification-cost'])    
    
    fold_confusion_matrix_files = glob.glob(os.path.join(config.get('params','workbench_folder_path'),'ConfusionMatrix_*.csv'))+glob.glob(os.path.join(config.get('params','workbench_folder_path'),'Fold_?'+os.path.sep+'ConfusionMatrix_*.csv'))
    
    stats=[]
    for i in fold_confusion_matrix_files:
        stats.append(calc_cost_sensitive_stats(cost_matrix,i,os.path.join(config.get('params','output_folder'),'Mod_stats_'+i.split('_')[-1].split('.')[0]+'.csv')))
    
    cum_stats_file = csv.DictWriter(open(os.path.join(config.get('params','output_folder'),'Mod_stats_cumulative.csv'), 'wb'),fieldnames=['Intent','precision','precision-std','recall','recall-std','f-score','f-score-std'])
    cum_stats_file.writeheader()
    for i in stats[0].keys():
        precision = numpy.array([ stats[j].get(i)['precision'] for j in range(len(stats))])
        recall = numpy.array([ stats[j].get(i)['recall'] for j in range(len(stats))])
        f_score = numpy.array([ stats[j].get(i)['f-score'] for j in range(len(stats))])
        cum_stats_file.writerow({'Intent':i,'precision':round(numpy.mean(precision, axis=0),4),'precision-std':round(numpy.std(precision,axis=0),4),
                                                                    'recall':round(numpy.mean(recall, axis=0),4),'recall-std':round(numpy.std(recall,axis=0),4),
                                                                    'f-score':round(numpy.mean(f_score, axis=0),4),'f-score-std':round(numpy.std(f_score,axis=0),4)})
        
    weighted_f_score=numpy.array([sum([(j['f-score']*j['intent-frequency'])/100 for i,j in x.iteritems()]) for x in stats])
    print 'Foldwise weighted F-score ',weighted_f_score
    print 'Average weighted f-score: ', round(numpy.mean(weighted_f_score, axis=0),4), ' +-(',round(numpy.std(weighted_f_score, axis=0),4),')' 
    
#     print misclassification_cost
#     for i in open(r'C:\Experiments\Ebay\word_class_v1\eBay_UK_First30K_DataMaster_20160215a\normalized_02172016\Granular_Tags\Stats_1.csv', 'r'):
#         row=i.split(',')
#         if not intents.has_key(row[0]):
#             print row
#             continue
#     
#         if not ((int(row[1])==intents[row[0]]["tp"]) and (int(row[2])==intents[row[0]]["fp"]) and (int(row[3])==intents[row[0]]["fn"])):
#             print 'stats dont match ',row
#             p=intents[row[0]]['tp']/(intents[row[0]]['tp']+intents[row[0]]['fp'])
#             r=intents[row[0]]['tp']/(intents[row[0]]['tp']+intents[row[0]]['fn'])
#             print intents[row[0]],p,r,2.0*p*r/(p+r)
#             print int(row[1])+int(row[2])+int(row[3]),intents[row[0]]['tp']+intents[row[0]]['fp']+intents[row[0]]['fn']
#             print int(row[1])+int(row[3]),intents[row[0]]['tp']+intents[row[0]]['fn']
#             #print int(row[1])==intents[row[0]]["tp"]
#             #print int(row[2])==intents[row[0]]["fp"],int(row[2]),intents[row[0]]["fp"]
#             #print int(row[3])==intents[row[0]]["fn"]
        
    #for i,j in intents.iteritems():
    #    print i,j