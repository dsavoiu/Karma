#!/bin/bash

INFILE="/ceph/dsavoiu/Dijet/results/DijetAna_JetHT_Run2016G-Legacy-07Aug2017-v1_2018-09-24/merged.root"
OUTFILE="testPP_TriggerPrescales_v4_binning.root"

if [ -f $OUTFILE ]; then
    echo "ERROR: output file exists! [$OUTFILE]"
    exit 1
fi

echo "Sourcing master ROOT stack... [/cvmfs/sft.cern.ch/lcg/views/dev3/latest/x86_64-slc6-gcc62-opt/setup.sh]..."
source /cvmfs/sft.cern.ch/lcg/views/dev3/latest/x86_64-slc6-gcc62-opt/setup.sh

echo "Running post-processing (trigger prescales) [$OUTFILE]"
python testPP_TriggerPrescales.py "$INFILE" -j10 -o "$OUTFILE"

