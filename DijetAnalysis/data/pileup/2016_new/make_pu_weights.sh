#!/bin/sh
_in_files=""
_out_files=""
for t in HLT_All HLT_{,AK8}PFJet{40,60,80,140,200,260,320,400,450,500,_All} HLT_DiPFJetAve{40,60,80,140,200,260,320,400,500,_All}; do
    _in_files="${_in_files} Run2016BCDEFGH_07Aug17/pileup_80bins_Run2016BCDEFGH_07Aug17_Nominal_${t}.root"
    _out_files="${_out_files} Run2016BCDEFGH_07Aug17/pileupWeights_80bins_Run2016BCDEFGH_07Aug17_Nominal_${t}.root"
done

python make_pu_weights.py \
    -d $_in_files \
    -m QCD_PtBinned_TuneCUETP8M1_pythia8/pileup_80bins_QCD_PtBinned_TuneCUETP8M1_pythia8_FromSkim.root \
    -o $_out_files \
    --output-dir .
