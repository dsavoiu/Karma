#!/bin/bash

# use a version of ROOT that has RDataFrames
source `which with_root_df`

# -- 2017

# -- step1: use Lumberjack to create ROOT files containing shapes from Excalibur TTrees
# Note: if these already exist, they are skipped, unless `--overwrite` flag is passed

# directory containing Excalibur TTree files
SAMPLE_DIR="/ceph/dsavoiu/JEC/Fall17/17Nov2017_V31_2018-10-26"

for _ch in "mm" "ee"; do
    INFILE_DATA="${SAMPLE_DIR}/data17_${_ch}_BCDEF_17Nov2017.root"
    INFILE_MC="${SAMPLE_DIR}/mc17_${_ch}_DYNJ_Madgraph.root"

    # -- MC
    for _corr_level in "L1L2L3"; do
        OUTPUT_FILE_SUFFIX="Z${_ch}_17Nov2017_Fall17_JECV31_${_corr_level}"

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

    # -- DATA

    for _corr_level in "L1L2L3" "L1L2Res" "L1L2L3Res"; do
        OUTPUT_FILE_SUFFIX="Z${_ch}_17Nov2017_Fall17_JECV31_${_corr_level}"

        lumberjack.py -a zjet_excalibur -i "$INFILE_DATA" \
            --selection "zpt" "alpha" \
            --tree "basiccuts_${_corr_level}/ntuple" \
            --type data \
            -j10 \
            --log --progress \
            $@ \
            task Shape_Run2017BCDEF \
            --output-file-suffix "$OUTPUT_FILE_SUFFIX"
    done

done
