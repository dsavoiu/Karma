#!/bin/bash

INFILE="/ceph/dsavoiu/Dijet/results/DijetAna_JetHT_Run2016G-Legacy-07Aug2017-v1_2018-09-24/merged.root"
OUTPUT_FILE_SUFFIX="2018-09-27"

echo "Sourcing master ROOT stack... [/cvmfs/sft.cern.ch/lcg/views/dev3/latest/x86_64-slc6-gcc62-opt/setup.sh]..."
source /cvmfs/sft.cern.ch/lcg/views/dev3/latest/x86_64-slc6-gcc62-opt/setup.sh

TASKNAME="TriggerShapes"
echo "Running Task '${TASKNAME}'"
pp.py "$INFILE" "triggers" \
    --x-quantities jet1HLTAssignedPathIndex jet1HLTAssignedPathEfficiency jet1HLTAssignedPathPrescale jet2HLTAssignedPathIndex jet2HLTAssignedPathEfficiency jet2HLTAssignedPathPrescale \
    -j10 \
    -o "${TASKNAME}_${OUTPUT_FILE_SUFFIX}.root"

TASKNAME="CrossSection"
echo "Running Task '${TASKNAME}'"
pp.py "$INFILE" "ybys" \
    --x-quantities jet1pt jet12ptave jet12mass metOverSumET \
    --weights totalWeight triggerEfficiencyWeight triggerPrescaleWeight \
    -j10 \
    -o "${TASKNAME}_${OUTPUT_FILE_SUFFIX}.root"

TASKNAME="TriggerComposition"
echo "Running Task '${TASKNAME}'"
pp.py "$INFILE" "triggers" \
    --x-quantities jet1pt jet12ptave jet12mass metOverSumET \
    --weights totalWeight triggerEfficiencyWeight triggerPrescaleWeight \
    -j10 \
    -o "${TASKNAME}_${OUTPUT_FILE_SUFFIX}.root"

TASKNAME="TriggerEfficienciesPrescales"
echo "Running Task '${TASKNAME}'"
pp.py "$INFILE" "triggers" \
    --x-quantities jet1pt jet12ptave jet12mass metOverSumET \
    --y-quantities jet1HLTAssignedPathEfficiency jet1HLTAssignedPathPrescale \
    -j10 \
    -o "${TASKNAME}_${OUTPUT_FILE_SUFFIX}.root"
