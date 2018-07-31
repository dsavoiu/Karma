import FWCore.ParameterSet.Config as cms


dijetJetCollectionProducer = cms.EDProducer(
    "JetCollectionProducer",
    cms.PSet(
        inputCollection = cms.InputTag("slimmedJets"),
    )
)
