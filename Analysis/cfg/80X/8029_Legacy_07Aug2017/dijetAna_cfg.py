from DijetAnalysis.Core.dijetPrelude_cff import *


# -- for testing and debugging
if not os.getenv("GC_VERSION"):
    # -- override CLI options for test
    options.inputFiles="file://{}".format(os.path.realpath("../../../../Skimming/test/FullSkim/testFullSkim_out.root"))
    options.isData=1
    options.globalTag="80X_dataRun2_2016LegacyRepro_v4"
    options.edmOut="testSkim_out.root"
    options.maxEvents=1000
    options.dumpPython=1
else:
    # -- running on grid node
    options.globalTag = "__GLOBALTAG__"
    options.isData = __IS_DATA__
    options.edmOut = options.outputFile  # FIXME #.split('.')[:-1] + "_edmOut.root"
    options.dumpPython=False
    options.reportEvery = 100000 #int(max(1, 10**(round(math.log(__MAX_EVENTS__)/math.log(10))-1)))

    # temporary; gc later sets process.source.fileNames directly!
    options.inputFiles = [__FILE_NAMES__]


# -- must be called at the beginning
process = createProcess("DIJETANA", num_threads=1)


# -- configure CMSSW modules

from DijetAnalysis.Analysis.JetTriggerObjectMatchingProducer_cfi import dijetJetTriggerObjectMatchingProducer
from DijetAnalysis.Analysis.JECProducer_cfi import dijetJECProducer
from DijetAnalysis.Analysis.NtupleProducer_cfi import dijetNtupleProducer
from DijetAnalysis.Analysis.NtupleSplicer_cfi import dijetNtupleSplicer

process.correctedJets = dijetJECProducer.clone(
    jecVersion = "{}/src/JECDatabase/textFiles/Summer16_07Aug2017{RUN}_V12_DATA/Summer16_07Aug2017{RUN}_V12_DATA".format(
        os.getenv('CMSSW_BASE'),
        RUN="GH"
    )
)
process.correctedJetsUpShift = process.correctedJets.clone(
    jecUncertaintyShift = cms.double(1.0),
)
process.correctedJetsDnShift = process.correctedJets.clone(
    jecUncertaintyShift = cms.double(-1.0),
)

#process.uncorrectedJets = dijetJECProducer.clone(
#    jecVersion = "{}/src/JECDatabase/textFiles/Summer16_07Aug2017{RUN}_V12_DATA/Summer16_07Aug2017{RUN}_V12_DATA".format(
#        os.getenv('CMSSW_BASE'),
#        RUN="GH"
#    ),
#    jecLevels = cms.vstring("L3Absolute"),
#)


process.jetTriggerObjectMap = dijetJetTriggerObjectMatchingProducer.clone(
    dijetEventSrc = cms.InputTag("dijetEvents"),
    dijetJetCollectionSrc = cms.InputTag("correctedJets"),
    #dijetJetCollectionSrc = cms.InputTag("dijetUpdatedPatJetsNoJEC"),
    dijetTriggerObjectCollectionSrc = cms.InputTag("dijetTriggerObjects"),
)

process.ntuple = dijetNtupleProducer.clone(
    dijetJetCollectionSrc = cms.InputTag("correctedJets"),
    #dijetJetCollectionSrc = cms.InputTag("dijetUpdatedPatJetsNoJEC"),
    dijetJetTriggerObjectMapSrc = cms.InputTag("jetTriggerObjectMap"),

    triggerEfficienciesFile = cms.string(
        "{}/src/DijetAnalysis/Analysis/data/trigger_efficiencies/2016/trigger_efficiencies.root".format(os.getenv("CMSSW_BASE"))
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
process.leadingJetEtaFilter = cms.EDFilter(
    "LeadingJetEtaFilter",
    cms.PSet(
        dijetNtupleSrc = cms.InputTag("ntuple"),
        maxJetAbsEta = cms.double(2.5),
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

preSequence = cms.Sequence(
    #process.uncorrectedJets *
    process.correctedJets *
    process.correctedJetsDnShift *
    process.correctedJetsUpShift *
    process.jetTriggerObjectMap *
    process.ntuple * 
    process.jetPairFilter * 
    process.leadingJetEtaFilter * 
    process.leadingJetPtFilter
);

process.path = cms.Path(preSequence)


# -- must be called at the end
finalizeAndRun(process, outputCommands=['keep *_*_*_DIJETANA', 'drop *_jetTriggerObjectMap_*_DIJETANA'])

# selective writeout based on path decisions
process.edmOut.SelectEvents = cms.untracked.PSet(
    SelectEvents = cms.vstring('path')
)
