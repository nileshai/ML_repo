import csv,re,sys

if __name__ == '__main__':
    if len(sys.argv)!=3:
        print 'Usage: python ParseLogtags.py <sorted_input_tsv_file> <output_csv_file>\n'
        sys.exit(1)

    uuid=''
    tagged_dta=csv.writer(open(sys.argv[2], 'wb'))
    tagged_dta.writerow(['uuid', 'intent_concatenated', 'menus', 'first intent', 'last intent' ])
    intents=[]
    menus=[]

    RU_intent_regex=re.compile('amex\.([a-z0-9]+)\.match\.([a-z]+_RU)', re.IGNORECASE)
    for row in csv.DictReader(open(sys.argv[1]), delimiter ='\t'):

        if uuid!=row['channelsessionId']:

            if uuid!='':
                tagged_dta.writerow([uuid, ':'.join(intents), ':'.join(menus)]+([intents[0],intents[1]] if len(intents)>1 else [intents[0],intents[0]] if len(intents)>0 else ["",""])                                     )

            uuid = row['channelsessionId']
            intents = []
            menus = []

        for i in RU_intent_regex.findall(row['logtag']):
            menus.append(i[0])
            intents.append(i[1])