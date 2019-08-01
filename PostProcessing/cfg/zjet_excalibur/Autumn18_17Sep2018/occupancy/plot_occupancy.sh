#!/usr/bin/env bash

# import common configuration for sample
source ../common.sh


palisade.py task zjet_excalibur plot_occupancy \
    --basename-data 'Occupancy_IOV2018_EtaBins_ZPtBins' \
    --basename-mc 'Occupancy_RunMC_EtaBins_ZPtBins' \
    --jec "${SAMPLE_JECV_NAME}" \
    --sample "${SAMPLE_BASE_NAME}" \
    --corr-levels "L1L2L3Res" \
    --quantity-pairs  \
                      jet1eta:jet1phi jet2eta:jet2phi jet3eta:jet3phi zeta:zphi \
                      jet1pt:jet1eta  jet2pt:jet2eta  jet3pt:jet3eta  zpt:zeta \
                      jet12DeltaEta:jet12DeltaPhi     zJet1DeltaEta:zJet1DeltaPhi \
    --run-periods $SAMPLE_IOVS \
    --channel "mm" "ee" \
    --output-dir "plots" \
    --output-format 'Occupancy/{jec}/{sample}/{channel}/{run_period}/{split}/{quantity_pair}_{source}.png'
