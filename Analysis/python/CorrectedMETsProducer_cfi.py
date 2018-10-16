import FWCore.ParameterSet.Config as cms


dijetCorrectedMETsProducer = cms.EDProducer(
    "CorrectedMETsProducer",
    cms.PSet(
        # -- input sources
        dijetEventSrc = cms.InputTag("dijetEvents"),
        dijetMETCollectionSrc = cms.InputTag("dijetCHSMETs"),
        dijetCorrectedJetCollectionSrc = cms.InputTag("correctedJets"),

        # -- other configuration
        typeICorrectionMinJetPt = cms.double(15),
    )
)
