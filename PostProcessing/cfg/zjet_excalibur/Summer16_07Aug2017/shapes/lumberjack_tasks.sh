#!/bin/bash

# use a version of ROOT that has RDataFrames
source `which with_root_df`

# -- 2016

# -- step1: use Lumberjack to create ROOT files containing shapes from Excalibur TTrees
# Note: if these already exist, they are skipped, unless `--overwrite` flag is passed

# directory containing Excalibur TTree files
SAMPLE_DIR="/portal/ekpbms3/home/tfesenbecker/excalibur_work/merged"

for _ch in "mm" "ee"; do
    INFILE_DATA="${SAMPLE_DIR}/data16_${_ch}_BCDEFGH_07Aug2017.root"
    INFILE_MC="${SAMPLE_DIR}/mc16_${_ch}_BCDEFGH_DYJets_Madgraph.root"

    # -- MC
    for _corr_level in "L1L2L3"; do
        OUTPUT_FILE_SUFFIX="Z${_ch}_07Aug2017_Summer16_JECV11_${_corr_level}"
        echo $INFILE_MC

        lumberjack.py -a zjet_excalibur -i "$INFILE_MC" \
            --selection "zpt" "alpha" \
            --tree "basiccuts_${_corr_level}/ntuple" \
            --input-type mc \
            -j10 \
            --log --progress \
            $@ \
            task Shape_MC \
            --output-file-suffix "$OUTPUT_FILE_SUFFIX"
    done

    # -- DATA

    for _corr_level in "L1L2L3" "L1L2Res" "L1L2L3Res"; do
        OUTPUT_FILE_SUFFIX="Z${_ch}_07Aug2017_Summer16_JECV11_${_corr_level}"

        lumberjack.py -a zjet_excalibur -i "$INFILE_DATA" \
            --selection "zpt" "alpha" \
            --tree "basiccuts_${_corr_level}/ntuple" \
            --input-type data \
            -j10 \
            --log --progress \
            $@ \
            task Shape_IOV2016BCDEFGH \
            --output-file-suffix "$OUTPUT_FILE_SUFFIX"
    done

done
