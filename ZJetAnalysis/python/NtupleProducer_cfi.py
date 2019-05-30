import FWCore.ParameterSet.Config as cms


zjetNtupleProducer = cms.EDProducer(
    "ZJetNtupleProducer",
    cms.PSet(
        # -- input sources
        karmaEventSrc = cms.InputTag("karmaEvents"),
        karmaVertexCollectionSrc = cms.InputTag("karmaVertices"),
        karmaGeneratorQCDInfoSrc = cms.InputTag("karmaGeneratorQCDInfos"),
        karmaRunSrc = cms.InputTag("karmaEvents"),
        karmaJetCollectionSrc = cms.InputTag("karmaCorrectedJets"),
        karmaMETCollectionSrc = cms.InputTag("karmaCorrectedMETs"),
        karmaGenParticleCollectionSrc = cms.InputTag("karmaGenParticles"),
        karmaGenJetCollectionSrc = cms.InputTag("karmaGenJets"),
        karmaJetTriggerObjectMapSrc = cms.InputTag("karmaJetTriggerObjectMaps"),

        # -- other configuration

        #triggerEfficienciesFile = cms.string("trigger_efficiencies.root"),
        npuMeanFile = cms.string("npumean.txt"),
        minBiasCrossSection = cms.double(69.2),  # in mb

        pileupWeightFile = cms.string("nPUMean_ratio.root"),
        pileupWeightHistogramName = cms.string("pileup"),

        weightForStitching = cms.double(1.0),

        channelSpec = cms.string("mm"),

        #: vector of PSets, one for each trigger path to consider
        # each PSet contains the following keys:
        #   - name (string):          the (unversioned) name of the trigger path, as it appears in the skim
        #   - hltThreshold (double):  value to use as HLT-level pT/pTave threshold when emulating this trigger
        #   - l1Threshold (double):   value to use as L1-level pT/pTave threshold when emulating this trigger
        #       NOTE: an event is considered to contain a trigger match for Reco-Level objects (i.e. jets) if
        #             *both* HLT and L1-level matches exist. An exception to this is when the HLT or L1 threshold
        #             is set to zero. In that case, an event is considered to contain a trigger match even if there
        #             are no matched objects on HLT or L1 levels, respectively.
        hltPaths = cms.VPSet(
        ),

        jetIDSpec = cms.string("2016"),
        jetIDWorkingPoint = cms.string("TightLepVeto"),
    )
)
