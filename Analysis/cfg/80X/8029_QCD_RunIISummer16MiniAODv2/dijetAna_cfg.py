from DijetAnalysis.Core.dijetPrelude_cff import *


# -- for testing and debugging
if not os.getenv("GC_VERSION"):
    # -- override CLI options for test
    options.inputFiles="file://{}".format(os.path.realpath("../../../../../../Skimming/test/FullMCSkim/testFullMCSkim_out.root"))
    options.isData=0
    options.globalTag="80X_mcRun2_asymptotic_2016_TrancheIV_v6"
    #options.edmOut="testFullAnalysis_out.root"
    options.maxEvents=1000
    options.dumpPython=1
    options.weightForStitching = 1.0
else:
    # -- running on grid node
    options.globalTag = "__GLOBALTAG__"
    options.isData = __IS_DATA__
    #options.edmOut = options.outputFile  # FIXME #.split('.')[:-1] + "_edmOut.root"
    options.dumpPython=False
    options.reportEvery = 100000 #int(max(1, 10**(round(math.log(__MAX_EVENTS__)/math.log(10))-1)))

    # temporary; gc later sets process.source.fileNames directly!
    options.inputFiles = [__FILE_NAMES__]
    options.weightForStitching = float(__CROSS_SECTION__) / float(__NUMBER_OF_EVENTS__)


# -- must be called at the beginning
process = createProcess("DIJETANA", num_threads=1)


# -- configure CMSSW modules

from DijetAnalysis.Analysis.JetTriggerObjectMatchingProducer_cfi import dijetJetTriggerObjectMatchingProducer
from DijetAnalysis.Analysis.JetGenJetMatchingProducer_cfi import dijetJetGenJetMatchingProducer
from DijetAnalysis.Analysis.CorrectedValidJetsProducer_cfi import dijetCorrectedValidJetsProducer
from DijetAnalysis.Analysis.CorrectedMETsProducer_cfi import dijetCorrectedMETsProducer
from DijetAnalysis.Analysis.NtupleProducer_cfi import dijetNtupleProducer
from DijetAnalysis.Analysis.NtupleSplicer_cfi import dijetNtupleSplicer


for _jet_radius in (4, 8):
    _jet_algo_name = "AK{}PFchs".format(_jet_radius)
    setattr(
        process,
        "correctedJets{}".format(_jet_algo_name),
        dijetCorrectedValidJetsProducer.clone(
            # -- input sources
            dijetEventSrc = cms.InputTag("dijetEvents"),
            dijetJetCollectionSrc = cms.InputTag("dijetUpdatedPatJets{}".format(_jet_algo_name)),

            # -- other configuration
            jecVersion = "{}/src/JECDatabase/textFiles/Summer16_07Aug2017_V11_MC/Summer16_07Aug2017_V11_MC".format(
                os.getenv('CMSSW_BASE'),
            ),
            jecAlgoName = cms.string(_jet_algo_name),
            jecLevels = cms.vstring(
                "L1FastJet",
                "L2Relative",
            ),
            jecUncertaintyShift = cms.double(0.0),

            jetIDSpec = cms.string("2016"),   # use "None" for no object-based JetID
            jetIDWorkingPoint = cms.string("TightLepVeto"),
        )
    )

    #setattr(
    #    process,
    #    "correctedJets{}JEUUp".format(_jet_algo_name),
    #    getattr(process, "correctedJets{}".format(_jet_algo_name)).clone(
    #        jecUncertaintyShift = cms.double(1.0),
    #    )
    #)

    #setattr(
    #    process,
    #    "correctedJets{}JEUDn".format(_jet_algo_name),
    #    getattr(process, "correctedJets{}".format(_jet_algo_name)).clone(
    #        jecUncertaintyShift = cms.double(-1.0),
    #    )
    #)

    setattr(
        process,
        "jetTriggerObjectMap{}".format(_jet_algo_name),
        dijetJetTriggerObjectMatchingProducer.clone(
            dijetEventSrc = cms.InputTag("dijetEvents"),
            dijetJetCollectionSrc = cms.InputTag("correctedJets{}".format(_jet_algo_name)),
            dijetTriggerObjectCollectionSrc = cms.InputTag("dijetTriggerObjects"),
        )
    )

    setattr(
        process,
        "jetGenJetMap{}".format(_jet_algo_name),
        dijetJetGenJetMatchingProducer.clone(
            dijetEventSrc = cms.InputTag("dijetEvents"),
            dijetJetCollectionSrc = cms.InputTag("correctedJets{}".format(_jet_algo_name)),
            dijetGenJetCollectionSrc = cms.InputTag("dijetGenJets{}".format(_jet_algo_name[:3])),
        )
    )

    setattr(
        process,
        "correctedMETs{}".format(_jet_algo_name),
        dijetCorrectedMETsProducer.clone(
            # -- input sources
            dijetEventSrc = cms.InputTag("dijetEvents"),
            dijetMETCollectionSrc = cms.InputTag("dijetCHSMETs"),
            dijetCorrectedJetCollectionSrc = cms.InputTag("correctedJets{}".format(_jet_algo_name)),
        )
    )


_jet_algo_name = 'AK4PFchs'

process.ntuple = dijetNtupleProducer.clone(
    dijetJetCollectionSrc = cms.InputTag("correctedJets{}".format(_jet_algo_name)),
    #dijetJetCollectionSrc = cms.InputTag("dijetUpdatedPatJetsNoJEC"),  # no JEC

    dijetJetTriggerObjectMapSrc = cms.InputTag("jetTriggerObjectMap{}".format(_jet_algo_name)),
    dijetJetGenJetMapSrc = cms.InputTag("jetGenJetMap{}".format(_jet_algo_name)),

    dijetMETCollectionSrc = cms.InputTag("correctedMETs{}".format(_jet_algo_name)),
    #dijetMETCollectionSrc = cms.InputTag("dijetCHSMETs"),  # no Type-I correction

    isData = cms.bool(options.isData),
    weightForStitching = cms.double(options.weightForStitching),

    triggerEfficienciesFile = cms.string(
        "{}/src/DijetAnalysis/Analysis/data/trigger_efficiencies/2016/trigger_efficiencies_bootstrapping_2018-09-24.root".format(os.getenv("CMSSW_BASE"))
    ),
)

# filter ensuring the existence of a leading jet pair
process.jetPairFilter = cms.EDFilter(
    "JetPairFilter",
    cms.PSet(
        dijetNtupleSrc = cms.InputTag("ntuple"),
    )
)

# filter ensuring that the leading jet is within eta
process.leadingJetRapidityFilter = cms.EDFilter(
    "LeadingJetRapidityFilter",
    cms.PSet(
        dijetNtupleSrc = cms.InputTag("ntuple"),
        maxJetAbsRapidity = cms.double(3.0),
    )
)

# filter ensuring that the leading jet is above pt threshold
process.leadingJetPtFilter = cms.EDFilter(
    "LeadingJetPtFilter",
    cms.PSet(
        dijetNtupleSrc = cms.InputTag("ntuple"),
        minJetPt = cms.double(60),
    )
)

# analyzer for writing out flat ntuple
process.flatNtupleWriter = cms.EDAnalyzer(
    "NtupleFlatOutput",
    cms.PSet(
        isData = cms.bool(options.isData),
        dijetNtupleSrc = cms.InputTag("ntuple"),
        outputFileName = cms.string(options.outputFile),
        treeName = cms.string("Events"),
        checkForCompleteness = cms.bool(False),
    )
)

_main_sequence = cms.Sequence(
    getattr(process, 'correctedJets{}'.format(_jet_algo_name)) *
    getattr(process, 'jetGenJetMap{}'.format(_jet_algo_name)) *
    getattr(process, 'jetTriggerObjectMap{}'.format(_jet_algo_name)) *
    getattr(process, 'correctedMETs{}'.format(_jet_algo_name)) *
    process.ntuple *
    process.jetPairFilter *
    #process.leadingJetRapidityFilter *
    process.leadingJetPtFilter *
    process.flatNtupleWriter
)
process.path = cms.Path(_main_sequence)


# -- must be called at the end
finalizeAndRun(process, outputCommands=['keep *_*_*_DIJETANA', 'drop *_jetTriggerObjectMap_*_DIJETANA'])


## selective writeout based on path decisions
#process.edmOut.SelectEvents = cms.untracked.PSet(
#    SelectEvents = cms.vstring('path')
#)
