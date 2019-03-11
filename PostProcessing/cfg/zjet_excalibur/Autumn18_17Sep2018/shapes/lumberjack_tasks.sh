#!/bin/bash

# use a version of ROOT that has RDataFrames
source `which with_root_df`

# -- 2018

# -- step1: use Lumberjack to create ROOT files containing shapes from Excalibur TTrees
# Note: if these already exist, they are skipped, unless `--overwrite` flag is passed

# directory containing Excalibur TTree files
SAMPLE_DIR="/ceph/dsavoiu/JEC/Autumn18/17Sep2018_V5_2019-02-26"

for _ch in "mm" "ee"; do
    INFILE_DATA="${SAMPLE_DIR}/data18_${_ch}_ABCD_17Sep2018.root"
    INFILE_MC="${SAMPLE_DIR}/mc18_${_ch}_DYNJ_Madgraph.root"

    # -- MC
    for _corr_level in "L1L2L3"; do
        OUTPUT_FILE_SUFFIX="Z${_ch}_17Sep2018_Autumn18_JECV5_${_corr_level}"

        lumberjack.py -a zjet_excalibur -i "$INFILE_MC" \
            --selection "zpt" "alpha" \
            --tree "basiccuts_${_corr_level}/ntuple" \
            --type mc \
            -j10 \
            --log --progress \
            $@ \
            task Shape_MC \
            --output-file-suffix "$OUTPUT_FILE_SUFFIX"
    done

    # -- DATA (runs A, B, C with corr levels L1L2Res and L1L2L3)

    for _corr_level in "L1L2L3" "L1L2Res"; do
        OUTPUT_FILE_SUFFIX="Z${_ch}_17Sep2018_Autumn18_JECV5_${_corr_level}"

        lumberjack.py -a zjet_excalibur -i "$INFILE_DATA" \
            --selection "zpt" "alpha" \
            --tree "basiccuts_${_corr_level}/ntuple" \
            --type data \
            -j10 \
            --log --progress \
            $@ \
            task Shape_Run2018ABC \
            --output-file-suffix "$OUTPUT_FILE_SUFFIX"
    done

    # -- DATA (run D with corr level L1L2L3)

    for _corr_level in "L1L2L3"; do
        OUTPUT_FILE_SUFFIX="Z${_ch}_17Sep2018_Autumn18_JECV5_${_corr_level}"

        lumberjack.py -a zjet_excalibur -i "$INFILE_DATA" \
            --selection "zpt" "alpha" \
            --tree "basiccuts_${_corr_level}/ntuple" \
            --type data \
            -j10 \
            --log --progress \
            $@ \
            task Shape_Run2018D \
            --output-file-suffix "$OUTPUT_FILE_SUFFIX"
    done

    # -- merge ROOT files for runs ABC and D (only for correction level L1L2L3)
    hadd Shape_Run2018{ABCD,ABC,D}_Z${_ch}_17Sep2018_Autumn18_JECV5_L1L2L3.root
done
