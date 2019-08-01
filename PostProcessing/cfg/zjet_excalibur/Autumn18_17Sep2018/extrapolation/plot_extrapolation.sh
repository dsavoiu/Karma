#!/usr/bin/env bash

# import common configuration for sample
source ../common.sh


palisade.py task zjet_excalibur plot_extrapolation \
    --basename-mc 'Extrapolation_RunMC_EtaBins_ZPtBins' \
    --basename-data 'Extrapolation_IOV2018_EtaBins_ZPtBins' \
    --jec "${SAMPLE_JECV_NAME}" \
    --sample "${SAMPLE_BASE_NAME}" \
    --corr-levels "L1L2L3" "L1L2L3Res" "L1L2Res" \
    --split-quantity "eta" \
    --quantity-pairs  alpha:{mpf,ptbalance} alpha:jet12Delta{Eta,Phi,R} \
    --run-periods $SAMPLE_IOVS \
    --channel "mm" "ee" \
    --output-dir "plots" \
    --output-format 'Extrapolation/{jec}/{sample}/{corr_level}/{channel}/{split}/{quantity_pair}.png'
