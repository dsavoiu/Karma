import FWCore.ParameterSet.Config as cms


karmaSmearedJetsProducer = cms.EDProducer(
    "KarmaSmearedJetsProducer",
    cms.PSet(
        # -- input sources
        karmaEventSrc = cms.InputTag("karmaEvents"),
        karmaJetCollectionSrc = cms.InputTag("karmaUpdatedPatJetsNoJEC"),
        karmaJetGenJetMapSrc = cms.InputTag("karmaJetGenJetMapSrc"),

        # JER
        jerVersion = cms.string("<REPLACE ME>"),
        jetAlgoName = cms.string("<REPLACE_ME>"),  # e.g. AK4PFchs
        jerVariation = cms.int32(0),  # -1 for 'DOWN', 0 for 'NOMINAL', 1 for 'UP
        jerMethod = cms.string('stochastic'),
    )
)
