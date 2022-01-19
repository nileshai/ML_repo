for var in 1 2 3 4 5
do
    echo "Building the Combined SLM-SSI model for Fold_$var"
    train_file="corpus_$var"
    ssi_file="ssi_$var"
    sed "s/corpus_1/$train_file/g" ModelCompiler.cfg > temp.cfg
    sed "s/ssi_1/$ssi_file/g" temp.cfg > tempCompiler.cfg
    rm temp.cfg
    bash src/ModelCompilerV2.sh tempCompiler.cfg
    mv Output/compiled_model.cfg SLM_SSI_combined/Fold_$var.cfg
    mv Output/ssi.cfr SLM_SSI_combined/ssi_$var.cfr
    mv Inter/inter.arpa SLM_SSI_combined/Additional-Files/inter_$var.arpa
    mv Inter/inter.cfg SLM_SSI_combined/Additional-Files/inter_$var.cfg
    rm tempCompiler.cfg
    echo "Transferred model files to Target destination"
done
cp ModelCompiler.cfg SLM_SSI_combined/Additional-Files/
cp Input/classifier_params SLM_SSI_combined/Additional-Files/
cp Input/substitutions_ML-WMCS_class_1099.txt SLM_SSI_combined/Additional-Files/
rm -r Inter/ Output/
