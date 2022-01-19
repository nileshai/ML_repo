import sys, sets, operator, datetime, csv, math
from _collections import defaultdict


class Account(object):
    sorted_sessions,ivr2web_sessions,ivr2chat_sessions,chat2ivr_sessions,web2ivr_sessions,true_ivr2chat_sessions,true_chat2ivr_sessions=(None,)*7
    def __init__(self, id):
        self.account_id=id
        self.web_sessions={}
        self.ivr_sessions={}
    
    def add_IVRSession(self, id, ssn):
        self.ivr_sessions[id]=ssn
            
    def add_WebSession(self, id, ssn):
        self.web_sessions[id]=ssn
    
    def sort_sessions(self):
        self.sorted_sessions=(self.web_sessions.values()+self.ivr_sessions.values())
        self.sorted_sessions.sort(key = lambda x:x.start_time)
           
    def create_IVR2Web_session_pairs(self):
        self.ivr2web_sessions=[]
        ivr_ssn=None
        for i in self.sorted_sessions:
            if i.ivr:
                ivr_ssn = i
                continue
            if ivr_ssn!=None and not i.ivr:
                self.ivr2web_sessions.append((i,ivr_ssn))        
                ivr_ssn=None 

    def create_IVR2Chat_session_pairs(self):
        self.ivr2chat_sessions=[]
        ivr_ssn=None
        for i in self.sorted_sessions:
            if i.ivr:
                ivr_ssn = i
                continue
            if ivr_ssn!=None and (not i.ivr) and i.chat_offered:
                self.ivr2chat_sessions.append((i,ivr_ssn))
                ivr_ssn=None 

    def create_True_IVR2Chat_session_pairs(self):
        self.true_ivr2chat_sessions=[]        
        for i in range(len(self.sorted_sessions)):
            if (i+1<len(self.sorted_sessions)) and self.sorted_sessions[i].ivr and (not self.sorted_sessions[i+1].ivr) and self.sorted_sessions[i+1].chat_offered:
                self.true_ivr2chat_sessions.append((self.sorted_sessions[i+1], self.sorted_sessions[i]))

    def create_True_Chat2IVR_session_pairs(self):
        self.true_chat2ivr_sessions=[]        
        for i in range(len(self.sorted_sessions)):
            if (i+1<len(self.sorted_sessions)) and self.sorted_sessions[i+1].ivr and (not self.sorted_sessions[i].ivr) and self.sorted_sessions[i].chat_offered:
                self.true_chat2ivr_sessions.append((self.sorted_sessions[i+1], self.sorted_sessions[i]))
                         
    def create_Chat2IVR_session_pairs(self):
        self.chat2ivr_sessions=[]
        chat_ssn=None
        for i in self.sorted_sessions:
            if (not i.ivr) and i.chat_offered:
                chat_ssn = i
                continue
            if chat_ssn!=None and i.ivr:
                self.chat2ivr_sessions.append((i,chat_ssn))
                chat_ssn=None 

    def create_Web2IVR_session_pairs(self):
        self.web2ivr_sessions=[]
        web_ssn=None
        for i in self.sorted_sessions:
            if not i.ivr:
                web_ssn = i
                continue
            if web_ssn!=None and i.ivr:
                self.web2ivr_sessions.append((i,web_ssn))
                web_ssn=None 

class session():
    start_time, id, ivr = (None,)*3    
    def __init__(self, id, timestamp, ivr_flag=False):
        self.id = id
        self.start_time = timestamp       
        self.ivr = ivr_flag
        
class web_session(session):
    chat_offered=False
    chat_offering_timestamp=None
    
    def __init__(self, id, timestamp):
        session.__init__(self, id, timestamp)

    def set_chat_offered(self, timestamp):
        self.chat_offered=True
        self.chat_offering_timestamp=timestamp
        self.start_time = timestamp
                
class ivr_session(session):
    ani,cust_id,dnis,call_direction,termination_type,call_duration,transferType,tfReason,destination=(None,)*9
    
    def __init__(self, id, timestamp):
        session.__init__(self, id, timestamp, True)

class linked_sessions(object):
    web_session_info=None
    def __init__(self, ivr_session,web_session):
        self.ivr_session = ivr_session
        self.web_session = web_session

def diff_in_hrs(timestamp_1,timestamp_2):
    diff=datetime.datetime.fromtimestamp(timestamp_1/1000.)-datetime.datetime.fromtimestamp(timestamp_2/1000.)
    return diff.total_seconds()/60.0/60.0

def generateHourlyStats(session_pairs):
    hourly_stats = defaultdict(lambda:0)
    for i in session_pairs:hourly_stats[math.ceil(diff_in_hrs(i[0].start_time,i[1].start_time))]+=1
    return hourly_stats



if __name__ == "__main__":
    
    #out_file = open(r'E:\tmp_dir\duplicate_link_properties', 'w')
    #ssn_pairs = {}
    #for i in open(r'E:\tmp_dir\CapOne_omnichannel_sessions_June_by_CallstartEvent\query_output', 'r'):
    #    session_details = i.split('\t')
    #    
    #    if ssn_pairs.has_key(session_details[11]+'+'+session_details[0]):
    #        out_file.write(i)
    #        out_file.write(ssn_pairs[session_details[11]+'+'+session_details[0]].web_session_info)
    #        continue
        
    #    ws = web_session(session_details[11], int(session_details[12]))
    #    ivs = ivr_session(session_details[0],int(session_details[1]))
    #    link = linked_sessions(ivs, ws)
    #    link.web_session_info=i
        
    #    ssn_pairs[session_details[11]+'+'+session_details[0]] = link
         
    #sys.exit()
    
    
    accounts = {}
    for i in open(r'E:\tmp_dir\CapOne_omnichannel\June\All_month\Linked_Web_sessions\Sessions_grouped_by_acc_id\Raw\query_output', 'r'):
        parts=i.split('\t')
        acc = Account(int(parts[0]))    
        
        for j in parts[1].split('),('):
            session_details = j.split(',')
            ws_id=session_details[1].split('@@')[0]
            ts = int(session_details[3].split(')}')[0])
            if acc.web_sessions.has_key(ws_id): ws=acc.web_sessions[ws_id]
            else: ws = web_session(ws_id, ts)
            if '@@' in session_details[1]:ws.set_chat_offered(ts)
            acc.add_WebSession(ws_id, ws)       
                
        accounts[int(parts[0])]=acc
    
    for i in open(r'E:\tmp_dir\CapOne_omnichannel_sessions_June_by_CallstartEvent\query_output', 'r'):
        session_details = i.split('\t')
        acc_id = int(session_details[12])
        if not accounts.has_key(acc_id):
            print i
            raise Exception('Account-id not found in linked web sessions')
        acc = accounts[acc_id]
        
        if acc.ivr_sessions.has_key(session_details[0]):continue
          
        ivs=ivr_session(session_details[0],int(session_details[1]))
        ivs.ani=session_details[2]
        ivs.call_direction=session_details[4]
        ivs.call_duration=int(session_details[6])
        ivs.destination=session_details[9]
        ivs.dnis=session_details[3]
        ivs.termination_type=session_details[5]
        ivs.tfReason=session_details[8]
        ivs.transferType=session_details[7]
        acc.add_IVRSession(session_details[0], ivs)    
    
    stats = defaultdict(lambda:0)
    session_pairs = defaultdict(lambda:[])
    for i in accounts.values():
        
        stats['web_sessions']+=len(i.web_sessions)
        stats['ivr_sessions']+=len(i.ivr_sessions)
        stats['chat_sessions']+=[x.chat_offered for x in i.web_sessions.values()].count(True)
        
        if len(i.ivr_sessions)>0 and len(i.web_sessions)>0:
            stats['acc_ids_with_ivr_and_web_sessions']+=1

            
            i.sort_sessions()
            i.create_IVR2Web_session_pairs()
            i.create_IVR2Chat_session_pairs()
            i.create_Web2IVR_session_pairs()
            i.create_Chat2IVR_session_pairs()
            i.create_True_IVR2Chat_session_pairs()
            i.create_True_Chat2IVR_session_pairs()
            #if i.account_id==10056761518:
            #print i.account_id, len(i.ivr_sessions), len(i.web_sessions), len(i.ivr2web_sessions), len(i.ivr2chat_sessions), len(i.web2ivr_sessions), len(i.chat2ivr_sessions) #, [x.chat_offered for x in i.web_sessions.values()]
            #    for j in i.ivr2web_sessions:
            #        print j[0].id, j[0].start_time, j[1].id, j[1].start_time
                       
            session_pairs['ivr2web_sessions']+=i.ivr2web_sessions
            session_pairs['ivr2chat_sessions']+=i.ivr2chat_sessions
            session_pairs['web2ivr_sessions']+=i.web2ivr_sessions
            session_pairs['chat2ivr_sessions']+=i.chat2ivr_sessions
            session_pairs['true_ivr2chat_sessions']+=i.true_ivr2chat_sessions
            session_pairs['true_chat2ivr_sessions']+=i.true_chat2ivr_sessions
        else:
            stats['acc_ids_with_web_sessions_only']+=1
           
    print 'Total account ids from web-session data: '+str(len(accounts))
    print stats
    for i,j in session_pairs.iteritems():
        print i, len(j)
        writer = csv.writer(open(r'E:\tmp_dir\CapOne_omnichannel\June\All_month\Stats\\'+i+'.csv', 'wb'))
        writer.writerow(['Difference between the sessions', 'Frequency', 'Percentage'])        
        hourly = generateHourlyStats(j)
        tot_ssns = sum(hourly.values())
        for key, value in sorted(hourly.items(), key=operator.itemgetter(0)):
            writer.writerow([key, value, "{0:.2f}".format((float(value)/tot_ssns)*100)+"%"])
    
    