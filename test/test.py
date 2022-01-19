



in_file = open('E:\\Data\\CapOne\\Transcriptions\\CapOne_NLData_TagMaster_20140226a\\DatasetDivision\\CompleteDataset+SyntheticData_WordClasses_v2', 'r')
out_file = open('E:\\Data\\CapOne\\Transcriptions\\CapOne_NLData_TagMaster_20140226a\\DatasetDivision\\First+SecondResponses\\SLMData\\CompleteDataset+SyntheticData_WordClasses_v2', 'w')
for line in in_file:
    parts = line.split('\t')
    out_file.write(parts[1]+'\n')
    
out_file.close()