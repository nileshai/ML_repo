#!/bin/ksh

if [ $# -ne 1 ]; then
    echo "Usage:bash src/CompileGrammar.sh <Config-file=CompileGrammar.cfg>"
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

USER_NAME=$USER

SSI_COMPILE_HOST=$host
SSI_COMPILE_USER_HOST=$USER_NAME@$SSI_COMPILE_HOST

ARPA_COMPILE_HOST=$host1
ARPA_COMPILE_USER_HOST=$USER_NAME@$ARPA_COMPILE_HOST

SLM_COMPILE_HOST=$host2
SLM_COMPILE_USER_HOST=$USER_NAME@$SLM_COMPILE_HOST



if [ $CFLAG -ne 0 ]; then
    echo "Substituting urls in place of classes"
    python $SRCDIR/norm_corpus.py $INPDATA $NORMDATA 1 $SUBS_FILE
else
    python $SRCDIR/norm_corpus.py $INPDATA $NORMDATA 0
fi

echo "Processing input corpus to ARPA file"
output=`ssh $ARPA_COMPILE_USER_HOST bash $SRCDIR/convert_to_arpa.sh $NORMDATA $INPARPA`


echo "adding backoff weights and correcting the arpa file"
python $SRCDIR/add_backoff.py $INPARPA

echo "Confirming existence of local files for compiling SLM"
echo

## Check local files
required_local_files="$INTERARPA $ARPAX_FILE $RECO_CONFIG_FILE"
for file in ${required_local_files}
do
    if [ ! -f $file ]; then
	echo "$file not found"
	exit 1
    fi
done
## Create tmp directory and copy required files to that directory
command="New-Item -type "directory" $tmp_dir | Out-Null;"
ssh $SLM_COMPILE_USER_HOST $command;
echo "Copying arpa,arpax,config files to $SLM_COMPILE_HOST"
scp -q $INTERARPA $RECO_CONFIG_FILE $ARPAX_FILE $SLM_COMPILE_USER_HOST:$tmp_dir

echo "compiling the SLM file"
remote_arpax_file=`basename $ARPAX_FILE`
echo "arpax file $ARPAX_FILE"
remote_slm_file=`basename $slm_file`
remote_reco_config_file=`basename $RECO_CONFIG_FILE`
echo "required remote files $remote_arpax_file $remote_reco_config_file $remote_slm_file"

#command='Push-Location C:\Users\jgeorge\tmp;&(\"C:\Program Files\Microsoft SDKs\Speech\v11.1\Tools\CompileGrammar.exe\") -In all.arpax -InFormat ARPA -Out inter.cfg -RecoConfig RecoConfig.xml'
command='Push-Location '"$tmp_dir"';&(\"C:\Program Files\Microsoft SDKs\Speech\v11.1\Tools\CompileGrammar.exe\") -In '"$remote_arpax_file"' -InFormat ARPA -Out '"$remote_slm_file"' -RecoConfig '"$remote_reco_config_file"
echo "command $command"
output=`ssh $SLM_COMPILE_USER_HOST $command`
scp -q $SLM_COMPILE_USER_HOST:$tmp_dir\\inter.cfg $slm_file

echo "Removing files used for SLM compilation from $SLM_COMPILE_HOST"
ssh $SLM_COMPILE_USER_HOST Remove-Item -Force -Recurse $tmp_dir

echo `date` "Successfully finished !!"
