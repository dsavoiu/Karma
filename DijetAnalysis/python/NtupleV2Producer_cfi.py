import FWCore.ParameterSet.Config as cms


dijetNtupleV2Producer = cms.EDProducer(
    "DijetNtupleV2Producer",
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
        karmaJetGenJetMapSrc = cms.InputTag("karmaJetTriggerObjectMaps"),
        karmaPrefiringWeightSrc = cms.InputTag("karmaPrefiringWeightProducer:nonPrefiringProb"),
        karmaPrefiringWeightUpSrc = cms.InputTag("karmaPrefiringWeightProducer:nonPrefiringProbUp"),
        karmaPrefiringWeightDownSrc = cms.InputTag("karmaPrefiringWeightProducer:nonPrefiringProbDown"),

        # -- other configuration

        #triggerEfficienciesFile = cms.string("trigger_efficiencies.root"),
        npuMeanFile = cms.string("npumean.txt"),
        # values from [https://twiki.cern.ch/twiki/bin/viewauth/CMS/PileupJSONFileforData]
        minBiasCrossSection = cms.double(69.2),  # in mb
        minBiasCrossSectionRelativeUncertainty = cms.double(0.046),  # 4.6%

        pileupHistogramName = cms.string("pileup"),
        pileupWeightNumeratorProfileFile = cms.string("nPUMean_data.root"),
        pileupWeightDenominatorProfileFile = cms.string("nPUMean_mc.root"),
        # optional: alternative PU profiles for comparison
        pileupWeightNumeratorProfileFileAlt = cms.string("nPUMean_data_alt.root"),
        pileupWeightDenominatorProfileFileAlt = cms.string("nPUMean_mc.root"),

        stitchingWeight = cms.double(1.0),

        #: vector of PSets, one for each trigger path to consider
        # each PSet contains the following keys:
        #   - name (string):          the (unversioned) name of the trigger path, as it appears in the skim
        #   - hltThreshold (double):  value to use as HLT-level pT/pTave threshold when emulating this trigger
        #   - l1Threshold (double):   value to use as L1-level pT/pTave threshold when emulating this trigger
        #       NOTE: an event is considered to contain a trigger match for Reco-Level objects (i.e. jets) if
        #             *both* HLT and L1-level matches exist. An exception to this is when the HLT or L1 threshold
        #             is set to zero. In that case, an event is considered to contain a trigger match even if there
        #             are no matched objects on HLT or L1 levels, respectively.
        #   - puProfileFile (string): path to a file that contains a single TH1D `pileup` with the pileup profile
        #                             of this trigger. This will be used for filling dedicated per-trigger weights
        #                             for doing pileup reweighting in MC.
        #   - puProfileFileAlt (string): alternative PU weight file (optional)
        hltPaths = cms.VPSet(
            cms.PSet(name=cms.string("HLT_IsoMu24"),        hltThreshold=cms.double(0),   l1Threshold=cms.double(0),   puProfileFile=cms.string("pileup_HLT_IsoMu24.root")),
            #
            cms.PSet(name=cms.string("HLT_PFJet40"),        hltThreshold=cms.double(40),  l1Threshold=cms.double(0),   puProfileFile=cms.string("pileup_HLT_PFJet40.root")),
            cms.PSet(name=cms.string("HLT_PFJet60"),        hltThreshold=cms.double(60),  l1Threshold=cms.double(35),  puProfileFile=cms.string("pileup_HLT_PFJet60.root")),
            cms.PSet(name=cms.string("HLT_PFJet80"),        hltThreshold=cms.double(80),  l1Threshold=cms.double(60),  puProfileFile=cms.string("pileup_HLT_PFJet80.root")),
            cms.PSet(name=cms.string("HLT_PFJet140"),       hltThreshold=cms.double(140), l1Threshold=cms.double(90),  puProfileFile=cms.string("pileup_HLT_PFJet140.root")),
            cms.PSet(name=cms.string("HLT_PFJet200"),       hltThreshold=cms.double(200), l1Threshold=cms.double(120), puProfileFile=cms.string("pileup_HLT_PFJet200.root")),
            cms.PSet(name=cms.string("HLT_PFJet260"),       hltThreshold=cms.double(260), l1Threshold=cms.double(170), puProfileFile=cms.string("pileup_HLT_PFJet260.root")),
            cms.PSet(name=cms.string("HLT_PFJet320"),       hltThreshold=cms.double(320), l1Threshold=cms.double(170), puProfileFile=cms.string("pileup_HLT_PFJet320.root")),
            cms.PSet(name=cms.string("HLT_PFJet400"),       hltThreshold=cms.double(400), l1Threshold=cms.double(170), puProfileFile=cms.string("pileup_HLT_PFJet400.root")),
            cms.PSet(name=cms.string("HLT_PFJet450"),       hltThreshold=cms.double(450), l1Threshold=cms.double(170), puProfileFile=cms.string("pileup_HLT_PFJet450.root")),
            cms.PSet(name=cms.string("HLT_PFJet500"),       hltThreshold=cms.double(500), l1Threshold=cms.double(170), puProfileFile=cms.string("pileup_HLT_PFJet500.root")),
            #
            cms.PSet(name=cms.string("HLT_AK8PFJet40"),     hltThreshold=cms.double(40),  l1Threshold=cms.double(0),   puProfileFile=cms.string("pileup_HLT_AK8PFJet40.root")),
            cms.PSet(name=cms.string("HLT_AK8PFJet60"),     hltThreshold=cms.double(60),  l1Threshold=cms.double(35),  puProfileFile=cms.string("pileup_HLT_AK8PFJet60.root")),
            cms.PSet(name=cms.string("HLT_AK8PFJet80"),     hltThreshold=cms.double(80),  l1Threshold=cms.double(60),  puProfileFile=cms.string("pileup_HLT_AK8PFJet80.root")),
            cms.PSet(name=cms.string("HLT_AK8PFJet140"),    hltThreshold=cms.double(140), l1Threshold=cms.double(90),  puProfileFile=cms.string("pileup_HLT_AK8PFJet140.root")),
            cms.PSet(name=cms.string("HLT_AK8PFJet200"),    hltThreshold=cms.double(200), l1Threshold=cms.double(120), puProfileFile=cms.string("pileup_HLT_AK8PFJet200.root")),
            cms.PSet(name=cms.string("HLT_AK8PFJet260"),    hltThreshold=cms.double(260), l1Threshold=cms.double(170), puProfileFile=cms.string("pileup_HLT_AK8PFJet260.root")),
            cms.PSet(name=cms.string("HLT_AK8PFJet320"),    hltThreshold=cms.double(320), l1Threshold=cms.double(170), puProfileFile=cms.string("pileup_HLT_AK8PFJet320.root")),
            cms.PSet(name=cms.string("HLT_AK8PFJet400"),    hltThreshold=cms.double(400), l1Threshold=cms.double(170), puProfileFile=cms.string("pileup_HLT_AK8PFJet400.root")),
            cms.PSet(name=cms.string("HLT_AK8PFJet450"),    hltThreshold=cms.double(450), l1Threshold=cms.double(170), puProfileFile=cms.string("pileup_HLT_AK8PFJet450.root")),
            cms.PSet(name=cms.string("HLT_AK8PFJet500"),    hltThreshold=cms.double(500), l1Threshold=cms.double(170), puProfileFile=cms.string("pileup_HLT_AK8PFJet500.root")),
            #
            cms.PSet(name=cms.string("HLT_DiPFJetAve40"),   hltThreshold=cms.double(40),  l1Threshold=cms.double(0),   puProfileFile=cms.string("pileup_HLT_DiPFJetAve40.root")),
            cms.PSet(name=cms.string("HLT_DiPFJetAve60"),   hltThreshold=cms.double(60),  l1Threshold=cms.double(0),   puProfileFile=cms.string("pileup_HLT_DiPFJetAve60.root")),
            cms.PSet(name=cms.string("HLT_DiPFJetAve80"),   hltThreshold=cms.double(80),  l1Threshold=cms.double(60),  puProfileFile=cms.string("pileup_HLT_DiPFJetAve80.root")),
            cms.PSet(name=cms.string("HLT_DiPFJetAve140"),  hltThreshold=cms.double(140), l1Threshold=cms.double(90),  puProfileFile=cms.string("pileup_HLT_DiPFJetAve140.root")),
            cms.PSet(name=cms.string("HLT_DiPFJetAve200"),  hltThreshold=cms.double(200), l1Threshold=cms.double(120), puProfileFile=cms.string("pileup_HLT_DiPFJetAve200.root")),
            cms.PSet(name=cms.string("HLT_DiPFJetAve260"),  hltThreshold=cms.double(260), l1Threshold=cms.double(170), puProfileFile=cms.string("pileup_HLT_DiPFJetAve260.root")),
            cms.PSet(name=cms.string("HLT_DiPFJetAve320"),  hltThreshold=cms.double(320), l1Threshold=cms.double(170), puProfileFile=cms.string("pileup_HLT_DiPFJetAve320.root")),
            cms.PSet(name=cms.string("HLT_DiPFJetAve400"),  hltThreshold=cms.double(400), l1Threshold=cms.double(170), puProfileFile=cms.string("pileup_HLT_DiPFJetAve400.root")),
            cms.PSet(name=cms.string("HLT_DiPFJetAve500"),  hltThreshold=cms.double(500), l1Threshold=cms.double(170), puProfileFile=cms.string("pileup_HLT_DiPFJetAve500.root")),
        ),

        # if true, write out prescales to NtupleV2 as vector<int>
        doPrescales = cms.bool(False),

        jetIDSpec = cms.string("2016"),
        jetIDWorkingPoint = cms.string("TightLepVeto"),

        metFilterNames = cms.vstring(
            'Flag_goodVertices',
            'Flag_globalSuperTightHalo2016Filter',
            'Flag_HBHENoiseFilter',
            'Flag_HBHENoiseIsoFilter',
            'Flag_EcalDeadCellTriggerPrimitiveFilter',
            'Flag_BadPFMuonFilter',
            'Flag_eeBadScFilter',
            #'Flag_CSCTightHaloFilter',
            #'Flag_CSCTightHaloTrkMuUnvetoFilter',
            #'Flag_CSCTightHalo2015Filter',
            #'Flag_globalTightHalo2016Filter',
            #'Flag_HcalStripHaloFilter',
            #'Flag_hcalLaserEventFilter',
            #'Flag_EcalDeadCellBoundaryEnergyFilter',
            #'Flag_ecalLaserCorrFilter',
            #'Flag_trkPOGFilters',
            #'Flag_chargedHadronTrackResolutionFilter',
            #'Flag_muonBadTrackFilter',
            #'Flag_BadChargedCandidateFilter',
            #'Flag_BadChargedCandidateSummer16Filter',
            #'Flag_BadPFMuonSummer16Filter',
            #'Flag_trkPOG_manystripclus53X',
            #'Flag_trkPOG_toomanystripclus53X',
            #'Flag_trkPOG_logErrorTooManyClusters',
            #'Flag_METFilters',
        ),
    )
)
