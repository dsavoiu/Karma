#!/bin/sh

for tag in "QCD_PtBinned_TuneCUETP8M1_pythia8" "QCD_HTBinned_madgraphMLM-pythia8"; do
    proxy_file="${tag}/proxy.root"
    if [ ! -f "${proxy_file}" ]; then
        echo "[ERROR] Canot extract PU profile from skim '$tag': no proxy file found"
        continue
    fi
    mkdir -p ${tag}
    echo "[INFO] Extracting PU profile from skim: $tag"
    echo python make_pu_profile_ttree_draw.py \
        "${proxy_file}" \
        ${tag}/pileup_80bins_${tag}_FromSkim.root \
         -b80 -j20
done
