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





echo "Processing input corpus to ARPA file"
echo "Processing input corpus to ARPA file"
output=`ssh $host1 bash $SRCDIR/convert_to_arpa.sh $2 $3`

