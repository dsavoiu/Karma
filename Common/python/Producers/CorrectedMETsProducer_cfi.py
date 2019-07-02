import FWCore.ParameterSet.Config as cms


karmaCorrectedMETsProducer = cms.EDProducer(
    "KarmaCorrectedMETsProducer",
    cms.PSet(
        # -- input sources
        karmaEventSrc = cms.InputTag("karmaEvents"),
        karmaMETCollectionSrc = cms.InputTag("karmaMETs"),
        karmaCorrectedJetCollectionSrc = cms.InputTag("correctedJets"),

        # -- other configuration
        typeICorrectionMinJetPt = cms.double(15),
        typeICorrectionMaxTotalEMFraction = cms.double(0.9),
        typeICorrectionJECReferenceLevel = cms.string("L1"),  # alternatively: "L1RC"
    )
)
