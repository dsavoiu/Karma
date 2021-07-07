#!/bin/sh


# Pythia
tag="QCD_PtBinned_TuneCUETP8M1_pythia8"
mkdir -p ${tag}
if [ ! -f "${proxy_file}" ]; then
  echo "[INFO] Making input proxy file for: $tag"
  python make_skim_tchain_proxy.py "${proxy_file}" \
    `pathsub_local_grid /storage/gridka-nrg/dsavoiu/Dijet/skims/KarmaSkim_QCD_Pt_*_2020-11-{12,15}/*.root`
else
  echo "[INFO] Skipping existing file '${proxy_file}'"
fi

# MadGraph
tag="QCD_HTBinned_madgraphMLM-pythia8"
mkdir -p ${tag}
proxy_file="${tag}/proxy.root"
if [ ! -f "${proxy_file}" ]; then
  echo "[INFO] Making input proxy file for: $tag"
  python make_skim_tchain_proxy.py "${proxy_file}" \
    `pathsub_local_grid /storage/gridka-nrg/dsavoiu/Dijet/skims/KarmaSkim_QCD_HT*_2020-09-15/*.root`
else
  echo "[INFO] Skipping existing file '${proxy_file}'"
fi
