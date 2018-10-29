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

process.correctedJets = dijetCorrectedValidJetsProducer.clone(
    jecVersion = "{}/src/JECDatabase/textFiles/Summer16_07Aug2017_V11_MC/Summer16_07Aug2017_V11_MC".format(
        os.getenv('CMSSW_BASE'),
    ),
)
process.correctedJetsUpShift = process.correctedJets.clone(
    jecUncertaintyShift = cms.double(1.0),
)
process.correctedJetsDnShift = process.correctedJets.clone(
    jecUncertaintyShift = cms.double(-1.0),
)

#process.uncorrectedJets = dijetCorrectedValidJetsProducer.clone(
#    jecVersion = "{}/src/JECDatabase/textFiles/Summer16_07Aug2017{RUN}_V11_DATA/Summer16_07Aug2017{RUN}_V11_DATA".format(
#        os.getenv('CMSSW_BASE'),
#        RUN="GH"
#    ),
#    jecLevels = cms.vstring("L3Absolute"),
#)

process.jetTriggerObjectMap = dijetJetTriggerObjectMatchingProducer.clone(
    dijetEventSrc = cms.InputTag("dijetEvents"),
    dijetJetCollectionSrc = cms.InputTag("correctedJets"),
    dijetTriggerObjectCollectionSrc = cms.InputTag("dijetTriggerObjects"),
)
process.jetGenJetMap = dijetJetGenJetMatchingProducer.clone(
    dijetEventSrc = cms.InputTag("dijetEvents"),
    dijetJetCollectionSrc = cms.InputTag("correctedJets"),
    dijetGenJetCollectionSrc = cms.InputTag("dijetGenJets"),
)

process.correctedMETs = dijetCorrectedMETsProducer.clone(
    # -- input sources
    dijetEventSrc = cms.InputTag("dijetEvents"),
    dijetMETCollectionSrc = cms.InputTag("dijetCHSMETs"),
    dijetCorrectedJetCollectionSrc = cms.InputTag("correctedJets"),
)

process.ntuple = dijetNtupleProducer.clone(
    dijetJetCollectionSrc = cms.InputTag("correctedJets"),
    #dijetJetCollectionSrc = cms.InputTag("dijetUpdatedPatJetsNoJEC"),  # no JEC

    dijetJetTriggerObjectMapSrc = cms.InputTag("jetTriggerObjectMap"),
    dijetJetGenJetMapSrc = cms.InputTag("jetGenJetMap"),

    dijetMETCollectionSrc = cms.InputTag("correctedMETs"),
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
    #process.uncorrectedJets *
    process.correctedJets *
    #process.correctedJetsDnShift *
    #process.correctedJetsUpShift *
    process.jetGenJetMap *
    process.jetTriggerObjectMap *
    process.correctedMETs *
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
