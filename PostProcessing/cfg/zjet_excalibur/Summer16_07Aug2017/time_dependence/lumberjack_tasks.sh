#!/bin/bash

# use a version of ROOT that has RDataFrames
source `which with_root_df`

# -- 2018

# -- step1: use Lumberjack to create ROOT files containing shapes from Excalibur TTrees
# Note: if these already exist, they are skipped, unless `--overwrite` flag is passed

# directory containing Excalibur TTree files
SAMPLE_DIR="/portal/ekpbms3/home/tfesenbecker/excalibur_work/merged"

for _ch in "mm" "ee"; do

     INFILE_DATA="${SAMPLE_DIR}/data16_${_ch}_BCDEFGH_07Aug2017.root"

    # -- DATA (runs A, B, C with corr levels L1L2Res and L1L2L3)

    for _corr_level in "L1L2L3" "L1L2Res"; do
        OUTPUT_FILE_SUFFIX="Z${_ch}_07Aug2017_Summer16_JECV11_${_corr_level}"

        lumberjack.py -a zjet_excalibur -i "$INFILE_DATA" \
            --selection "zpt" "alpha" \
            --tree "basiccuts_${_corr_level}/ntuple" \
            --input-type data \
            -j10 \
            --log --progress \
            $@ \
            task TimeDependence_Run2016BCDEFGH \
            --output-file-suffix "$OUTPUT_FILE_SUFFIX"
    done



#    # -- merge ROOT files for runs ABC and D (only for correction level L1L2L3)
#    if [ ! -f TimeDependence_Run2018ABCD_Z${_ch}_17Sep2018_Autumn18_JECV5_L1L2L3.root ]; then
#        hadd TimeDependence_Run2018{ABCD,ABC,D}_Z${_ch}_17Sep2018_Autumn18_JECV5_L1L2L3.root
#    fi

done
