import FWCore.ParameterSet.Config as cms


karmaGenJetsAK4 = cms.EDProducer(
    "GenJetCollectionProducer",
    cms.PSet(
        inputCollection = cms.InputTag("slimmedGenJets"),
    )
)
karmaGenJetsAK8 = cms.EDProducer(
    "GenJetCollectionProducer",
    cms.PSet(
        inputCollection = cms.InputTag("slimmedGenJetsAK8"),
    )
)
