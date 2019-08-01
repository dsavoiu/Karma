#!/bin/bash

# use a version of ROOT that has RDataFrames
source `which with_root_df`

# import common configuration for sample
source ../common.sh


for _ch in "mm" "ee"; do

    INFILE_DATA="${SAMPLE_DIR}/data17_${_ch}_BCDEF_17Nov2017.root"

    for _corr_level in "L1L2L3" "L1L2Res"; do
        OUTPUT_FILE_SUFFIX="Z${_ch}_${SAMPLE_NAME}_${_corr_level}"

        lumberjack.py -a zjet_excalibur -i "$INFILE_DATA" \
            --selection "zpt" "alpha" \
            --tree "basiccuts_${_corr_level}/ntuple" \
            --input-type data \
            -j10 \
            --log --progress \
            $@ \
            task TimeDependence_IOV2017 \
            --output-file-suffix "$OUTPUT_FILE_SUFFIX"
    done

done
