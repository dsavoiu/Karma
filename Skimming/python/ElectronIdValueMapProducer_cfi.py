import FWCore.ParameterSet.Config as cms


karmaElectronIdValueMapProducer = cms.EDProducer(
    "ElectronIdValueMapProducer",
    cms.PSet(
        inputCollection = cms.InputTag("karmaElectrons"),
        associationSpec = cms.VPSet(
            cms.PSet(
                name = cms.string("electronIdSummer1680XV1"),
                transientMapKey = cms.string("Summer16-80X-V1"),
            ),
            cms.PSet(
                name = cms.string("electronIdFall1794XV1"),
                transientMapKey = cms.string("Fall17-94X-V1"),
            ),
        )
    )
)
