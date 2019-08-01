#!/bin/bash

# import common configuration for sample
source ../common.sh


# -- step 2: run Palisade to create plots


palisade.py task zjet_excalibur plot_time_dependence \
    --basename 'TimeDependence_IOV2017' \
    --jec "${SAMPLE_JECV_NAME}" \
    --sample "${SAMPLE_BASE_NAME}" \
    --corr-levels "L1L2L3" \
    --quantities {z,jet1,jet2,jet3}{pt,eta,phi} zmass met metphi mpf ptbalance rho npumean npv \
    --run-periods $SAMPLE_IOVS \
    --time-quantity "run2017" \
    --channel "mm" "ee" \
    --output-dir "plots" \
    --output-format 'TimeDependence/{jec}/{sample}/{corr_level}/{channel}/{eta}/{quantity}_vs_{time_quantity}.png'

