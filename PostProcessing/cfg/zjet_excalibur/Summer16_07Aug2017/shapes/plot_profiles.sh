#!/bin/bash

# import common configuration for sample
source ../common.sh


# -- step 2: run Palisade to create profile plots

palisade.py task zjet_excalibur plot_profiles \
    --basename-mc 'ProfileZPt_RunMC_EtaBins' \
    --basename-data 'ProfileZPt_IOV2016_EtaBins' \
    --jec "${SAMPLE_JECV_NAME}" \
    --sample "${SAMPLE_BASE_NAME}" \
    --corr-levels "L1L2L3" "L1L2L3Res" "L1L2Res" \
    --split-quantity "eta" \
    --quantity-pairs zpt:{jet1,jet2}pt zpt:{zmass,met,mpf,ptbalance,alpha,jet12DeltaR} \
    --run-periods $SAMPLE_IOVS $SAMPLE_IOV_WHOLEYEAR \
    --channel "mm" "ee" \
    --output-dir "plots" \
    --output-format 'Profiles/{jec}/{sample}/{corr_level}/{channel}/{split}/{quantity_pair}.png'

palisade.py task zjet_excalibur plot_profiles \
    --basename-mc 'ProfileEta_RunMC_ZPtBins' \
    --basename-data 'ProfileEta_IOV2016_ZPtBins' \
    --jec "${SAMPLE_JECV_NAME}" \
    --sample "${SAMPLE_BASE_NAME}" \
    --corr-levels "L1L2L3" "L1L2L3Res" "L1L2Res" \
    --split-quantity "zpt" \
    --quantity-pairs absjet1eta:{jet1,jet2}pt absjet1eta:{zmass,met,mpf,ptbalance,alpha,jet12DeltaR} \
    --run-periods $SAMPLE_IOVS $SAMPLE_IOV_WHOLEYEAR \
    --channel "mm" "ee" \
    --output-dir "plots" \
    --output-format 'Profiles/{jec}/{sample}/{corr_level}/{channel}/{split}/{quantity_pair}.png'
