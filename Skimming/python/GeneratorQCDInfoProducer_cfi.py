import FWCore.ParameterSet.Config as cms


dijetGeneratorQCDInfoProducer = cms.EDProducer(
    "GeneratorQCDInfoProducer",
    cms.PSet(
        # -- input sources
        genEventInfoProductSrc = cms.InputTag("generator"),
    )
)
