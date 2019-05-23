import FWCore.ParameterSet.Config as cms


dijetJetTriggerObjectMatchingProducer = cms.EDProducer(
    "JetTriggerObjectMatchingProducer",
    cms.PSet(
        # -- input sources
        primaryCollectionSrc = cms.InputTag("karmaUpdatedPatJetsNoJEC"),
        secondaryCollectionSrc = cms.InputTag("karmaTriggerObjects"),

        # -- other configuration
        maxDeltaR = cms.double(0.2),
    )
)
