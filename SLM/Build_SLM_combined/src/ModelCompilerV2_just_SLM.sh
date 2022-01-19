#!/bin/ksh

if [ $# -ne 1 ]; then
    echo "Usage:bash ModelCompilerV2.sh <Config-file>"
    exit 1
fi

if [ ! -f $1 ]; then
    echo "Config file doesn't exist"
    exit 1
else
    source $1
fi


echo `date` "Building SLM from the Input corpus ..."
echo "current directory: $WORKDIR"
echo

mkdir -p $INTERDIR
mkdir -p $OUTDIR

FAFR19=$USER@$host2
if [ $CFLAG -ne 0 ]; then
    echo "Substituting urls in place of classes"
    python $SRCDIR/norm_corpus.py $INPDATA $NORMDATA 1 $SUBS_FILE
else
    python $SRCDIR/norm_corpus.py $INPDATA $NORMDATA 0
fi

echo "Processing input corpus to ARPA file"
output=`ssh $host1 bash $SRCDIR/convert_to_arpa.sh $NORMDATA $INPARPA`

echo "adding backoff weights"
python $SRCDIR/add_backoff.py $INPARPA

echo "Copying arpa files to fafr19"
scp -q $INTERARPA $FAFR19:~/

command="(/usr/local/bin/NGramToCFGTool.exe -i inter.arpa -t ARPA -o inter.cfg -b \"<s>\" -e \"</s>\" -l 1033 -r Top -sf W3C -inittag \"out={}; out.classsubstitution = gSubstitutions = [];\")"
output=`ssh $host2 $command`
scp -q $FAFR19:~/inter.cfg $slm_file
