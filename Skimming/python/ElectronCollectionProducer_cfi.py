import FWCore.ParameterSet.Config as cms


karmaElectronCollectionProducer = cms.EDProducer(
    "ElectronCollectionProducer",
    cms.PSet(
        inputCollection = cms.InputTag("slimmedElectrons"),
    )
)
