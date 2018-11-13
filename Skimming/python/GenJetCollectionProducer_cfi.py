import FWCore.ParameterSet.Config as cms


dijetGenJetsAK4 = cms.EDProducer(
    "GenJetCollectionProducer",
    cms.PSet(
        inputCollection = cms.InputTag("slimmedGenJets"),
    )
)
dijetGenJetsAK8 = cms.EDProducer(
    "GenJetCollectionProducer",
    cms.PSet(
        inputCollection = cms.InputTag("slimmedGenJetsAK8"),
    )
)
