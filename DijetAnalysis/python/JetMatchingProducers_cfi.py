import FWCore.ParameterSet.Config as cms


dijetJetTriggerObjectMatchingProducer = cms.EDProducer(
    "JetTriggerObjectMatchingProducer",
    cms.PSet(
        # -- input sources
        primaryCollectionSrc = cms.InputTag("karmaUpdatedPatJetsNoJEC"),
        secondaryCollectionSrc = cms.InputTag("karmaTriggerObjects"),

        # -- other configuration
        maxDeltaR = cms.double(0.2),
    )
)

dijetJetMuonMatchingProducer = cms.EDProducer(
    "JetMuonMatchingProducer",
    cms.PSet(
        # -- input sources
        primaryCollectionSrc = cms.InputTag("karmaUpdatedPatJetsNoJEC"),
        secondaryCollectionSrc = cms.InputTag("karmaMuons"),

        # -- other configuration
        maxDeltaR = cms.double(0.4),
    )
)

dijetJetElectronMatchingProducer = cms.EDProducer(
    "JetElectronMatchingProducer",
    cms.PSet(
        # -- input sources
        primaryCollectionSrc = cms.InputTag("karmaUpdatedPatJetsNoJEC"),
        secondaryCollectionSrc = cms.InputTag("karmaElectrons"),

        # -- other configuration
        maxDeltaR = cms.double(0.4),
    )
)

dijetJetGenJetMatchingProducer = cms.EDProducer(
    "JetLVMatchingProducer",
    cms.PSet(
        # -- input sources
        primaryCollectionSrc = cms.InputTag("karmaUpdatedPatJetsNoJEC"),
        secondaryCollectionSrc = cms.InputTag("karmaGenJets"),

        # -- other configuration
        maxDeltaR = cms.double(0.2),
    )
)
