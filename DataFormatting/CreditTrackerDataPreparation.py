import sets, csv, xlrd, collections, os,re, sys, random, operator, codecs, unicodedata

def strip_accents(s):
    return unicodedata.normalize('NFD', unicode(s)).encode('ascii','ignore')
    #return ''.join(c for c in unicodedata.normalize('NFD', unicode(s))
    #              if unicodedata.category(c) != 'Mn')

def getCreditTrackerUtts(inp_file, out_file):
    
    phrases = ['credit track','credit score track','alert', 'simulator', 'tracker', 'credit report']
    wr = csv.writer(open(out_file, 'wb'))
    for row in csv.reader(open(inp_file, 'rb')):
        if any(x in row[2] for x in phrases):
            wr.writerow(row)
             
def prepareCreditTrackerData_OldFormat(inp_file, out_file):
    wr = csv.writer(open(out_file, 'wb'))
    id_count=1
    current_category=None
    
    classes={'<provider>':'fico',
             '<account>':'account',
             '<time>':'february',
             '<number>':'23',
             '<creditreport>':'credit report',
             '<court>':'court',
             '<decrease>':'decrease',
             '<increase>':'increase',
             '<score>':'score',
             '<months>':'february',
             '<month>':'february',
             '<phonetype>':'iphone',
             '<iphone>':'iphone',
             '<dollars>':'$4',
             '<factor>':'on-time payments',
             '<incorrect>':'buggy',
             '<fraud>':'fraud',
             '<grade>':'b',
             '<profiletype>':'balances',
             '<creditscore>':'credit score',
             '<information>':'information'
             }
    
    
    for row in csv.reader(open(inp_file, 'rb')):
        if (row[0]=='' and row[1]=='') or (row[0]=='Intent'): continue
        if row[0]!='':current_category=row[0].replace('-','').replace(' ','')
            
        if current_category!=None:
            normalized=row[1]
            for class_name, substitution in classes.iteritems():
                normalized = normalized.replace(class_name, substitution)
                
            wr.writerow(['utt_id_'+str(id_count),normalized, current_category])
            id_count+=1;

def readClasses(inp_file):
    word_classes=collections.defaultdict(lambda:set([]))
    word_classes_order=[]
    wrd_class=None
    for i in open(inp_file, 'r'):
        i=i.strip()
        if i=='':continue
        if i.startswith('_class'):
            wrd_class=i
            word_classes_order.append(wrd_class)
            continue
        if wrd_class!=None:
            word_classes[wrd_class].add(i)
            
    return word_classes, word_classes_order        

def prepareCreditTrackerData_NewFormat(inp_file, out_file, word_class_dict, word_class_order):
    
    wr = csv.writer(open(out_file, 'wb'))
    current_category=None
    required_cols=set(['IntentName','InventoData'])
    header={}
    
    wb = xlrd.open_workbook( inp_file )
    sh = wb.sheet_by_index(0) 
    
    ctr=0
    for rownum in range(sh.nrows):
                
        if ctr==0:
            col_ctr=0
            for i in sh.row_values(rownum):
                header[str(i)]=col_ctr
                col_ctr+=1            
            
            if len(required_cols - set(header.keys()))>0:
                print required_cols
                print header.keys()
                raise Exception('Required columns not found!')               
            ctr+=1
            continue 
        
        row=sh.row_values(rownum)
        
        if (row[header['IntentName']]=='' or row[header['InventoData']]==''): continue
        normalized=words_only.sub('', row[header['InventoData']].lower())
        for wd_clss in word_class_order:
            normalized = normalized.replace(wd_clss, random.sample(word_class_dict[wd_clss],1)[0])
        #for class_name,class_content in word_class_dict.iteritems():
        #    normalized = normalized.replace(class_name, random.sample(class_content,1)[0])
                
        wr.writerow(['utt_id_'+str(ctr),normalized, row[header['IntentName']]])
        ctr+=1;

def getWorksheetHeader(sheet):
    header={}
    col_ctr=0
    for i in sheet.row_values(0):
        header[str(i).strip()]=col_ctr
        col_ctr+=1
    return header

def prepareTestData(inp_file, out_file, word_class_dict):
    wr = csv.writer(open(out_file, 'wb'))
    
    wb = xlrd.open_workbook( inp_file )
    test_data_sheet = wb.sheet_by_name('Kathy Data') 
    
    test_data_sheet_header = getWorksheetHeader(test_data_sheet)
    
    ctr=0
    for rownum in range(test_data_sheet.nrows):                
        if ctr==0:
            ctr+=1;
            continue         
        row=test_data_sheet.row_values(rownum)
        
        if (row[test_data_sheet_header['Tag']]=='' or row[test_data_sheet_header['Question']]==''): continue
               
        wr.writerow(['utt_id_'+str(ctr),row[test_data_sheet_header['Question']], row[test_data_sheet_header['Tag']]])
        ctr+=1;

def createClusterData(output_dir, input_file):

    unambiguous_CT=set(['CT05_InfoWrongTotalBalances','CT10_InfoWrongProfile','CT13_CreditUtilization','CT17_InfoUnknownLender','CT20_CTGeneral','CT21_CTCost','CT22_CTCancel','CT23_CTTransUnion','CT24_AuthUserInfo','CT25_InfoInquiries','CT26_CTScoreGeneration','CT27_CTRatingScale','CT29_CTDataUpdate','CT30_C1ReportingDate','CT31_CTUpdateDate','CT34_CTGradesOldestLine','CT40_CTBureauDispute','CT41_CreditEduReportFraud','CT42_CreditEduACRDotCom','CT43_ScoreHowIncrease','CT45_LendingWhyDeclined','CT46_LendingDeclineReasons','CT47_LendingDeclineInfoWrong','CT48_LendingScoreDifferent','CT49_CreditEduPayoffStrategy','CT51_NegativeInfoLifespan','CT53_CreditEduCreditFreeze'])
    Scores=set(['CT02_ScoreZero','CT03_ScoreUnchanged','CT04_ScoreDropping','CT01_ScoreDifferent','CT44_ScoreHowDecide'])
    Grades=set(['CT33_CTGradeStrategy','CT36_CTGradesCreditUtil','CT37_CTGradesRecentInquiries','CT35_CTGradesOnTimePayment','CT39_CTGradesAvailableCredit','CT38_CTGradesNewAccounts'])
    
    #unambiguous_CT=set(['CT05_InfoWrongTotalBalances','CT10_InfoWrongProfile','CT13_CreditUtilization','CT17_InfoUnknownLender','CT20_CTGeneral','CT21_CTCost','CT22_CTCancel','CT23_CTTransUnion','CT24_AuthUserInfo','CT25_InfoInquiries','CT27_CTRatingScale','CT29_CTDataUpdate','CT30_C1ReportingDate','CT31_CTUpdateDate','CT40_CTBureauDispute','CT41_CreditEduReportFraud','CT42_CreditEduACRDotCom','CT45_LendingWhyDeclined','CT46_LendingDeclineReasons','CT47_LendingDeclineInfoWrong','CT49_CreditEduPayoffStrategy','CT51_NegativeInfoLifespan','CT53_CreditEduCreditFreeze'])
    #Scores=set(['CT02_ScoreZero','CT03_ScoreUnchanged','CT04_ScoreDropping','CT01_ScoreDifferent','CT44_ScoreHowDecide','CT48_LendingScoreDifferent','CT26_CTScoreGeneration','CT43_ScoreHowIncrease'])
    #Grades=set(['CT33_CTGradeStrategy','CT36_CTGradesCreditUtil','CT37_CTGradesRecentInquiries','CT35_CTGradesOnTimePayment','CT39_CTGradesAvailableCredit','CT38_CTGradesNewAccounts','CT34_CTGradesOldestLine'])
    
    alerts=set(['CT55_AlertsDiscontinue','CT19_AlertsMultiple','CT54_AlertNoInfo','CT16_AlertsGeneral','CT18_AlertsMissing'])
    Info=set(['CT06_InfoWrongPayments','CT09_InfoWrongBankruptcy','CT14_InfoWrongRecentInquiries','CT15_InfoWrongNewAccounts','CT12_InfoWrongOldestAccount','CT11_InfoWrongOnTimePayments','CT07_InfoWrongAccounts','CT08_InfoWrongDelinquent'])
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    unambiguous_CT_file=open(os.path.join(output_dir, 'unambiguous_CT'), 'w')
    Info_file=open(os.path.join(output_dir, 'Info_cluster'), 'w')
    Scores_file=open(os.path.join(output_dir, 'Scores_cluster'), 'w')
    Grades_file=open(os.path.join(output_dir, 'Grades_cluster'), 'w')
    Alerts_file=open(os.path.join(output_dir, 'Alerts_cluster'), 'w')
    FirstLevel_file=open(os.path.join(output_dir, 'FirstLevel'), 'w')
        
    for line in open(input_file, 'r'):
        parts=line.split('\t')      
                
        if parts[2] in unambiguous_CT:
            unambiguous_CT_file.write(line)
            FirstLevel_file.write(parts[0]+'\t'+parts[1]+'\tUnambiguous_CT\t'+parts[2]+'\n')
        elif parts[2] in Info:
            Info_file.write(line)
            FirstLevel_file.write(parts[0]+'\t'+parts[1]+'\tCluster_Info\t'+parts[2]+'\n')
        elif parts[2] in Scores:
            Scores_file.write(line)
            FirstLevel_file.write(parts[0]+'\t'+parts[1]+'\tCluster_Score\t'+parts[2]+'\n')
        elif parts[2] in Grades:
            Grades_file.write(line)
            FirstLevel_file.write(parts[0]+'\t'+parts[1]+'\tCluster_Grades\t'+parts[2]+'\n')
        elif parts[2] in alerts:
            Alerts_file.write(line)
            FirstLevel_file.write(parts[0]+'\t'+parts[1]+'\tCluster_Alerts\t'+parts[2]+'\n')
        else:
            print parts[2]
            raise Exception('Unknown Intent')
    FirstLevel_file.close()    
    unambiguous_CT_file.close()
    Info_file.close()
    Scores_file.close()
    Grades_file.close()
    Alerts_file.close()

def prepareCreditTrackerData_NewFormat_withResponses(inp_file, out_file):
    
    wr = csv.writer(open(out_file, 'wb'))
    
    synth_data_required_cols=set(['line_ref_id','synthetic_data','ctid_tag', 'gran_intent_key'])
    header={}
    intents=set([])
    
    faqs=set([])
    
    wb = xlrd.open_workbook( inp_file )
    synth_data_sheet = wb.sheet_by_name('CT_Data') 
    resp_data_sheet = wb.sheet_by_name('IntentResponseLists-RevCycles')
    
    synth_data_sheet_header = getWorksheetHeader(synth_data_sheet)
    if len(synth_data_required_cols - set(synth_data_sheet_header.keys()))>0:
        print synth_data_required_cols
        print header.keys()
        raise Exception('Required columns not found!')  
    
    ctr=0
    for rownum in range(synth_data_sheet.nrows):                
        if ctr==0:
            ctr+=1;
            continue         
        
        row=synth_data_sheet.row_values(rownum)
        
        if (row[synth_data_sheet_header['synthetic_data']]=='' or row[synth_data_sheet_header['ctid_tag']]==''): continue
        #normalized=words_only.sub('', row[synth_data_sheet_header['synthetic_data']].lower())
        #for class_name,class_content in word_class_dict.iteritems():
        #    normalized = normalized.replace(class_name, random.sample(class_content,1)[0])
        if row[synth_data_sheet_header['ctid_tag']]=="CT11_InfoWrongOntimePayments": row[synth_data_sheet_header['ctid_tag']]="CT11_InfoWrongOnTimePayments"
        intents.add(row[synth_data_sheet_header['ctid_tag']])
        
        #row[synth_data_sheet_header['synthetic_data']]=unicode(row[synth_data_sheet_header['synthetic_data']].strip(codecs.BOM_UTF8), 'utf-8')
        #print row[synth_data_sheet_header['synthetic_data']]
        row[synth_data_sheet_header['synthetic_data']]=unicodedata.normalize('NFD', unicode(row[synth_data_sheet_header['synthetic_data']])).encode('ascii', 'ignore')
        #print row[synth_data_sheet_header['gran_intent_key']]
        row[synth_data_sheet_header['gran_intent_key']]=unicodedata.normalize('NFD', unicode(row[synth_data_sheet_header['gran_intent_key']])).encode('ascii', 'ignore')
        if (row[synth_data_sheet_header['gran_intent_key']] not in faqs) and (row[synth_data_sheet_header['gran_intent_key']].strip()!=''):
            #print row[synth_data_sheet_header['gran_intent_key']],row[synth_data_sheet_header['ctid_tag']]
            #print ['utt_id_'+str(ctr),row[synth_data_sheet_header['synthetic_data']], row[synth_data_sheet_header['ctid_tag']]]
            wr.writerow(['utt_id_'+str(ctr),row[synth_data_sheet_header['gran_intent_key']], row[synth_data_sheet_header['ctid_tag']]])
            ctr+=1;
            faqs.add(row[synth_data_sheet_header['gran_intent_key']])
                       
        #print row[synth_data_sheet_header['synthetic_data']]   
        #if row[synth_data_sheet_header['source']]=="chat":    
        #print ['utt_id_'+str(ctr),row[synth_data_sheet_header['synthetic_data']], row[synth_data_sheet_header['ctid_tag']]]
        wr.writerow([row[synth_data_sheet_header['line_ref_id']],row[synth_data_sheet_header['synthetic_data']], row[synth_data_sheet_header['ctid_tag']]])
        #ctr+=1;
    
    #sys.exit()
    #resp_data_required_cols=set(['response_text','ctid_tag','gran_id'])
    resp_data_required_cols=set(['gran_intents_included','ctid_tag'])
    resp_data_sheet_header = getWorksheetHeader(resp_data_sheet)
    if len(resp_data_required_cols - set(resp_data_sheet_header.keys()))>0:
        print resp_data_required_cols
        print header.keys()
        raise Exception('Required columns not found!')
    #print intents
    uniq_resp_utts={}
    row_ctr=0
    for rownum in range(resp_data_sheet.nrows):                
        if row_ctr==0:
            row_ctr+=1;
            continue         
        row=resp_data_sheet.row_values(rownum)
        if row[resp_data_sheet_header['ctid_tag']]=="CT11_InfoWrongOntimePayments": row[resp_data_sheet_header['ctid_tag']]="CT11_InfoWrongOnTimePayments"
        
        if row[resp_data_sheet_header['ctid_tag']] not in intents: 
            print 'Skipping '+row[resp_data_sheet_header['ctid_tag']]+' intent utterance from responses sheet'
            continue
        row[resp_data_sheet_header['gran_intents_included']]=unicodedata.normalize('NFD', unicode(row[resp_data_sheet_header['gran_intents_included']])).encode('ascii', 'ignore')
        for question in row[resp_data_sheet_header['gran_intents_included']].split("\n"): 
            #print ['utt_id_'+str(ctr),question,row[resp_data_sheet_header['ctid_tag']]]
            wr.writerow(['utt_id_'+str(ctr),question,row[resp_data_sheet_header['ctid_tag']]])
            ctr+=1; 
    print "Number of intents : "+str(len(intents))
        #if (row[resp_data_sheet_header['response_text']]=='' or row[resp_data_sheet_header['ctid_tag']]=='' or row[synth_data_sheet_header['gran_id']]!='n/a'): continue
               
        #resp_intent=[y for y in intents if '_'+row[resp_data_sheet_header['ctid_name']] in y]
        
        #if len(resp_intent)!=1:
        #    print '_'+row[resp_data_sheet_header['ctid_name']], resp_intent
        #    #print intents
        #    raise Exception('Problematic second response intent')
        
        #normalized=words_only.sub('', row[resp_data_sheet_header['response_text']].lower())
        #for class_name,class_content in word_class_dict.iteritems():
        #    normalized = normalized.replace(class_name, random.sample(class_content,1)[0])
        #uniq_resp_utts[row[resp_data_sheet_header['response_text']]]=row[resp_data_sheet_header['ctid_tag']]
    
    #for u, i in uniq_resp_utts.iteritems():            
    #    wr.writerow(['utt_id_'+str(ctr),u,i])
    #    ctr+=1;

def createDatasetForCT_Vs_Acc(acc_data_file, ct_data_file, out_file):
    
    #gen_inf_topic_goal_composition=['account_online_pw-get_help','account_online-get_help','account_online-login','account_pin-change','account_pin-query','account_pin-vague','account-query','activation-execute','balance_xfer-vague','billing-vague','card_add-request','card_benefits-query','card_expired-report','card_lost-report','card_not_received-report','card_not_working-report','card_replacement-request','cash_advance-query','charge-vague','credit_refund-query','fees_interest-query','payment_history-review','payments_automatic-query','promotional_apr-query','purchase_apr-find_out','purchase_apr-reduce','purchase_apr-vague','purchase-authorize','rewards_balance-find_out','rewards-query','rewards-redeem','statement_copy-request','statement_missing-report','statement-query','travel_domestic-notify','travel_international-notify','travel-notify']
    #gen_inf_topic_goal_composition=['account_online_pw-get_help','account_online-get_help','account_online-login','account_pin-change','account_pin-query','account_pin-vague','account-query','activation-execute','balance_xfer-vague','billing-vague','card_add-request','card_benefits-query','card_expired-report','card_lost-report','card_not_received-report','card_not_working-report','card_replacement-request','cash_advance-query','charge-vague','credit_refund-query','fees_interest-query','payment_history-review','payments_automatic-query','promotional_apr-query','purchase_apr-find_out','purchase_apr-reduce','purchase_apr-vague','purchase-authorize','rewards_balance-find_out','rewards-query','rewards-redeem','statement_copy-request','statement_missing-report','statement-query','travel_domestic-notify','travel_international-notify','travel-notify','account_status-query','billing-query','make_payment-execute','minimum_payment-find_out','pay_balance-execute','payment_due_date-change']
    gen_inf_topic_goal_composition=['account_pin-change','account_pin-query','account_pin-vague','activation-execute','balance_xfer-vague','card_add-request','card_lost-report','card_not_received-report','card_not_working-report','card_replacement-request','cash_advance-query','charge-vague','fees_interest-query','payment_history-review','payments_automatic-query','promotional_apr-query','purchase_apr-find_out','purchase_apr-reduce','purchase_apr-vague','purchase-authorize','rewards_balance-find_out','rewards-query','rewards-redeem','statement_copy-request','statement_missing-report','statement-query','travel_domestic-notify','travel_international-notify','travel-notify','make_payment-execute','minimum_payment-find_out','pay_balance-execute']
    
    #gen_inf_composition=['Payments_RU','AccountOnline_RU','Fraud_RU','AccountPIN_RU','ChargeDispute_RU','FileAddress_RU','Activation_RU','PaymentNextInfo_RU','CreditCard_RU','CreditLimit_RU','CardUsers_RU','Travel_RU','AvailableCredit_RU','Account_RU','Rewards_RU','FeesQuery_RU','CardNotWorking_RU','CreditLimitIncrease_RU','Billing_RU','AccountInfo_RU','APRPurchase_RU','Repeat_RU','AccountClose_RU','Statement_RU','MakePayment_RU','RecentTransactions_RU','CashAdvance_RU','BalanceDetails_RU','TravelInternational_RU','CardLostStolen_RU','APRPromo_RU','BalanceXfer_RU','ChargeQuery_RU','PaymentHistory_RU']
    gen_other_composition=['NONE_RU', 'Representative_RU', 'Command_RU']
    
    toplevel_CT=set(['CT56_CTLogout', 'CT57_Simulator'])
    unambiguous_CT=set(['CT05_InfoWrongTotalBalances','CT10_InfoWrongProfile','CT13_CreditUtilization','CT17_InfoUnknownLender','CT20_CTGeneral','CT21_CTCost','CT22_CTCancel','CT23_CTTransUnion','CT24_AuthUserInfo','CT25_InfoInquiries','CT26_CTScoreGeneration','CT27_CTRatingScale','CT29_CTDataUpdate','CT30_C1ReportingDate','CT31_CTUpdateDate','CT34_CTGradesOldestLine','CT40_CTBureauDispute','CT41_CreditEduReportFraud','CT42_CreditEduACRDotCom','CT43_ScoreHowIncrease','CT45_LendingWhyDeclined','CT46_LendingDeclineReasons','CT47_LendingDeclineInfoWrong','CT48_LendingScoreDifferent','CT49_CreditEduPayoffStrategy','CT51_NegativeInfoLifespan','CT53_CreditEduCreditFreeze'])
    Scores=set(['CT02_ScoreZero','CT03_ScoreUnchanged','CT04_ScoreDropping','CT01_ScoreDifferent','CT44_ScoreHowDecide'])
    Grades=set(['CT33_CTGradeStrategy','CT36_CTGradesCreditUtil','CT37_CTGradesRecentInquiries','CT35_CTGradesOnTimePayment','CT39_CTGradesAvailableCredit','CT38_CTGradesNewAccounts'])
    
    #unambiguous_CT=set(['CT05_InfoWrongTotalBalances','CT10_InfoWrongProfile','CT13_CreditUtilization','CT17_InfoUnknownLender','CT20_CTGeneral','CT21_CTCost','CT22_CTCancel','CT23_CTTransUnion','CT24_AuthUserInfo','CT25_InfoInquiries','CT27_CTRatingScale','CT29_CTDataUpdate','CT30_C1ReportingDate','CT31_CTUpdateDate','CT40_CTBureauDispute','CT41_CreditEduReportFraud','CT42_CreditEduACRDotCom','CT45_LendingWhyDeclined','CT46_LendingDeclineReasons','CT47_LendingDeclineInfoWrong','CT49_CreditEduPayoffStrategy','CT51_NegativeInfoLifespan','CT53_CreditEduCreditFreeze'])
    #Scores=set(['CT02_ScoreZero','CT03_ScoreUnchanged','CT04_ScoreDropping','CT01_ScoreDifferent','CT44_ScoreHowDecide','CT48_LendingScoreDifferent','CT26_CTScoreGeneration','CT43_ScoreHowIncrease'])
    #Grades=set(['CT33_CTGradeStrategy','CT36_CTGradesCreditUtil','CT37_CTGradesRecentInquiries','CT35_CTGradesOnTimePayment','CT39_CTGradesAvailableCredit','CT38_CTGradesNewAccounts','CT34_CTGradesOldestLine'])
        
    Info=set(['CT06_InfoWrongPayments','CT09_InfoWrongBankruptcy','CT14_InfoWrongRecentInquiries','CT15_InfoWrongNewAccounts','CT12_InfoWrongOldestAccount','CT11_InfoWrongOnTimePayments','CT07_InfoWrongAccounts','CT08_InfoWrongDelinquent'])
    alerts=set(['CT55_AlertsDiscontinue','CT19_AlertsMultiple','CT54_AlertNoInfo','CT16_AlertsGeneral','CT18_AlertsMissing'])    
       
    print 'total topic-goals in Accounts: '+str(len(gen_inf_topic_goal_composition))
    print 'total topic-goals in Other: '+str(len(gen_other_composition))
    print 'total granular intents in Unambiguous cluster: '+str(len(unambiguous_CT))
    print 'total granular intents in Info cluster: '+str(len(Info))
    print 'total granular intents in Scores cluster: '+str(len(Scores))
    print 'total granular intents in Grades cluster: '+str(len(Grades))
    print 'total granular intents in alerts cluster: '+str(len(alerts))
       
    #intent_ctrs={'Unambiguous_CT':0,'Cluster_Info':0,'Cluster_Score':0,'Cluster_Grades':0,'Cluster_Alerts':0}
    intent_ctrs = collections.defaultdict(lambda:0)    
    acc_utts={'other':collections.defaultdict(lambda: collections.defaultdict(lambda:0)),
              'acc':collections.defaultdict(lambda: collections.defaultdict(lambda:0))}
    
    dollar_amount_hack=re.compile('(?:_class_number\\s)+_class_currency')
    acc_intent_freq=collections.defaultdict(lambda:0)
    other_intent_freq=collections.defaultdict(lambda:0)    
    total_acc_utts=0.0
    total_other_utts=0.0
    for i in open(acc_data_file,'r').readlines():
        #parts=i.split('\t')
        parts=[x.strip() for x in i.split('\t')]
        if parts[2].strip() in gen_inf_topic_goal_composition:            
            acc_utts['acc'][parts[2].strip()][parts[1].strip()]+=1
            acc_intent_freq[parts[2]]+=1
            total_acc_utts+=1.0
            continue
        elif parts[5].strip() in gen_other_composition:
            acc_utts['other'][parts[5].strip()][parts[1]]+=1
            other_intent_freq[parts[5].strip()]+=1
            total_other_utts+=1.0
        else:continue
    print total_acc_utts,total_other_utts
    
    ## topic-goal distribution the same as IVR data
    #for i,j in acc_intent_freq.iteritems():
    #    acc_intent_freq[i]=float(j)/total_acc_utts
    
    ##  Equal distribution
    for i,j in acc_intent_freq.iteritems():
        #print 1.0/float(len(acc_intent_freq))
        acc_intent_freq[i]=1.0/float(len(acc_intent_freq))

    for i,j in other_intent_freq.iteritems():
        other_intent_freq[i]=float(j)/total_other_utts

        
    acc_utts_sorted= {'other':{},
                      'acc':{}}
        
    for i,j in acc_utts.iteritems():
        for intent, utt_dict in j.iteritems():
            acc_utts_sorted[i][intent] = sorted(utt_dict.items(), key=operator.itemgetter(1), reverse=True)
         
    
    wr= open(out_file, 'w')
    for i in open(ct_data_file,'r').readlines():
        parts=i.split('\t')
        intent=None
        if parts[2].strip() in unambiguous_CT:
            intent='Unambiguous_CT'
            intent_ctrs['Unambiguous_CT']+=1
        elif parts[2].strip() in Info:
            intent='Cluster_Info'
            intent_ctrs['Cluster_Info']+=1
        elif parts[2].strip() in Scores:
            intent='Cluster_Score'
            intent_ctrs['Cluster_Score']+=1
        elif parts[2].strip() in Grades:
            intent='Cluster_Grades'
            intent_ctrs['Cluster_Grades']+=1
        elif parts[2].strip() in alerts:
            intent_ctrs['Cluster_Alerts']+=1
            intent='Cluster_Alerts'
        elif parts[2].strip() in toplevel_CT:
            intent_ctrs[parts[2].strip()]+=1
            intent=parts[2].strip()    
        else:
            raise Exception('Unknown Intent : '+parts[2].strip())
            
        wr.write(parts[0]+'\t'+parts[1]+'\t'+intent+'\t'+parts[2].strip()+'\n')
        #print utt_ctr
        
    #print sorted(acc_intent_freq.items(), key=operator.itemgetter(1))
    #print sorted(other_intent_freq.items(), key=operator.itemgetter(1))
    #num_ct_utts=utt_ctr
    num_ct_utts=max(intent_ctrs.values())
    num_acc_utts=0
    utt_ctr=0
    
    for intent,percentage in acc_intent_freq.iteritems():
        
        for x in range(int(percentage*(num_ct_utts-300))):
            if x>=len(acc_utts_sorted['acc'][intent]):                     
                div = x/len(acc_utts_sorted['acc'][intent])
                utt_mod = dollar_amount_hack.sub( '_class_number_class_currency',acc_utts_sorted['acc'][intent][x-(div*len(acc_utts_sorted['acc'][intent]))][0])
            #    wr.write('utt_'+str(utt_ctr)+'\t'+utt_mod+'\tAccount\t'+intent+'\n')
            else:
                utt_mod=dollar_amount_hack.sub( '_class_number_class_currency',acc_utts_sorted['acc'][intent][x][0])
            wr.write('acc_utt_'+str(utt_ctr)+'\t'+utt_mod+'\tAccount\t'+intent+'\n')
            num_acc_utts+=1
            utt_ctr+=1
        
    num_other_utts=0   
    for intent,percentage in other_intent_freq.iteritems():
        
        for x in range(int(percentage*(num_ct_utts-300))):
            if x>=len(acc_utts_sorted['other'][intent]):
                div = x/len(acc_utts_sorted['other'][intent])
                utt_mod=dollar_amount_hack.sub( '_class_number_class_currency',acc_utts_sorted['other'][intent][x-(div*len(acc_utts_sorted['other'][intent]))][0])
            #    wr.write('utt_'+str(utt_ctr)+'\t'+acc_utts_sorted['other'][intent][x-(div*len(acc_utts_sorted['other'][intent]))][0]+'\tOther\t'+intent+'\n')
            else:
                utt_mod=dollar_amount_hack.sub( '_class_number_class_currency',acc_utts_sorted['other'][intent][x][0])
            wr.write('ood_utt_'+str(utt_ctr)+'\t'+utt_mod+'\tOther\t'+intent+'\n')
            num_other_utts+=1
            utt_ctr+=1
    ####### Equal Intent frequency ########
    ########################################
    #num_acc_utts=0          
    #while (num_acc_utts<=(num_ct_utts+500) and len(acc_utts_sorted['acc'])>0):
    #    acc_intents=acc_utts_sorted['acc'].keys()               
    #    for intent in acc_intents:    
    #        if len(acc_utts_sorted['acc'][intent])==0:
    #            del acc_utts_sorted['acc'][intent]
    #            continue
            
    #        wr.write('utt_'+str(utt_ctr)+'\t'+acc_utts_sorted['acc'][intent].pop()[0]+'\tAccount\t'+intent+'\n')
    #        utt_ctr+=1
    #        num_acc_utts+=1
    #        continue
    
    #num_other_utts=0    
    #while (num_other_utts<=(num_ct_utts+500) and len(acc_utts_sorted['other'])>0):    
        
    #    other_intents = acc_utts_sorted['other'].keys()
    #    for intent in other_intents:
    #        if len(acc_utts_sorted['other'][intent])==0:
    #            del acc_utts_sorted['other'][intent]
    #            continue
            
    #        if len(acc_utts_sorted['other'][intent])==0:
    #            del acc_utts_sorted['other'][intent]
    #            continue            
    #        wr.write('utt_'+str(utt_ctr)+'\t'+acc_utts_sorted['other'][intent].pop()[0]+'\tOther\t'+intent+'\n')
    #        utt_ctr+=1
    #        num_other_utts+=1            
    #        continue    
        
    ########################################
    ########################################
    ########################################
    
    wr.close()
    
    #if len(acc_utts['acc'].keys())>(num_ct_utts+200): num_acc_utts= num_ct_utts+200
    #else:num_acc_utts= len(acc_utts['acc'].keys())-1
    
    #for i in sorted(acc_utts['acc'].items(), key=operator.itemgetter(1), reverse=True)[:num_acc_utts]:
    #    #print utt_ctr
    #    #print i
    #    wr.write('utt_'+str(utt_ctr)+'\t'+i[0]+'\tAccount\tAccount_1\n')
        
    #    utt_ctr+=1
    
    #if len(acc_utts['other'].keys())>(num_ct_utts+200):num_other_utts= num_ct_utts+200
    #else:num_other_utts=len(acc_utts['other'].keys())-1            
    #for i in sorted(acc_utts['other'].items(), key=operator.itemgetter(1), reverse=True)[:num_other_utts]:
    #    wr.write('utt_'+str(utt_ctr)+'\t'+i[0]+'\tOther\tOther_1\n')
    #    utt_ctr+=1
    
    print intent_ctrs
    print 'number of ct utts: '+str(sum(intent_ctrs.values()))
    print 'number of acc utts: '+str(num_acc_utts)
    print 'number of other utts: '+str(num_other_utts)

if __name__ == '__main__':
    ## ***** USE THIS *******
    
    ## Created a dataset with account and credit tracker utterances - keeping all the account topic-goals equi-probable. 
    createDatasetForCT_Vs_Acc('E:\\Data\\CapOne\\Credit_tracker\\20150721b_withResponses\\Data\\FirstLevelNormalization\\Account\\FirstResponses_WCNormalized',
                              'E:\\Data\\CapOne\\Credit_tracker\\20150721b_withResponses\\Data\\FirstLevelNormalization\\CT\\Normalized_chat_data',                              
                              'E:\\Data\\CapOne\\Credit_tracker\\20150721b_withResponses\\Data\\FirstLevelNormalization\\First_level_dataset_account_fixed_flattened_distribution')
    sys.exit()
    #wd_classes, wd_class_order = readClasses('E:\\Data\\CapOne\\Credit_tracker\\Word_Classes_new_Kathy')
    #for x,y in d.iteritems():
    #    print x, random.sample(y,1)[0]
    
    #print "Number of classes : "+str(len(wd_classes))
    words_only = re.compile(r"[^a-z'|\s]")
    
    #prepareTestData('E:\\Data\\CapOne\\Credit_tracker\\TestDataFromKathy.xlsx',
    #                                   'E:\\Data\\CapOne\\Credit_tracker\\formatted_TestDataFromKathy.csv',
    #                                   d)
    
    #createClusterData('E:\\Data\\CapOne\\Credit_tracker\\20150401a_withResponses\\Data\\FirstLevelNormalization_new_word_classes\\ClusterData',
    #                  'E:\\Data\\CapOne\\Credit_tracker\\20150401a_withResponses\\Data\\FirstLevelNormalization_new_word_classes\\CT\\Normalized_chat_data')
    #sys.exit()
    
    ## ***** USE THIS *******
    ## Create un-normalized dataset from the datamaster 
    prepareCreditTrackerData_NewFormat_withResponses('E:\\Data\\CapOne\\Credit_tracker\\C1_CT_DataSheet_20150721b.xlsx',
                                       'E:\\Data\\CapOne\\Credit_tracker\\formatted_synthData_20150721b_withResponses.csv')
    
    sys.exit()
    
    
    
