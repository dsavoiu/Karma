#!/bin/bash

# -- step 2: run Palisade to combine the "pre-combination" files to the full
# combination files for submission to JEC

palisade.py task zjet_excalibur combination \
    --basename-data 'CombinationData2018ABC' \
    --basename-mc 'CombinationMC' \
    --jec Autumn18_JECV5 \
    --sample 17Sep2018 \
    --corr-levels "L1L2Res" \
    --run-periods Run2018{A,B,C,ABC} \
    --channel "mm" "ee" \
    --output-dir full_combination

palisade.py task zjet_excalibur combination \
    --basename-data 'CombinationData2018ABCD' \
    --basename-mc 'CombinationMC' \
    --jec Autumn18_JECV5 \
    --sample 17Sep2018 \
    --corr-levels "L1L2L3" \
    --run-periods Run2018{A,B,C,D,ABCD} \
    --channel "mm" "ee" \
    --output-dir full_combination
