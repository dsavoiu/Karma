#!/bin/bash

INFILE="/ceph/dsavoiu/Dijet/results/DijetAna_JetHT_Run2016G-Legacy-07Aug2017-v1_2018-09-24/merged.root"

echo "Sourcing master ROOT stack... [/cvmfs/sft.cern.ch/lcg/views/dev3/latest/x86_64-slc6-gcc62-opt/setup.sh]..."
source /cvmfs/sft.cern.ch/lcg/views/dev3/latest/x86_64-slc6-gcc62-opt/setup.sh



_run () {
    OUTFILE="testPP_$1_$2.root"
    if [ -f $OUTFILE ]; then
        echo "ERROR: output file exists! [$OUTFILE]"
        echo "Skipping post-processing (trigger composition)..."
    else
        echo "Running post-processing ($3) [$OUTFILE]"
        python testPP_$1.py "$INFILE" -j10 -o "$OUTFILE"
    fi
}

_vbinning="v4_binning"

_run "TriggerComposition"   "$_vbinning"  "trigger composition"
_run "TriggerEfficiencies"  "$_vbinning"  "trigger efficiencies"
_run "TriggerPrescales"      "$_vbinning"  "trigger prescales"
_run "CrossSection"         "$_vbinning"  "cross section"
