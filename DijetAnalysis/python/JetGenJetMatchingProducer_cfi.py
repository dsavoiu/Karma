import FWCore.ParameterSet.Config as cms


dijetJetGenJetMatchingProducer = cms.EDProducer(
    "JetGenJetMatchingProducer",
    cms.PSet(
        # -- input sources
        primaryCollectionSrc = cms.InputTag("karmaUpdatedPatJetsNoJEC"),
        secondaryCollectionSrc = cms.InputTag("karmaGenJets"),

        # -- other configuration
        maxDeltaR = cms.double(0.2),
    )
)
