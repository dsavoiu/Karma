import FWCore.ParameterSet.Config as cms


karmaMETCollectionProducer = cms.EDProducer(
    "METCollectionProducer",
    cms.PSet(
        inputCollection = cms.InputTag("slimmedMETs"),
        mainCorrectionLevel = cms.string("Type1"),  # correction level for main p4
    )
)
