import FWCore.ParameterSet.Config as cms


dijetJetGenJetMatchingProducer = cms.EDProducer(
    "JetGenJetMatchingProducer",
    cms.PSet(
        # -- input sources
        dijetEventSrc = cms.InputTag("dijetEvents"),
        dijetJetCollectionSrc = cms.InputTag("dijetUpdatedPatJetsNoJEC"),
        dijetGenJetSrc = cms.InputTag("dijetGenJets"),

        # -- other configuration
        maxDeltaR = cms.double(0.2),
    )
)
