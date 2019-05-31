import FWCore.ParameterSet.Config as cms


karmaZBosonFromElectronsProducer = cms.EDProducer(
    "KarmaZBosonFromElectronsProducer",
    cms.PSet(
        # -- input sources
        karmaLeptonCollectionSrc = cms.InputTag("karmaElectrons"),

        # -- other configuration
        maxDeltaInvariantMass = cms.double(20),
    )
)

karmaZBosonFromMuonsProducer = cms.EDProducer(
    "KarmaZBosonFromMuonsProducer",
    cms.PSet(
        # -- input sources
        karmaLeptonCollectionSrc = cms.InputTag("karmaMuons"),

        # -- other configuration
        maxDeltaInvariantMass = cms.double(20),
    )
)
