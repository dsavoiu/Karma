import FWCore.ParameterSet.Config as cms


dijetCorrectedMETsProducer = cms.EDProducer(
    "CorrectedMETsProducer",
    cms.PSet(
        # -- input sources
        karmaEventSrc = cms.InputTag("karmaEvents"),
        karmaMETCollectionSrc = cms.InputTag("karmaCHSMETs"),
        karmaCorrectedJetCollectionSrc = cms.InputTag("correctedJets"),

        # -- other configuration
        typeICorrectionMinJetPt = cms.double(15),
    )
)
