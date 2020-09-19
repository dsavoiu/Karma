import FWCore.ParameterSet.Config as cms


karmaCorrectedValidJetsProducer = cms.EDProducer(
    "KarmaCorrectedValidJetsProducer",
    cms.PSet(
        # -- input sources
        karmaEventSrc = cms.InputTag("karmaEvents"),
        karmaJetCollectionSrc = cms.InputTag("karmaUpdatedPatJetsNoJEC"),

        # -- other configuration
        jecFromGlobalTag = cms.bool(False),
        jecVersion = cms.string("<REPLACE_ME>"),
        jecAlgoName = cms.string("AK4PFchs"),
        jecLevels = cms.vstring(
            "L1FastJet",
            "L2Relative",
            "L2L3Residual",
        ),
        jecUncertaintyShift = cms.double(0.0),

        # which jet uncertainty sources to read and store in transient map
        # (these are then made available to the `JetUncertaintySourceApplier`)
        jecUncertaintySources = cms.vstring(),

        jetIDSpec = cms.string("2016"),   # use "None" for no object-based JetID
        jetIDWorkingPoint = cms.string("TightLepVeto"),
    )
)
