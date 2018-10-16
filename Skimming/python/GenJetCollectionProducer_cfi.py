import FWCore.ParameterSet.Config as cms


dijetGenJetCollectionProducer = cms.EDProducer(
    "GenJetCollectionProducer",
    cms.PSet(
        inputCollection = cms.InputTag("slimmedGenJets"),
    )
)
