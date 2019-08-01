#!/bin/bash

# import common configuration for sample
source ../common.sh


# -- step 2: run Palisade to combine the "pre-combination" files to the full
# combination files for submission to JEC

palisade.py task zjet_excalibur combination \
    --basename-data 'Combination_IOV2018' \
    --basename-mc 'Combination_RunMC' \
    --jec "${SAMPLE_JECV_NAME}" \
    --sample "${SAMPLE_BASE_NAME}" \
    --corr-levels "L1L2L3" "L1L2Res" \
    --run-periods $SAMPLE_IOVS $SAMPLE_IOV_WHOLEYEAR Run2018ABC \
    --channel "mm" "ee" \
    --output-dir full_combination
