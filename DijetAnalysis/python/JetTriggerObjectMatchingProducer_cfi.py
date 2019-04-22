import FWCore.ParameterSet.Config as cms


dijetJetTriggerObjectMatchingProducer = cms.EDProducer(
    "JetTriggerObjectMatchingProducer",
    cms.PSet(
        # -- input sources
        karmaEventSrc = cms.InputTag("karmaEvents"),
        karmaJetCollectionSrc = cms.InputTag("karmaUpdatedPatJetsNoJEC"),
        karmaTriggerObjectCollectionSrc = cms.InputTag("karmaTriggerObjects"),

        # -- other configuration
        maxDeltaR = cms.double(0.2),
    )
)
