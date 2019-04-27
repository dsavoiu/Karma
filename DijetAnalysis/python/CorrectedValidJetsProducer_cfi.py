import FWCore.ParameterSet.Config as cms


dijetCorrectedValidJetsProducer = cms.EDProducer(
    "CorrectedValidJetsProducer",
    cms.PSet(
        # -- input sources
        dijetEventSrc = cms.InputTag("dijetEvents"),
        dijetJetCollectionSrc = cms.InputTag("dijetUpdatedPatJetsNoJEC"),

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
