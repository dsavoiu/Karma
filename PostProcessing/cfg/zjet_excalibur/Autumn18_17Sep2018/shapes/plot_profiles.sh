#!/bin/bash

# -- step 2: run Palisade to create profile plots

# -- correction level 'L1L2L3' available for all runs periods (A--D)
palisade.py task zjet_excalibur plot_profiles \
    --basename-mc 'Shape_MC' \
    --basename-data 'Shape_Run2018ABCD' \
    --jec Autumn18_JECV5 \
    --sample 17Sep2018 \
    --corr-levels "L1L2L3" \
    --quantity-pairs zpt:{jet1,jet2}pt zpt:{zmass,met,mpf,ptbalance} \
    --run-periods Run2018{A,B,C,D} \
    --channel "mm" "ee" \
    --output-dir "plots" \
    --output-format 'Profiles/{jec}/{sample}/{corr_level}/{channel}/{eta}/{quantity_pair}.png'


palisade.py task zjet_excalibur plot_profiles \
    --basename-mc 'Shape_MC' \
    --basename-data 'Shape_Run2018ABC' \
    --jec Autumn18_JECV5 \
    --sample 17Sep2018 \
    --corr-levels "L1L2Res" \
    --quantity-pairs zpt:{jet1,jet2}pt zpt:{zmass,met,mpf,ptbalance} \
    --run-periods Run2018{A,B,C} \
    --channel "mm" "ee" \
    --output-dir "plots" \
    --output-format 'Profiles/{jec}/{sample}/{corr_level}/{channel}/{eta}/{quantity_pair}.png'
