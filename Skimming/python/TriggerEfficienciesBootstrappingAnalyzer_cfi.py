import FWCore.ParameterSet.Config as cms

import numpy as np


dijetTriggerEfficienciesBootstrappingAnalyzer = cms.EDAnalyzer(
    "TriggerEfficienciesBootstrappingAnalyzer",
    cms.PSet(

        outputFile = cms.string("triggerEfficiencies.root"),

        jetCollectionSrc = cms.InputTag("slimmedJets"),

        # the name of the process which created the trigger decisions/objects
        hltProcessName = cms.string("HLT"),

        # names of the paths for which to measure the trigger efficiencies
        hltProbePaths = cms.PSet(
            HLT_PFJet40  = cms.PSet(hltTagPath=cms.string("HLT_IsoMu24"),  hltThreshold=cms.double(40),  l1Threshold=cms.double(0)),
            HLT_PFJet60  = cms.PSet(hltTagPath=cms.string("HLT_PFJet40"),  hltThreshold=cms.double(60),  l1Threshold=cms.double(35)),
            HLT_PFJet80  = cms.PSet(hltTagPath=cms.string("HLT_PFJet60"),  hltThreshold=cms.double(80),  l1Threshold=cms.double(60)),
            HLT_PFJet140 = cms.PSet(hltTagPath=cms.string("HLT_PFJet80"),  hltThreshold=cms.double(140), l1Threshold=cms.double(90)),
            HLT_PFJet200 = cms.PSet(hltTagPath=cms.string("HLT_PFJet140"), hltThreshold=cms.double(200), l1Threshold=cms.double(120)),
            HLT_PFJet260 = cms.PSet(hltTagPath=cms.string("HLT_PFJet200"), hltThreshold=cms.double(260), l1Threshold=cms.double(170)),
            HLT_PFJet320 = cms.PSet(hltTagPath=cms.string("HLT_PFJet260"), hltThreshold=cms.double(320), l1Threshold=cms.double(170)),
            HLT_PFJet400 = cms.PSet(hltTagPath=cms.string("HLT_PFJet320"), hltThreshold=cms.double(400), l1Threshold=cms.double(170)),
            HLT_PFJet450 = cms.PSet(hltTagPath=cms.string("HLT_PFJet400"), hltThreshold=cms.double(450), l1Threshold=cms.double(170)),
            HLT_PFJet500 = cms.PSet(hltTagPath=cms.string("HLT_PFJet450"), hltThreshold=cms.double(500), l1Threshold=cms.double(170)),
        ),

        # binning (in reco. pT) for the trigger efficiency
        triggerEfficiencyBinning = cms.vdouble(*np.linspace(0, 800, 200))
    )
)
