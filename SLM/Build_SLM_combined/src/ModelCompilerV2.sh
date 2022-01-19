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

EN_US=1033
EN_GB=2057
LOCALE=$EN_GB

command="(/usr/local/bin/NGramToCFGTool.exe -i inter.arpa -t ARPA -o inter.cfg -b \"<s>\" -e \"</s>\" -l 2057 -r Top -sf W3C -inittag \"out={}; out.classsubstitution = gSubstitutions = [];\")"
output=`ssh $host2 $command`
scp -q $FAFR19:~/inter.cfg $slm_file

echo "Confirming existence of local files"
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

echo "Confirming existence of tools on $host"
echo

## Checking existence of Compile-tools
command="(Test-Path $installation_dir\\classifiermodelcompiler.exe\) -and (Test-Path $installation_dir\\cfgappend.exe) -and (Test-Path $installation_dir\\$required_dll)"
output=`ssh $host $command`
if [ ! output ]; then
    echo "Couldn't find $installation_dir\\classifiermodelcompiler.exe or $installation_dir\\cfgappend.exe or $installation_dir\\$required_dll"
    exit 1
fi

echo "Creating remote dir $tmp_dir and copying preparing for compilation"
echo

## Create tmp directory and copy the dll in that directory
command="New-Item -type "directory" $tmp_dir | Out-Null;Copy-Item $installation_dir\\$required_dll $tmp_dir | Out-Null;"
ssh $host $command;

echo "Copying files to $host:$tmp_dir"
echo

## Copy files to tmp directory
scp -q $slm_file $ssi_file $ssi_params_file $host:$tmp_dir 

echo "Compiling SSI"
echo


## Compile the SSI file
remote_slm_file=`basename $slm_file`
remote_ssi_file=`basename $ssi_file`
remote_ssi_params_file=`basename $ssi_params_file`
command="Push-Location $tmp_dir;$installation_dir\\classifiermodelcompiler.exe -m $remote_ssi_file -p $remote_ssi_params_file -o ssi.cfr;"
output=`ssh $host $command`

## Checking whether compiled SSI file was created or not. This step can be removed to improve speed
command="Test-path $tmp_dir\\ssi.cfr"
output=`ssh $host $command`
if [ ! output ]; then
    echo "Compiled SSI file couldn't be created: $tmp_dir\\ssi.cfr"
    exit 1
fi

echo "Compiling SSI with SLM"
echo

## Merging SSI and SLM models to form the final model
command="Push-Location $tmp_dir;$installation_dir\\cfgappend.exe $remote_slm_file ssi.cfr compiled_model.cfg;"
output=`ssh $host $command`

## Checking whether compiled model was created or not. This step can be removed to improve speed
command="Test-path $tmp_dir\\compiled_model.cfg"
output=`ssh $host $command`
if [ ! output ]; then
    echo "Model couldn't be created"
    exit 1
fi

CWD=`pwd`

echo "Copying compiled models to $CWD"
echo

## Copy model files to the current working directory
scp -q $host:$tmp_dir\\ssi.cfr $OUTDIR/ssi.cfr
scp -q $host:$tmp_dir\\compiled_model.cfg $OUTDIR/compiled_model.cfg

command="scp -q $host:$tmp_dir\\ssi.cfr $OUTDIR"

echo "Cleaning up $host for tmp files"
echo 

ssh $host Remove-Item -Force -Recurse $tmp_dir

echo `date` "Successfully finished !!"
