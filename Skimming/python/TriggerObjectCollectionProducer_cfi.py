import FWCore.ParameterSet.Config as cms


dijetTriggerObjectCollectionProducer = cms.EDProducer(
    "TriggerObjectCollectionProducer",
    cms.PSet(
        inputCollection = cms.InputTag("selectedPatTrigger", processName=cms.InputTag.skipCurrentProcess()),
        dijetRunSrc = cms.InputTag("dijetEvents"),
        triggerResultsSrc = cms.InputTag("TriggerResults", "", "HLT"),
    )
)
