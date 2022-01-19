input_file="/home/jgeorge/ebay_SLM/Build_SLM_combined/Input/word_classes_eBay_UK_v7"
output_file="/home/jgeorge/ebay_SLM/Build_SLM_combined/Input/substitutions"
sentence="<URL:http://grammar.svc.tellme.com/nlu/ebay/en-gb/word_classes_root.grxml"
fin = open(input_file,"r")
fout = open(output_file,"wb")
for line in fin:
    line = line.strip()
    if(line.startswith("_class_")):
        toWrite=line +" "+ sentence + "#"+line+">\n"
        fout.write(toWrite)

