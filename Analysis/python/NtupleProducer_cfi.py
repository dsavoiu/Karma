import FWCore.ParameterSet.Config as cms


dijetNtupleProducer = cms.EDProducer(
    "NtupleProducer",
    cms.PSet(
        # -- input sources
        dijetEventSrc = cms.InputTag("dijetEvents"),
        dijetVertexCollectionSrc = cms.InputTag("dijetVertices"),
        dijetGeneratorQCDInfoSrc = cms.InputTag("dijetGeneratorQCDInfos"),
        dijetRunSrc = cms.InputTag("dijetEvents"),
        dijetJetCollectionSrc = cms.InputTag("dijetCorrectedJets"),
        dijetMETCollectionSrc = cms.InputTag("dijetCorrectedMETs"),
        dijetGenParticleCollectionSrc = cms.InputTag("dijetGenParticles"),
        dijetJetTriggerObjectMapSrc = cms.InputTag("dijetJetTriggerObjectMaps"),

        # -- other configuration

        #triggerEfficienciesFile = cms.string("trigger_efficiencies.root"),
        weightForStitching = cms.double(1.0),

        hltPaths = cms.VPSet(
            cms.PSet(name=cms.string("HLT_IsoMu24"), hltThreshold=cms.double(0), l1Threshold=cms.double(0)),
            #
            cms.PSet(name=cms.string("HLT_PFJet40"), hltThreshold=cms.double(40), l1Threshold=cms.double(0)),
            cms.PSet(name=cms.string("HLT_PFJet60"), hltThreshold=cms.double(60), l1Threshold=cms.double(35)),
            cms.PSet(name=cms.string("HLT_PFJet80"), hltThreshold=cms.double(80), l1Threshold=cms.double(60)),
            cms.PSet(name=cms.string("HLT_PFJet140"), hltThreshold=cms.double(140), l1Threshold=cms.double(90)),
            cms.PSet(name=cms.string("HLT_PFJet200"), hltThreshold=cms.double(200), l1Threshold=cms.double(120)),
            cms.PSet(name=cms.string("HLT_PFJet260"), hltThreshold=cms.double(260), l1Threshold=cms.double(170)),
            cms.PSet(name=cms.string("HLT_PFJet320"), hltThreshold=cms.double(320), l1Threshold=cms.double(170)),
            cms.PSet(name=cms.string("HLT_PFJet400"), hltThreshold=cms.double(400), l1Threshold=cms.double(170)),
            cms.PSet(name=cms.string("HLT_PFJet450"), hltThreshold=cms.double(450), l1Threshold=cms.double(170)),
            cms.PSet(name=cms.string("HLT_PFJet500"), hltThreshold=cms.double(500), l1Threshold=cms.double(170)),
            #
            cms.PSet(name=cms.string("HLT_AK8PFJet40"), hltThreshold=cms.double(40), l1Threshold=cms.double(0)),
            cms.PSet(name=cms.string("HLT_AK8PFJet60"), hltThreshold=cms.double(60), l1Threshold=cms.double(35)),
            cms.PSet(name=cms.string("HLT_AK8PFJet80"), hltThreshold=cms.double(80), l1Threshold=cms.double(60)),
            cms.PSet(name=cms.string("HLT_AK8PFJet140"), hltThreshold=cms.double(140), l1Threshold=cms.double(90)),
            cms.PSet(name=cms.string("HLT_AK8PFJet200"), hltThreshold=cms.double(200), l1Threshold=cms.double(120)),
            cms.PSet(name=cms.string("HLT_AK8PFJet260"), hltThreshold=cms.double(260), l1Threshold=cms.double(170)),
            cms.PSet(name=cms.string("HLT_AK8PFJet320"), hltThreshold=cms.double(320), l1Threshold=cms.double(170)),
            cms.PSet(name=cms.string("HLT_AK8PFJet400"), hltThreshold=cms.double(400), l1Threshold=cms.double(170)),
            cms.PSet(name=cms.string("HLT_AK8PFJet450"), hltThreshold=cms.double(450), l1Threshold=cms.double(170)),
            cms.PSet(name=cms.string("HLT_AK8PFJet500"), hltThreshold=cms.double(500), l1Threshold=cms.double(170)),
            #
            cms.PSet(name=cms.string("HLT_DiPFJetAve40"), hltThreshold=cms.double(40), l1Threshold=cms.double(0)),
            cms.PSet(name=cms.string("HLT_DiPFJetAve60"), hltThreshold=cms.double(60), l1Threshold=cms.double(35)),
            cms.PSet(name=cms.string("HLT_DiPFJetAve80"), hltThreshold=cms.double(80), l1Threshold=cms.double(60)),
            cms.PSet(name=cms.string("HLT_DiPFJetAve140"), hltThreshold=cms.double(140), l1Threshold=cms.double(90)),
            cms.PSet(name=cms.string("HLT_DiPFJetAve200"), hltThreshold=cms.double(200), l1Threshold=cms.double(120)),
            cms.PSet(name=cms.string("HLT_DiPFJetAve260"), hltThreshold=cms.double(260), l1Threshold=cms.double(170)),
            cms.PSet(name=cms.string("HLT_DiPFJetAve320"), hltThreshold=cms.double(320), l1Threshold=cms.double(170)),
            cms.PSet(name=cms.string("HLT_DiPFJetAve400"), hltThreshold=cms.double(400), l1Threshold=cms.double(170)),
            cms.PSet(name=cms.string("HLT_DiPFJetAve500"), hltThreshold=cms.double(500), l1Threshold=cms.double(170)),
        ),

        jetIDSpec = cms.string("2016"),
        jetIDWorkingPoint = cms.string("TightLepVeto"),
    )
)
