import FWCore.ParameterSet.Config as cms


karmaTriggerObjectCollectionProducer = cms.EDProducer(
    "TriggerObjectCollectionProducer",
    cms.PSet(
        inputCollection = cms.InputTag("selectedPatTrigger", processName=cms.InputTag.skipCurrentProcess()),
        karmaRunSrc = cms.InputTag("karmaEvents"),
        triggerResultsSrc = cms.InputTag("TriggerResults", "", "HLT"),
    )
)
