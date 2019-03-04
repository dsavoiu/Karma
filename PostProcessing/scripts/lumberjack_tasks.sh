INFILE_MC="/ceph/dsavoiu/Dijet/results/DijetAna_QCD_Flat_RunIISummer16MiniAODv2_2019-01-12/merged.root"
INFILE_DATA="/ceph/dsavoiu/Dijet/results/DijetAna_JetHT_Run2016G-Legacy-07Aug2017-v1_2019-01-18/merged.root"
OUTPUT_FILE_SUFFIX="2019-01-24"

echo "Sourcing master ROOT stack... [/cvmfs/sft.cern.ch/lcg/views/dev3/latest/x86_64-slc6-gcc62-opt/setup.sh]..."
source /cvmfs/sft.cern.ch/lcg/views/dev3/latest/x86_64-slc6-gcc62-opt/setup.sh

# -- DATA

lumberjack.py -i "$INFILE_DATA" \
      --type data \
      -j10 \
      --log --progress \
      --tree "pipelineAK4PFCHSNominal/Events" \
      $@ \
      task TriggerEfficienciesAK4 EventYield_AK4PFJetTriggers \
      --output-file-suffix "$OUTPUT_FILE_SUFFIX"

lumberjack.py -i "$INFILE_DATA" \
      --type data \
      -j10 \
      --log --progress \
      --tree "pipelineAK8PFCHSNominal/Events" \
      $@ \
      task TriggerEfficienciesAK8 EventYield_AK8PFJetTriggers \
      --output-file-suffix "$OUTPUT_FILE_SUFFIX"

# -- MC

lumberjack.py -i "$INFILE_MC" \
      --type mc \
      -j10 \
      --log --progress \
      --tree "pipelineAK4PFCHSNominal/Events" \
      $@ \
      task EventYieldMC_AK4 \
      --output-file-suffix "$OUTPUT_FILE_SUFFIX"

lumberjack.py -i "$INFILE_MC" \
      --type mc \
      -j10 \
      --log --progress \
      --tree "pipelineAK8PFCHSNominal/Events" \
      $@ \
      task EventYieldMC_AK8 \
      --output-file-suffix "$OUTPUT_FILE_SUFFIX"
