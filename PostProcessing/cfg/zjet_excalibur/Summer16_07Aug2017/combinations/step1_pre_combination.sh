#!/bin/bash

# use a version of ROOT that has RDataFrames
source `which with_root_df`

# -- 2016

# -- step1: use Lumberjack to create "pre-combination" files from Excalibur TTrees
# Note: if these already exist, they are skipped, unless `--overwrite` flag is passed

SAMPLE_DIR="/portal/ekpbms3/home/tfesenbecker/excalibur_work/merged"

for _ch in "mm" "ee"; do
    INFILE_DATA="${SAMPLE_DIR}/data16_${_ch}_BCDEFGH_07Aug2017.root"
    INFILE_MC="${SAMPLE_DIR}/mc16_${_ch}_BCDEFGH_DYJets_Madgraph.root"

    # -- MC
    for _corr_level in "L1L2L3"; do
        OUTPUT_FILE_SUFFIX="Z${_ch}_07Aug2017_Summer16_JECV11_L1L2L3"

        lumberjack.py -a zjet_excalibur -i "$INFILE_MC" \
            --tree "basiccuts_L1L2L3/ntuple" \
            --input-type mc \
            -j10 \
            --log --progress \
            $@ \
            task CombinationMC \
            --output-file-suffix "$OUTPUT_FILE_SUFFIX"
    done

    # -- DATA (runs B, C, D, E, F, G, H with corr level L1L2L3)

    for _corr_level in "L1L2L3"; do
        OUTPUT_FILE_SUFFIX="Z${_ch}_07Aug2017_Summer16_JECV11_${_corr_level}"

        lumberjack.py -a zjet_excalibur -i "$INFILE_DATA" \
            --tree "basiccuts_${_corr_level}/ntuple" \
            --input-type data \
            -j10 \
            --log --progress \
            $@ \
            task CombinationData2016BCDEFGH \
            --output-file-suffix "$OUTPUT_FILE_SUFFIX"
    done


done
