#!/bin/bash

# -- step 2: run Palisade to create plots

palisade.py task zjet_excalibur plot_time_dependence \
    --basename 'TimeDependence_Run2018ABC' \
    --jec Autumn18_JECV5 \
    --sample 17Sep2018 \
    --corr-levels "L1L2Res" \
    --quantities {z,jet1,jet2,jet3}{pt,eta,phi} zmass met metphi mpf ptbalance rho npumean npv \
    --run-periods Run2018{A,B,C} \
    --time-quantity "run2018" \
    --channel "mm" "ee" \
    --output-dir "plots" \
    --output-format 'TimeDependence/{jec}/{sample}/{corr_level}/{channel}/{eta}/{quantity}_vs_{time_quantity}.png'


palisade.py task zjet_excalibur plot_time_dependence \
    --basename 'TimeDependence_Run2018ABCD' \
    --jec Autumn18_JECV5 \
    --sample 17Sep2018 \
    --corr-levels "L1L2L3" \
    --quantities {z,jet1,jet2,jet3}{pt,eta,phi} zmass met metphi mpf ptbalance rho npumean npv \
    --run-periods Run2018{A,B,C,D} \
    --time-quantity "run2018" \
    --channel "mm" "ee" \
    --output-dir "plots" \
    --output-format 'TimeDependence/{jec}/{sample}/{corr_level}/{channel}/{eta}/{quantity}_vs_{time_quantity}.png'

