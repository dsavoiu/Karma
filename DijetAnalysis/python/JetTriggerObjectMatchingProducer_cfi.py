import FWCore.ParameterSet.Config as cms


dijetJetTriggerObjectMatchingProducer = cms.EDProducer(
    "JetTriggerObjectMatchingProducer",
    cms.PSet(
        # -- input sources
        dijetEventSrc = cms.InputTag("dijetEvents"),
        dijetJetCollectionSrc = cms.InputTag("dijetUpdatedPatJetsNoJEC"),
        dijetTriggerObjectCollectionSrc = cms.InputTag("dijetTriggerObjects"),

        # -- other configuration
        maxDeltaR = cms.double(0.2),
    )
)
