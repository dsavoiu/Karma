#!/bin/sh

# -- DiPFJetAve

_in_files=""
_labels=""
_colors=""
for kt in HLT_All:k HLT_DiPFJetAve{40:indigo,60:navy,80:blue,140:forestgreen,200:darkgoldenrod,260:orange,320:darkorange,400:red,500:darkred,_All:gray}; do
    t=${kt%:*}
    c=${kt#*:}
    _in_files="${_in_files} Run2016BCDEFGH_07Aug17/pileup_80bins_Run2016BCDEFGH_07Aug17_Nominal_${t}.root"
    _labels="${_labels} ${t}"
    _colors="${_colors} ${c}"
done

python plot_pu_weights.py \
    -d $_in_files \
    -m "QCD_PtBinned_TuneCUETP8M1_pythia8/pileup_80bins_QCD_PtBinned_TuneCUETP8M1_pythia8_FromSkim.root" \
    -l ${_labels} \
    -c ${_colors} \
    -o "pu_weights_DiPFJetAve.png" \
    --output-dir "Run2016BCDEFGH_07Aug17"

# -- PFJet

_in_files=""
_labels=""
_colors=""
for kt in HLT_All:k HLT_PFJet{40:indigo,60:navy,80:blue,140:forestgreen,200:darkgoldenrod,260:orange,320:darkorange,400:red,450:pink,500:darkred,_All:gray}; do
    t=${kt%:*}
    c=${kt#*:}
    _in_files="${_in_files} Run2016BCDEFGH_07Aug17/pileup_80bins_Run2016BCDEFGH_07Aug17_Nominal_${t}.root"
    _labels="${_labels} ${t}"
    _colors="${_colors} ${c}"
done

python plot_pu_weights.py \
    -d $_in_files \
    -m "QCD_PtBinned_TuneCUETP8M1_pythia8/pileup_80bins_QCD_PtBinned_TuneCUETP8M1_pythia8_FromSkim.root" \
    -l ${_labels} \
    -c ${_colors} \
    -o "pu_weights_PFJet.png" \
    --output-dir "Run2016BCDEFGH_07Aug17"

# -- AK8PFJet

_in_files=""
_labels=""
_colors=""
for kt in HLT_All:k HLT_PFJet{40:indigo,60:navy,80:blue,140:forestgreen,200:darkgoldenrod,260:orange,320:darkorange,400:red,450:pink,500:darkred,_All:gray}; do
    t=${kt%:*}
    c=${kt#*:}
    _in_files="${_in_files} Run2016BCDEFGH_07Aug17/pileup_80bins_Run2016BCDEFGH_07Aug17_Nominal_${t}.root"
    _labels="${_labels} ${t}"
    _colors="${_colors} ${c}"
done

python plot_pu_weights.py \
    -d $_in_files \
    -m "QCD_PtBinned_TuneCUETP8M1_pythia8/pileup_80bins_QCD_PtBinned_TuneCUETP8M1_pythia8_FromSkim.root" \
    -l ${_labels} \
    -c ${_colors} \
    -o "pu_weights_AK8PFJet.png" \
    --output-dir "Run2016BCDEFGH_07Aug17"
