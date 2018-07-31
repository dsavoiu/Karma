import FWCore.ParameterSet.Config as cms


dijetTriggerObjectCollectionProducer = cms.EDProducer(
    "TriggerObjectCollectionProducer",
    cms.PSet(
        inputCollection = cms.InputTag("selectedPatTrigger"),

        # negative is L1, positive is HLT
        allowedTriggerObjectTypes = cms.vint32(-99, -86, -85, -84, +85, +86),
    )
)
