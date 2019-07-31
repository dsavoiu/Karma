#!/bin/bash

# use a version of ROOT that has RDataFrames
source `which with_root_df`

# import common configuration for sample
source ../common.sh


for _ch in "mm" "ee"; do
    INFILE_DATA="${SAMPLE_DIR}/data16_${_ch}_BCDEFGH_07Aug2017.root"
    INFILE_MC="${SAMPLE_DIR}/mc16_${_ch}_BCDEFGH_DYJets_Madgraph.root"

    # -- MC

    for _corr_level in "L1L2L3"; do
        OUTPUT_FILE_SUFFIX="Z${_ch}_${SAMPLE_NAME}_${_corr_level}"

        lumberjack.py -a zjet_excalibur -i "$INFILE_MC" \
            --selection "zpt" "alpha" \
            --tree "basiccuts_${_corr_level}/ntuple" \
            --input-type mc \
            -j15 \
            --log --progress --dump-yaml \
            $@ \
            task Extrapolation_RunMC_EtaBins_ZPtBins \
            --output-file-suffix "$OUTPUT_FILE_SUFFIX"
    done

    # -- DATA

    for _corr_level in "L1L2L3" "L1L2Res" "L1L2L3Res"; do
        OUTPUT_FILE_SUFFIX="Z${_ch}_${SAMPLE_NAME}_${_corr_level}"

        lumberjack.py -a zjet_excalibur -i "$INFILE_DATA" \
            --selection "zpt" "alpha" \
            --tree "basiccuts_${_corr_level}/ntuple" \
            --input-type data \
            -j15 \
            --log --progress --dump-yaml \
            $@ \
            task Extrapolation_IOV2016_EtaBins_ZPtBins \
            --output-file-suffix "$OUTPUT_FILE_SUFFIX"

    done
done
