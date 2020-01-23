import os
import FWCore.ParameterSet.Config as cms


karmaPrefiringWeightProducer = cms.EDProducer(
    "KarmaPrefiringWeightProducer",
    cms.PSet(
        # -- input sources
        karmaJetCollectionSrc = cms.InputTag("karmaUpdatedPatJetsNoJEC"),

        # -- other configuration
        prefiringWeightFilePath = cms.string(os.getenv('CMSSW_BASE') + "/src/Karma/DijetAnalysis/data/prefiring/L1prefiring_jetpt_2016BtoH.root"),
        prefiringWeightHistName = cms.string("L1prefiring_jetptvseta_2016BtoH"),
        prefiringRateSysUnc = cms.double(0.2),
    )
)
