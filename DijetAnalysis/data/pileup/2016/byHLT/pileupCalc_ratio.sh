#!/bin/bash

for t in 60 80 140 200 260 320 400 500; do
    ../../../../scripts/pu_reweighting.py datamc_pu_weights \
      -d "nPUMean_data_HLT_DiPFJetAve${t}.root" \
      -m "../nPUMean_mc.root" \
      -o "nPUMean_ratio_HLT_DiPFJetAve${t}.root"
done
