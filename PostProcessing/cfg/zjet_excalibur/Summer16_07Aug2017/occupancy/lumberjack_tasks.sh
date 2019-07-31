#!/bin/bash

# use a version of ROOT that has RDataFrames
source `which with_root_df`

# import common configuration for sample
source ../common.sh


for _ch in "mm" "ee"; do
    INFILE_DATA="${SAMPLE_DIR}/data16_${_ch}_BCDEFGH_07Aug2017.root"
    INFILE_MC="${SAMPLE_DIR}/mc16_${_ch}_BCDEFGH_DYJets_Madgraph.root"

    _corr_level="L1L2L3Res"

    # -- MC

    OUTPUT_FILE_SUFFIX="Z${_ch}_${SAMPLE_NAME}_${_corr_level}"

    lumberjack.py -a zjet_excalibur -i "$INFILE_MC" \
        --selection "zpt" "alpha" \
        --tree "basiccuts_${_corr_level}/ntuple" \
        --input-type mc \
        -j20 \
        --log --progress --dump-yaml \
        $@ \
        task Occupancy_RunMC_EtaBins_ZPtBins \
        --output-file-suffix "$OUTPUT_FILE_SUFFIX"

    # -- DATA

    OUTPUT_FILE_SUFFIX="Z${_ch}_${SAMPLE_NAME}_${_corr_level}"

    lumberjack.py -a zjet_excalibur -i "$INFILE_DATA" \
        --selection "zpt" "alpha" \
        --tree "basiccuts_${_corr_level}/ntuple" \
        --input-type data \
        -j20 \
        --log --progress --dump-yaml \
        $@ \
        task Occupancy_IOV2016_EtaBins_ZPtBins \
        --output-file-suffix "$OUTPUT_FILE_SUFFIX"

done