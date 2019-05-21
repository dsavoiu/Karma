import FWCore.ParameterSet.Config as cms


karmaMETCorrectedLVValueMapProducer = cms.EDProducer(
    "METCorrectedLVValueMapProducer",
    cms.PSet(
        inputCollection = cms.InputTag("karmaJets"),
        associationSpec = cms.VPSet(
            # uncorrected MET
            cms.PSet(
                name = cms.string("Raw"),
                transientMapKey = cms.string("corP4Raw"),
            ),

            # uncorrected MET
            cms.PSet(
                name = cms.string("Type1"),
                transientMapKey = cms.string("corP4Type1"),
            ),
        )
    )
)
