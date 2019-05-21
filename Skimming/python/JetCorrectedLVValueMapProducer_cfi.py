import FWCore.ParameterSet.Config as cms


karmaJetCorrectedLVValueMapProducer = cms.EDProducer(
    "JetCorrectedLVValueMapProducer",
    cms.PSet(
        inputCollection = cms.InputTag("karmaJets"),
        associationSpec = cms.VPSet(
            # without JEC corrections
            cms.PSet(
                name = cms.string("Uncorrected"),
                transientMapKey = cms.string("Uncorrected"),
            ),

            # after L1 correction
            # note: Puppi jets do not have this correction level
            cms.PSet(
                name = cms.string("L1FastJet"),
                transientMapKey = cms.string("L1FastJet"),
            ),

            # after L1+L2L3 corrections
            cms.PSet(
                name = cms.string("L2Relative"),
                transientMapKey = cms.string("L2Relative"),
            ),

            # not used, always 1.0
            #cms.PSet(
            #    name = cms.string("L3Absolute"),
            #    transientMapKey = cms.string("L3Absolute"),
            #),

            # after L1+L2L3+L2L3Res corrections
            # note: no point including this -> same as default karma::Jet::p4()
            #cms.PSet(
            #    name = cms.string("L2L3Residual"),
            #    transientMapKey = cms.string("L2L3Residual"),
            #),
        )
    )
)

karmaJetCorrectedLVValueMapProducerForPuppi = cms.EDProducer(
    "JetCorrectedLVValueMapProducer",
    cms.PSet(
        inputCollection = cms.InputTag("karmaJets"),
        associationSpec = cms.VPSet(
            # without JEC corrections
            cms.PSet(
                name = cms.string("Uncorrected"),
                transientMapKey = cms.string("Uncorrected"),
            ),

            # after L1+L2L3 corrections
            cms.PSet(
                name = cms.string("L2Relative"),
                transientMapKey = cms.string("L2Relative"),
            ),

            # not used, always 1.0
            #cms.PSet(
            #    name = cms.string("L3Absolute"),
            #    transientMapKey = cms.string("L3Absolute"),
            #),

            # after L1+L2L3+L2L3Res corrections
            # note: no point including this -> same as default karma::Jet::p4()
            #cms.PSet(
            #    name = cms.string("L2L3Residual"),
            #    transientMapKey = cms.string("L2L3Residual"),
            #),
        )
    )
)
