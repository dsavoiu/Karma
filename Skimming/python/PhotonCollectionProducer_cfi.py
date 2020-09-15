import FWCore.ParameterSet.Config as cms


karmaPhotonCollectionProducer = cms.EDProducer(
    "PhotonCollectionProducer",
    cms.PSet(
        # take miniAOD AK4 jets by default
        inputCollection = cms.InputTag("slimmedPhotons"),
    )
)
