pileupCalc.py -i ../../json/2016/Cert_271036-284044_13TeV_PromptReco_Collisions16_JSON.json \
    --inputLumiJSON nPUMean_data.json \
    --calcMode true \
    --minBiasXsec 69200 \
    --maxPileupBin 80 \
    --numPileupBins 80 \
    nPUMean_data.root
