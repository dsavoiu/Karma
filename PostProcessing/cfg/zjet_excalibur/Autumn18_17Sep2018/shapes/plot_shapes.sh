#!/bin/bash

# import common configuration for sample
source ../common.sh


# -- step 2: run Palisade to create shape plots

palisade.py task zjet_excalibur plot_shapes \
    --basename-mc 'Shape_RunMC_EtaBins_ZPtBins' \
    --basename-data 'Shape_IOV2018_EtaBins_ZPtBins' \
    --jec "${SAMPLE_JECV_NAME}" \
    --sample "${SAMPLE_BASE_NAME}" \
    --corr-levels "L1L2L3" "L1L2L3Res" "L1L2Res" \
    --split-quantity "eta" \
    --quantities {z,jet1,jet2,jet3}{pt,eta,phi} zmass met metphi mpf ptbalance rho npumean npv {zJet1,jet12}Delta{Phi,R} \
    --run-periods $SAMPLE_IOVS $SAMPLE_IOV_WHOLEYEAR \
    --channel "mm" "ee" \
    --output-dir "plots" \
    --output-format 'Shapes/{jec}/{sample}/{corr_level}/{channel}/{split}/{quantity}.png'
