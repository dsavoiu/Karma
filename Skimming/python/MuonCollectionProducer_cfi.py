import FWCore.ParameterSet.Config as cms


karmaMuonCollectionProducer = cms.EDProducer(
    "MuonCollectionProducer",
    cms.PSet(
        inputCollection = cms.InputTag("slimmedMuons"),
    )
)
