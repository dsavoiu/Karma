from DijetAnalysis.Core.dijetPrelude_cff import *


# -- override CLI options for test
options.inputFiles="file://{}".format(os.path.realpath("../../../Skimming/test/FullSkim/testFullSkim_out.root"))
options.isData=1
options.globalTag="80X_dataRun2_2016LegacyRepro_v4"
#options.edmOut="testFullAnalysis_out.root"  # no EDM output
options.maxEvents=-1 #10 #000
options.dumpPython=1


# -- must be called at the beginning
process = createProcess("DIJETANA", num_threads=1)


# -- configure CMSSW modules

from DijetAnalysis.Analysis.JetTriggerObjectMatchingProducer_cfi import dijetJetTriggerObjectMatchingProducer
from DijetAnalysis.Analysis.CorrectedValidJetsProducer_cfi import dijetCorrectedValidJetsProducer
from DijetAnalysis.Analysis.CorrectedMETsProducer_cfi import dijetCorrectedMETsProducer
from DijetAnalysis.Analysis.NtupleProducer_cfi import dijetNtupleProducer
from DijetAnalysis.Analysis.NtupleSplicer_cfi import dijetNtupleSplicer

process.correctedJets = dijetCorrectedValidJetsProducer.clone(
    jecVersion = "{}/src/JECDatabase/textFiles/Summer16_07Aug2017{RUN}_V11_DATA/Summer16_07Aug2017{RUN}_V11_DATA".format(
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
    #dijetJetCollectionSrc = cms.InputTag("dijetUpdatedPatJetsNoJEC"),
    dijetTriggerObjectCollectionSrc = cms.InputTag("dijetTriggerObjects"),
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

    dijetMETCollectionSrc = cms.InputTag("correctedMETs"),
    #dijetMETCollectionSrc = cms.InputTag("dijetCHSMETs"),  # no Type-I correction

    isData = cms.bool(options.isData),

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
        outputFileName = cms.string("output_flat.root"),
        treeName = cms.string("Events"),
        checkForCompleteness = cms.bool(False),
    )
)

_main_sequence = cms.Sequence(
    #process.uncorrectedJets *
    process.correctedJets *
    #process.correctedJetsDnShift *
    #process.correctedJetsUpShift *
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
