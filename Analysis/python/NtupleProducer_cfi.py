import FWCore.ParameterSet.Config as cms


dijetNtupleProducer = cms.EDProducer(
    "NtupleProducer",
    cms.PSet(
        # -- input sources
        dijetEventSrc = cms.InputTag("dijetEvents"),
        dijetRunSrc = cms.InputTag("dijetEvents"),
        dijetJetCollectionSrc = cms.InputTag("dijetCorrectedJets"),
        dijetMETCollectionSrc = cms.InputTag("dijetCorrectedMETs"),
        dijetJetTriggerObjectMapSrc = cms.InputTag("dijetJetTriggerObjectMaps"),

        # -- other configuration

        triggerEfficienciesFile = cms.string("trigger_efficiencies.root"),

        jetIDSpec = cms.string("2016"),
        jetIDWorkingPoint = cms.string("TightLepVeto"),
    )
)
