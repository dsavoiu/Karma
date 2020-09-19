import FWCore.ParameterSet.Config as cms


karmaJetUncertaintySourceApplier = cms.EDProducer(
    "KarmaJetUncertaintySourceApplier",
    cms.PSet(
        # -- input sources
        karmaJetCollectionSrc = cms.InputTag("karmaUpdatedPatJetsNoJEC"),

        # specify jet uncertainty sources to apply
        jetUncertaintySources = cms.vstring()
    )
)
