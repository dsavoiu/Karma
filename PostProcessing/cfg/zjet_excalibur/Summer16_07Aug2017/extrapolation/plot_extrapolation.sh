#!/usr/bin/env bash

palisade.py task zjet_excalibur plot_profiles \
    --basename-mc 'Extrapolation_MC' \
    --basename-data 'Extrapolation_IOV2016' \
    --jec Summer16_JECV11 \
    --sample 07Aug2017 \
    --corr-levels "L1L2L3" \
    --quantity-pairs  alpha:zmass \
    --run-periods IOV2016{BCD,EFearly, FlateGH} \
    --channel "mm" "ee" \
    --output-dir "plots" \
    --output-format 'Profiles/{jec}/{sample}/{corr_level}/{channel}/{eta}/{quantity_pair}.png'


# alpha:{z,jet1,jet2,jet3}{pt,eta,phi}
#,met,metphi,mpf,ptbalance,rho,npumean,npv