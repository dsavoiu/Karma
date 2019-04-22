import FWCore.ParameterSet.Config as cms


karmaVertexCollectionProducer = cms.EDProducer(
    "VertexCollectionProducer",
    cms.PSet(
        inputCollection = cms.InputTag("offlineSlimmedPrimaryVertices"),
    )
)
