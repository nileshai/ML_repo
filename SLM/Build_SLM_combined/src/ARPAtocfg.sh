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
FAFR19=$USER@$host2

scp -q $INTERARPA $FAFR19:~/

command="(/usr/local/bin/NGramToCFGTool.exe -i inter.arpa -t ARPA -o inter.cfg -b \"<s>\" -e \"</s>\" -l 1033 -r Top -sf W3C -inittag \"out={}; out.classsubstitution = gSubstitutions = [];\")"
output=`ssh $host2 $command`
scp -q $FAFR19:~/inter.cfg $slm_file

