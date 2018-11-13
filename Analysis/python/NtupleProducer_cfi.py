import FWCore.ParameterSet.Config as cms


dijetNtupleProducer = cms.EDProducer(
    "NtupleProducer",
    cms.PSet(
        # -- input sources
        dijetEventSrc = cms.InputTag("dijetEvents"),
        dijetGeneratorQCDInfoSrc = cms.InputTag("dijetGeneratorQCDInfos"),
        dijetRunSrc = cms.InputTag("dijetEvents"),
        dijetJetCollectionSrc = cms.InputTag("dijetCorrectedJets"),
        dijetMETCollectionSrc = cms.InputTag("dijetCorrectedMETs"),
        dijetGenParticleCollectionSrc = cms.InputTag("dijetGenParticles"),
        dijetJetTriggerObjectMapSrc = cms.InputTag("dijetJetTriggerObjectMaps"),

        # -- other configuration

        triggerEfficienciesFile = cms.string("trigger_efficiencies.root"),
        weightForStitching = cms.double(1.0),

        hltPaths = cms.vstring(
            "HLT_PFJet40",
            "HLT_PFJet60",
            "HLT_PFJet80",
            "HLT_PFJet140",
            "HLT_PFJet200",
            "HLT_PFJet260",
            "HLT_PFJet320",
            "HLT_PFJet400",
            "HLT_PFJet450",
            "HLT_PFJet500",
            #
            "HLT_AK8PFJet40",
            "HLT_AK8PFJet60",
            "HLT_AK8PFJet80",
            "HLT_AK8PFJet140",
            "HLT_AK8PFJet200",
            "HLT_AK8PFJet260",
            "HLT_AK8PFJet320",
            "HLT_AK8PFJet400",
            "HLT_AK8PFJet450",
            "HLT_AK8PFJet500",
            #
            "HLT_DiPFJetAve40",
            "HLT_DiPFJetAve60",
            "HLT_DiPFJetAve80",
            "HLT_DiPFJetAve140",
            "HLT_DiPFJetAve200",
            "HLT_DiPFJetAve260",
            "HLT_DiPFJetAve320",
            "HLT_DiPFJetAve400",
            "HLT_DiPFJetAve500",
        ),

        jetIDSpec = cms.string("2016"),
        jetIDWorkingPoint = cms.string("TightLepVeto"),
    )
)
