import FWCore.ParameterSet.Config as cms


karmaMETCorrectedSumEtValueMapProducer = cms.EDProducer(
    "METCorrectedSumEtValueMapProducer",
    cms.PSet(
        inputCollection = cms.InputTag("karmaJets"),
        associationSpec = cms.VPSet(
            # uncorrected MET
            cms.PSet(
                name = cms.string("Raw"),
                transientMapKey = cms.string("corSumEtRaw"),
            ),

            # uncorrected MET
            cms.PSet(
                name = cms.string("Type1"),
                transientMapKey = cms.string("corSumEtType1"),
            ),
        )
    )
)
