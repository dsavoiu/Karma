#!/bin/bash

# use a version of ROOT that has RDataFrames
source `which with_root_df`

# import common configuration for sample
source ../common.sh


for _ch in "mm" "ee"; do
    INFILE_DATA="${SAMPLE_DIR}/data16_${_ch}_BCDEFGH_07Aug2017.root"
    INFILE_MC="${SAMPLE_DIR}/mc16_${_ch}_BCDEFGH_DYJets_Madgraph.root"

    for _basetask in "Profile" "Shape"; do

        # -- MC

        if [ "${_basetask}" == "Profile" ]; then
            _tasklist="ProfileZPt_RunMC_EtaBins ProfileEta_RunMC_ZPtBins"
        else
            _tasklist="${_basetask}_RunMC_EtaBins_ZPtBins"
        fi

        for _corr_level in "L1L2L3"; do
            OUTPUT_FILE_SUFFIX="Z${_ch}_${SAMPLE_NAME}_${_corr_level}"

            lumberjack.py -a zjet_excalibur -i "$INFILE_MC" \
                --selection "zpt" "alpha" \
                --tree "basiccuts_${_corr_level}/ntuple" \
                --input-type mc \
                -j15 \
                --log --progress --dump-yaml \
                $@ \
                task $_tasklist \
                --output-file-suffix "$OUTPUT_FILE_SUFFIX"
        done

        # -- DATA

        if [ "${_basetask}" == "Profile" ]; then
            _tasklist="ProfileZPt_IOV2016_EtaBins ProfileEta_IOV2016_ZPtBins"
        else
            _tasklist="${_basetask}_IOV2016_EtaBins_ZPtBins"
        fi

        for _corr_level in "L1L2L3" "L1L2Res" "L1L2L3Res"; do
            OUTPUT_FILE_SUFFIX="Z${_ch}_${SAMPLE_NAME}_${_corr_level}"

            lumberjack.py -a zjet_excalibur -i "$INFILE_DATA" \
                --selection "zpt" "alpha" \
                --tree "basiccuts_${_corr_level}/ntuple" \
                --input-type data \
                -j15 \
                --log --progress --dump-yaml \
                $@ \
                task $_tasklist \
                --output-file-suffix "$OUTPUT_FILE_SUFFIX"

        done
    done
done
