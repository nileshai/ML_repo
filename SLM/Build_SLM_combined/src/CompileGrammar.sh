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

echo "Confirming existence of local files for compiling SSI and combining with SLM"
echo

## Check local files
required_local_files="$slm_file $ssi_file $ssi_params_file"
for file in ${required_local_files}
do
    if [ ! -f $file ]; then
	echo "$file not found"
	exit 1
    fi
done

echo "Confirming existence of tools on $SSI_COMPILE_HOST"
echo

## Checking existence of Compile-tools
command="(Test-Path $installation_dir\\classifiermodelcompiler.exe\) -and (Test-Path $installation_dir\\cfgappend.exe) -and (Test-Path $installation_dir\\$required_dll)"
output=`ssh $SSI_COMPILE_USER_HOST $command`
if [ ! output ]; then
    echo "Couldn't find $installation_dir\\classifiermodelcompiler.exe or $installation_dir\\cfgappend.exe or $installation_dir\\$required_dll"
    exit 1
fi

echo "Creating remote dir $tmp_dir and copying preparing for compilation"
echo

## Create tmp directory and copy the dll in that directory
command="New-Item -type "directory" $tmp_dir | Out-Null;Copy-Item $installation_dir\\$required_dll $tmp_dir | Out-Null;"
ssh $SSI_COMPILE_USER_HOST $command;

echo "Copying files to $SSI_COMPILE_HOST:$tmp_dir"
echo

## Copy files to tmp directory
scp -q $slm_file $ssi_file $ssi_params_file $SSI_COMPILE_USER_HOST:$tmp_dir 

echo "Compiling SSI"
echo


## Compile the SSI file
remote_slm_file=`basename $slm_file`
echo "remote slm files $remote_slm_file"
remote_ssi_file=`basename $ssi_file`
remote_ssi_params_file=`basename $ssi_params_file`
command="Push-Location $tmp_dir;$installation_dir\\classifiermodelcompiler.exe -m $remote_ssi_file -p $remote_ssi_params_file -o ssi.cfr;"
output=`ssh $SSI_COMPILE_USER_HOST $command`

## Checking whether compiled SSI file was created or not. This step can be removed to improve speed
command="Test-path $tmp_dir\\ssi.cfr"
output=`ssh $SSI_COMPILE_USER_HOST $command`
if [ ! output ]; then
    echo "Compiled SSI file couldn't be created: $tmp_dir\\ssi.cfr"
    exit 1
fi

echo "Compiling SSI with SLM"
echo

## Merging SSI and SLM models to form the final model
command="Push-Location $tmp_dir;$installation_dir\\cfgappend.exe $remote_slm_file ssi.cfr compiled_model.cfg;"
output=`ssh $SSI_COMPILE_USER_HOST $command`

## Checking whether compiled model was created or not. This step can be removed to improve speed
command="Test-path $tmp_dir\\compiled_model.cfg"
output=`ssh $SSI_COMPILE_USER_HOST $command`
if [ ! output ]; then
    echo "Model couldn't be created"
    exit 1
fi

CWD=`pwd`

echo "Copying compiled models to $CWD"
echo

## Copy model files to the current working directory
scp -q $SSI_COMPILE_USER_HOST:$tmp_dir\\ssi.cfr $OUTDIR/ssi.cfr
scp -q $SSI_COMPILE_USER_HOST:$tmp_dir\\compiled_model.cfg $OUTDIR/compiled_model.cfg

command="scp -q $SSI_COMPILE_USER_HOST:$tmp_dir\\ssi.cfr $OUTDIR"

echo "Cleaning up $SSI_COMPILE_USER_HOST for tmp files"
echo 

ssh $SSI_COMPILE_USER_HOST Remove-Item -Force -Recurse $tmp_dir

echo `date` "Successfully finished !!"
