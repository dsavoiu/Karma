import FWCore.ParameterSet.Config as cms


dijetVertexCollectionProducer = cms.EDProducer(
    "VertexCollectionProducer",
    cms.PSet(
        inputCollection = cms.InputTag("offlineSlimmedPrimaryVertices"),
    )
)
