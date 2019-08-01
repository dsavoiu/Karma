#!/bin/bash

# use a version of ROOT that has RDataFrames
source `which with_root_df`

# import common configuration for sample
source ../common.sh


# -- step1: use Lumberjack to create "pre-combination" files from Excalibur TTrees
# Note: if these already exist, they are skipped, unless `--overwrite` flag is passed


for _ch in "mm" "ee"; do
    INFILE_DATA="${SAMPLE_DIR}/data17_${_ch}_BCDEF_17Nov2017.root"
    INFILE_MC="${SAMPLE_DIR}/mc17_${_ch}_BCDEF_DYJets_Madgraph.root"

    # -- MC
    for _corr_level in "L1L2L3"; do
        OUTPUT_FILE_SUFFIX="Z${_ch}_${SAMPLE_NAME}_L1L2L3"

        lumberjack.py -a zjet_excalibur -i "$INFILE_MC" \
            --tree "basiccuts_L1L2L3/ntuple" \
            --input-type mc \
            -j20 \
            --log --progress \
            $@ \
            task Combination_RunMC \
            --output-file-suffix "$OUTPUT_FILE_SUFFIX"
    done

    # -- DATA

    for _corr_level in "L1L2L3" "L1L2Res" "L1L2L3Res"; do
        OUTPUT_FILE_SUFFIX="Z${_ch}_${SAMPLE_NAME}_${_corr_level}"

        lumberjack.py -a zjet_excalibur -i "$INFILE_DATA" \
            --tree "basiccuts_${_corr_level}/ntuple" \
            --input-type data \
            -j20 \
            --log --progress \
            $@ \
            task Combination_IOV2017 \
            --output-file-suffix "$OUTPUT_FILE_SUFFIX"
    done

done
