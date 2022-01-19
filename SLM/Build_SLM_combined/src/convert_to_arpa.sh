export LD_LIBRARY_PATH=/platinum/libgcc-3_4_3-1.i386.solaris.5_10/lib/:$LD_LIBRARY_PATH
#/rap/slm_tools/srilm-170/bin/i386-solaris/ngram-count -text $1 -text-has-weights -ndiscount -lm $2
#/rap/slm_tools/srilm-170/bin/i386-solaris/ngram-count -order 3 -text-has-weights $1 -ndiscount -lm $2
#/rap/slm_tools/srilm-170/bin/i386-solaris/ngram-count -order 3 -text-has-weights -no-sos -no-eos -text $1 -ndiscount -lm $2 -gt1min 1 -gt2min 1 -gt3min 1 -minprune 3
#regular slm compilation
#/rap/slm_tools/srilm-170/bin/i386-solaris/ngram-count -order 3 -text $1 -ndiscount -lm $2
####Kneser Ney
#temp="$2_temp"
#echo "normalized data used is $1 ,arpa file is $2"
#echo  "temp is $temp"
#/rap/slm_tools/srilm-170/bin/i386-solaris/ngram-count -kndiscount -order 3 -text $1 -interpolate -lm $temp
/rap/slm_tools/srilm-170/bin/i386-solaris/ngram-count -kndiscount -order 3 -text $1 -interpolate -lm $2

# add-dummy-bows --
#   add redundant backoff weights to model file to make some broken
#   programs happy.
#   (Normally a backoff weight is only required for ngrams that
#   are prefixes of longer ngrams.)
#
#/rap/slm_tools/srilm-170/bin/i386-solaris/add-dummy-bows $temp > $2
#echo "removing $temp"
#rm $temp
