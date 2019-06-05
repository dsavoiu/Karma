#!/bin/bash

# -- step 2: run Palisade to combine the "pre-combination" files to the full
# combination files for submission to JEC

#palisade.py task zjet_excalibur combination \
#    --basename-data 'CombinationData2016BCDEFGH' \
#    --basename-mc 'CombinationMC' \
#    --jec Summer16_JECV11 \
#    --sample 07Aug2017 \
#    --corr-levels "L1L2Res" \
#    --run-periods IOV2016{BCD,EFearly, FlateGH} \
#    --channel "mm" "ee" \
#    --output-dir full_combination

palisade.py task zjet_excalibur combination \
    --basename-data 'CombinationData2016BCDEFGH' \
    --basename-mc 'CombinationMC' \
    --jec Summer16_JECV11\
    --sample 07Aug2017 \
    --corr-levels "L1L2L3" \
    --run-periods Run2016{BCD,EFearly,FlateGH,BCDEFGH} \
    --channel "mm" "ee" \
    --output-dir full_combination
