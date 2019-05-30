import FWCore.ParameterSet.Config as cms


karmaJetTriggerObjectMatchingProducer = cms.EDProducer(
    "KarmaJetTriggerObjectMatchingProducer",
    cms.PSet(
        # -- input sources
        primaryCollectionSrc = cms.InputTag("karmaUpdatedPatJetsNoJEC"),
        secondaryCollectionSrc = cms.InputTag("karmaTriggerObjects"),

        # -- other configuration
        maxDeltaR = cms.double(0.2),
    )
)

karmaJetMuonMatchingProducer = cms.EDProducer(
    "KarmaJetMuonMatchingProducer",
    cms.PSet(
        # -- input sources
        primaryCollectionSrc = cms.InputTag("karmaUpdatedPatJetsNoJEC"),
        secondaryCollectionSrc = cms.InputTag("karmaMuons"),

        # -- other configuration
        maxDeltaR = cms.double(0.4),
    )
)

karmaJetElectronMatchingProducer = cms.EDProducer(
    "KarmaJetElectronMatchingProducer",
    cms.PSet(
        # -- input sources
        primaryCollectionSrc = cms.InputTag("karmaUpdatedPatJetsNoJEC"),
        secondaryCollectionSrc = cms.InputTag("karmaElectrons"),

        # -- other configuration
        maxDeltaR = cms.double(0.4),
    )
)

karmaJetGenJetMatchingProducer = cms.EDProducer(
    "KarmaJetLVMatchingProducer",
    cms.PSet(
        # -- input sources
        primaryCollectionSrc = cms.InputTag("karmaUpdatedPatJetsNoJEC"),
        secondaryCollectionSrc = cms.InputTag("karmaGenJets"),

        # -- other configuration
        maxDeltaR = cms.double(0.2),
    )
)
