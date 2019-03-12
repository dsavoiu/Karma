#!/bin/bash

# -- step 2: run Palisade to create shape plots

palisade.py task zjet_excalibur plot_shapes \
    --basename-mc 'Shape_MC' \
    --basename-data 'Shape_Run2017BCDEF' \
    --jec Fall17_JECV31 \
    --sample 17Nov2017 \
    --corr-levels "L1L2L3" "L1L2L3Res" "L1L2Res" \
    --quantities {z,jet1,jet2,jet3}{pt,eta,phi} zmass met metphi mpf ptbalance rho npumean npv \
    --run-periods Run2017{B,C,D,E,F} \
    --channel "mm" "ee" \
    --output-dir "plots" \
    --output-format 'Shapes/{jec}/{sample}/{corr_level}/{channel}/{eta}/{quantity}.png'
