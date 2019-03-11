#!/bin/bash

# -- step 2: run Palisade to create shape plots

# -- correction level 'L1L2L3' available for all runs periods (A--D)
palisade.py task zjet_excalibur plot_shapes \
    --basename-mc 'Shape_MC' \
    --basename-data 'Shape_Run2018ABCD' \
    --jec Autumn18_JECV5 \
    --sample 17Sep2018 \
    --corr-levels "L1L2L3" \
    --quantities {z,jet1,jet2,jet3}{pt,eta,phi} zmass met metphi mpf ptbalance rho npumean npv \
    --run-periods Run2018{A,B,C,D} \
    --channel "mm" "ee" \
    --output-dir "plots" \
    --output-format 'Shapes/{jec}/{sample}/{corr_level}/{channel}/{eta}/{quantity}.png'


# -- correction level 'L1L2Res' only available for runs A--C
palisade.py task zjet_excalibur plot_shapes \
    --basename-mc 'Shape_MC' \
    --basename-data 'Shape_Run2018ABC' \
    --jec Autumn18_JECV5 \
    --sample 17Sep2018 \
    --corr-levels "L1L2Res" \
    --quantities {z,jet1,jet2,jet3}{pt,eta,phi} zmass met metphi mpf ptbalance rho npumean npv \
    --run-periods Run2018{A,B,C} \
    --channel "mm" "ee" \
    --output-dir "plots" \
    --output-format 'Shapes/{jec}/{sample}/{corr_level}/{channel}/{eta}/{quantity}.png'
