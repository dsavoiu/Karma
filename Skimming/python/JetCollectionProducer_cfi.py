import FWCore.ParameterSet.Config as cms


dijetJets = cms.EDProducer(
    "JetCollectionProducer",
    cms.PSet(
        # take miniAOD AK4 jets by default
        inputCollection = cms.InputTag("slimmedJets"),
    )
)
