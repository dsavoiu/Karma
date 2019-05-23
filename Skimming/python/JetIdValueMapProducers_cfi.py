import FWCore.ParameterSet.Config as cms


karmaJetIdValueMapProducer = cms.EDProducer(
    "JetIdValueMapProducer",
    cms.PSet(
        inputCollection = cms.InputTag("karmaJets"),
        associationSpec = cms.VPSet(
            cms.PSet(
                name = cms.string("jetIdWinter16TightLepVeto"),
                transientMapKey = cms.string("jetIdWinter16TightLepVeto"),
            ),
        )
    )
)

karmaJetPileupIdValueMapProducer = cms.EDProducer(
    "JetPileupIdValueMapProducer",
    cms.PSet(
        inputCollection = cms.InputTag("karmaJets"),
        associationSpec = cms.VPSet(
            cms.PSet(
                name = cms.string("pileupJetId"),
                transientMapKey = cms.string("pileupJetId"),
            ),
        )
    )
)

karmaJetPileupIdDiscriminantValueMapProducer = cms.EDProducer(
    "JetPileupIdDiscriminantValueMapProducer",
    cms.PSet(
        inputCollection = cms.InputTag("karmaJets"),
        associationSpec = cms.VPSet(
            cms.PSet(
                name = cms.string("pileupJetId"),
                transientMapKey = cms.string("pileupJetId"),
            ),
        )
    )
)
