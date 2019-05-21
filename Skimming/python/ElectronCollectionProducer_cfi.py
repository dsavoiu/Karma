import FWCore.ParameterSet.Config as cms


karmaElectronCollectionProducer = cms.EDProducer(
    "ElectronCollectionProducer",
    cms.PSet(
        inputCollection = cms.InputTag("slimmedElectrons"),
        electronIds = cms.VPSet(
            cms.PSet(
                name = cms.string("Summer16-80X-V1"),
                workingPoints = cms.vstring(
                    # ordered from loosest to tightest
                    "cutBasedElectronID-Summer16-80X-V1-veto",
                    "cutBasedElectronID-Summer16-80X-V1-loose",
                    "cutBasedElectronID-Summer16-80X-V1-medium",
                    "cutBasedElectronID-Summer16-80X-V1-tight",
                )
            ),
            cms.PSet(
                name = cms.string("Fall17-94X-V1"),
                workingPoints = cms.vstring(
                    # ordered from loosest to tightest
                    "cutBasedElectronID-Fall17-94X-V1-veto",
                    "cutBasedElectronID-Fall17-94X-V1-loose",
                    "cutBasedElectronID-Fall17-94X-V1-medium",
                    "cutBasedElectronID-Fall17-94X-V1-tight",
                )
            ),
        )
    )
)
