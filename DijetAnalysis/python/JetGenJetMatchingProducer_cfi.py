import FWCore.ParameterSet.Config as cms


dijetJetGenJetMatchingProducer = cms.EDProducer(
    "JetGenJetMatchingProducer",
    cms.PSet(
        # -- input sources
        karmaEventSrc = cms.InputTag("karmaEvents"),
        karmaJetCollectionSrc = cms.InputTag("karmaUpdatedPatJetsNoJEC"),
        karmaGenJetCollectionSrc = cms.InputTag("karmaGenJets"),

        # -- other configuration
        maxDeltaR = cms.double(0.2),
    )
)
