import FWCore.ParameterSet.Config as cms


karmaGeneratorQCDInfoProducer = cms.EDProducer(
    "GeneratorQCDInfoProducer",
    cms.PSet(
        # -- input sources
        genEventInfoProductSrc = cms.InputTag("generator"),
    )
)
