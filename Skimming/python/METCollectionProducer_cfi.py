import FWCore.ParameterSet.Config as cms


karmaMETCollectionProducer = cms.EDProducer(
    "METCollectionProducer",
    cms.PSet(
        inputCollection = cms.InputTag("slimmedMETs"),
    )
)
