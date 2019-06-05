#!/bin/bash

# -- step 2: run Palisade to create plots

#palisade.py task zjet_excalibur plot_time_dependence \
#    --basename 'TimeDependence_Run2016BCDEFGH' \
#    --jec Summer16_V11 \
#    --sample 07Aug2017 \
#    --corr-levels "L1L2Res" \
#    --quantities {z,jet1,jet2,jet3}{pt,eta,phi} zmass met metphi mpf ptbalance rho npumean npv \
#    --run-periods Run2016{BCD,EFearly,FlateGH} \
#    --time-quantity "run2016" \
#    --channel "mm" "ee" \
#    --output-dir "plots" \
#    --output-format 'TimeDependence/{jec}/{sample}/{corr_level}/{channel}/{eta}/{quantity}_vs_{time_quantity}.png'


palisade.py task zjet_excalibur plot_time_dependence \
    --basename 'TimeDependence_Run2016BCDEFGH' \
    --jec Summer16_JECV11 \
    --sample 07Aug2017 \
    --corr-levels "L1L2L3" \
    --quantities {z,jet1,jet2,jet3}{pt,eta,phi} zmass met metphi mpf ptbalance rho npumean npv \
    --run-periods Run2016{B,C,D,E,F,G,H,BCDEFGH} \
    --time-quantity "run2016" \
    --channel "mm" "ee" \
    --output-dir "plots" \
    --output-format 'TimeDependence/{jec}/{sample}/{corr_level}/{channel}/{eta}/{quantity}_vs_{time_quantity}.png'

