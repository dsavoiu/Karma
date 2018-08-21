from DijetAnalysis.Core.dijetPrelude_cff import *


# -- override CLI options for test
options.inputFiles="file://{}".format(os.path.realpath("../../../Skimming/test/FullSkim/testFullSkim_out.root"))
options.isData=1
options.globalTag="80X_dataRun2_2016LegacyRepro_v4"
#options.edmOut="testFullAnalysis_out.root"  # no EDM output
options.maxEvents=-1 #10 #000
options.dumpPython=1

SPLICES = dict(
    YS01YB01 = "0<abs(jet12ystar)<=1&&0<abs(jet12yboost)<=1",
    YS01YB12 = "0<abs(jet12ystar)<=1&&1<abs(jet12yboost)<=2",
    YS01YB23 = "0<abs(jet12ystar)<=1&&2<abs(jet12yboost)<=3",
    YS12YB01 = "1<abs(jet12ystar)<=2&&0<abs(jet12yboost)<=1",
    YS12YB12 = "1<abs(jet12ystar)<=2&&1<abs(jet12yboost)<=2",
    YS23YB01 = "2<abs(jet12ystar)<=3&&0<abs(jet12yboost)<=1",
)

# -- must be called at the beginning
process = createProcess("DIJETANA", num_threads=1)


# -- configure CMSSW modules

from DijetAnalysis.Analysis.JetTriggerObjectMatchingProducer_cfi import dijetJetTriggerObjectMatchingProducer
from DijetAnalysis.Analysis.CorrectedValidJetsProducer_cfi import dijetCorrectedValidJetsProducer
from DijetAnalysis.Analysis.NtupleProducer_cfi import dijetNtupleProducer
from DijetAnalysis.Analysis.NtupleSplicer_cfi import dijetNtupleSplicer

process.correctedJets = dijetCorrectedValidJetsProducer.clone(
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

#process.uncorrectedJets = dijetCorrectedValidJetsProducer.clone(
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

# analyzer for writing out flat ntuple
process.flatNtupleWriter = cms.EDAnalyzer(
    "NtupleFlatOutput",
    cms.PSet(
        dijetNtupleSrc = cms.InputTag("ntuple"),
        outputFileName = cms.string("output_flat.root"),
        treeName = cms.string("Events"),
    )
)

_main_sequence = cms.Sequence(
    #process.uncorrectedJets *
    process.correctedJets *
    process.correctedJetsDnShift *
    process.correctedJetsUpShift *
    process.jetTriggerObjectMap *
    process.ntuple *
    process.jetPairFilter *
    process.leadingJetEtaFilter *
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

### # create ystar-yboost splices
### for splice_name, splice_filter_expr in SPLICES.iteritems():
###     setattr(
###         process,
###         "ntuple{}".format(splice_name),
###         dijetNtupleSplicer.clone(
###             dijetNtupleSrc = cms.InputTag("ntuple"),
###             spliceName = cms.string(splice_name),
###             spliceFilterExpression = cms.string(splice_filter_expr),
###         )
###     )
###     setattr(
###         process,
###         "path{}".format(splice_name),
###         cms.Path(
###             preSequence *
###             getattr(process, "ntuple{}".format(splice_name))
###         )
###     )
###     _file_basename = _output_filename = process.edmOut.fileName.value()
###     if _file_basename.endswith(".root"):
###         _file_basename = _file_basename[:-5]
###     setattr(
###         process,
###         "edmOut{}".format(splice_name),
###         process.edmOut.clone(
###             fileName = cms.untracked.string("{}_splice_{}.root".format(_file_basename, splice_name)),
###             SelectEvents = cms.untracked.PSet(
###                 SelectEvents = cms.vstring("path{}".format(splice_name))
###             )
###         )
###     )
###     process.endpath *= getattr(process, "edmOut{}".format(splice_name))
