import FWCore.ParameterSet.Config as cms

import numpy as np


karmaTriggerEfficienciesAnalyzer = cms.EDAnalyzer(
    "TriggerEfficienciesAnalyzer",
    cms.PSet(

        outputFile = cms.string("triggerEfficiencies.root"),

        # the name of the process which created the trigger decisions/objects
        hltProcessName = cms.string("HLT"),

        # regex matching paths to use as event preselection
        hltPreselectionPathRegex = cms.string("^HLT_IsoMu24_v[0-9]+$"),
        #hltPreselectionPathRegex = cms.string("^HLT_PFJet140_v[0-9]+$"),
        #hltPreselectionPathRegex = cms.string("^HLT_ZeroBias_v[0-9]+$"),

        # names of the paths for which to measure the trigger efficiencies on the preselected sample
        hltProbePaths = cms.vstring(
            "HLT_PFJet40",   # "^HLT_PFJet40_v[0-9]+$",
            "HLT_PFJet60",   # "^HLT_PFJet60_v[0-9]+$",
            "HLT_PFJet80",   # "^HLT_PFJet80_v[0-9]+$",
            "HLT_PFJet140",  # "^HLT_PFJet140_v[0-9]+$",
            "HLT_PFJet200",  # "^HLT_PFJet200_v[0-9]+$",
            "HLT_PFJet260",  # "^HLT_PFJet260_v[0-9]+$",
            "HLT_PFJet320",  # "^HLT_PFJet320_v[0-9]+$",
            "HLT_PFJet400",  # "^HLT_PFJet400_v[0-9]+$",
            "HLT_PFJet450",  # "^HLT_PFJet450_v[0-9]+$",
            "HLT_PFJet500",  # "^HLT_PFJet500_v[0-9]+$",
        ),

        # for each path, a set of filters that trigger objects are required to pass
        hltProbePathFilterSpecs = cms.PSet(
            HLT_PFJet40  = cms.VPSet(
                #cms.PSet(filterName=cms.string('hltL1sZeroBias'), filterThreshold=cms.double(0), isL1=cms.bool(True)),
                cms.PSet(filterName=cms.string('hltSinglePFJet40'), filterThreshold=cms.double(40), isL1=cms.bool(False)),
            ),
            HLT_PFJet60  = cms.VPSet(
                cms.PSet(filterName=cms.string('hltL1sSingleJet35'), filterThreshold=cms.double(35), isL1=cms.bool(True)),
                cms.PSet(filterName=cms.string('hltSinglePFJet60'), filterThreshold=cms.double(60), isL1=cms.bool(False)),
            ),
            HLT_PFJet80  = cms.VPSet(
                cms.PSet(filterName=cms.string('hltL1sSingleJet60'), filterThreshold=cms.double(60), isL1=cms.bool(True)),
                cms.PSet(filterName=cms.string('hltSinglePFJet80'), filterThreshold=cms.double(80), isL1=cms.bool(False)),
            ),
            HLT_PFJet140 = cms.VPSet(
                cms.PSet(filterName=cms.string('hltL1sSingleJet90'), filterThreshold=cms.double(90), isL1=cms.bool(True)),
                cms.PSet(filterName=cms.string('hltSinglePFJet140'), filterThreshold=cms.double(140), isL1=cms.bool(False)),
            ),
            HLT_PFJet200 = cms.VPSet(
                cms.PSet(filterName=cms.string('hltL1sSingleJet120'), filterThreshold=cms.double(120), isL1=cms.bool(True)),
                cms.PSet(filterName=cms.string('hltSinglePFJet200'), filterThreshold=cms.double(200), isL1=cms.bool(False)),
            ),
            HLT_PFJet260 = cms.VPSet(
                cms.PSet(filterName=cms.string('hltL1sSingleJet170IorSingleJet180IorSingleJet200'), filterThreshold=cms.double(170), isL1=cms.bool(True)),
                cms.PSet(filterName=cms.string('hltSinglePFJet260'), filterThreshold=cms.double(260), isL1=cms.bool(False)),
            ),
            HLT_PFJet320 = cms.VPSet(
                cms.PSet(filterName=cms.string('hltL1sSingleJet170IorSingleJet180IorSingleJet200'), filterThreshold=cms.double(170), isL1=cms.bool(True)),
                cms.PSet(filterName=cms.string('hltSinglePFJet320'), filterThreshold=cms.double(320), isL1=cms.bool(False)),
            ),
            HLT_PFJet400 = cms.VPSet(
                cms.PSet(filterName=cms.string('hltL1sSingleJet170IorSingleJet180IorSingleJet200'), filterThreshold=cms.double(170), isL1=cms.bool(True)),
                cms.PSet(filterName=cms.string('hltSinglePFJet400'), filterThreshold=cms.double(400), isL1=cms.bool(False)),
            ),
            HLT_PFJet450 = cms.VPSet(
                cms.PSet(filterName=cms.string('hltL1sSingleJet170IorSingleJet180IorSingleJet200'), filterThreshold=cms.double(170), isL1=cms.bool(True)),
                cms.PSet(filterName=cms.string('hltSinglePFJet450'), filterThreshold=cms.double(450), isL1=cms.bool(False)),
            ),
            HLT_PFJet500 = cms.VPSet(
                cms.PSet(filterName=cms.string('hltL1sSingleJet170IorSingleJet180IorSingleJet200'), filterThreshold=cms.double(170), isL1=cms.bool(True)),
                cms.PSet(filterName=cms.string('hltSinglePFJet500'), filterThreshold=cms.double(500), isL1=cms.bool(False)),
            ),
        ),

        # binning (in reco. pT) for the trigger efficiency
        triggerEfficiencyBinning = cms.vdouble(*np.linspace(0, 700, 200))
    )
)
