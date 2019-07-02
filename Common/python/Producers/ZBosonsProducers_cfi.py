import FWCore.ParameterSet.Config as cms


karmaZBosonsFromElectronsProducer = cms.EDProducer(
    "KarmaZBosonsFromElectronsProducer",
    cms.PSet(
        # -- input sources
        karmaLeptonCollectionSrc = cms.InputTag("karmaElectrons"),

        # -- other configuration
        maxDeltaInvariantMass = cms.double(20),
    )
)

karmaZBosonsFromMuonsProducer = cms.EDProducer(
    "KarmaZBosonsFromMuonsProducer",
    cms.PSet(
        # -- input sources
        karmaLeptonCollectionSrc = cms.InputTag("karmaMuons"),

        # -- other configuration
        maxDeltaInvariantMass = cms.double(20),
    )
)
