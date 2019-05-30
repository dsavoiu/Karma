import FWCore.ParameterSet.Config as cms


karmaCorrectedValidJetsProducer = cms.EDProducer(
    "KarmaCorrectedValidJetsProducer",
    cms.PSet(
        # -- input sources
        karmaEventSrc = cms.InputTag("karmaEvents"),
        karmaJetCollectionSrc = cms.InputTag("karmaUpdatedPatJetsNoJEC"),

        # -- other configuration
        jecVersion = cms.string("<REPLACE_ME>"),
        jecAlgoName = cms.string("AK4PFchs"),
        jecLevels = cms.vstring(
            "L1FastJet",
            "L2Relative",
            "L2L3Residual",
        ),
        jecUncertaintyShift = cms.double(0.0),

        jetIDSpec = cms.string("2016"),   # use "None" for no object-based JetID
        jetIDWorkingPoint = cms.string("TightLepVeto"),
    )
)
