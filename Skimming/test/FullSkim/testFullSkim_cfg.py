from DijetAnalysis.Core.dijetPrelude_cff import *


# -- override CLI options for test
options.inputFiles="file://{}".format(os.path.realpath("../../../data/test_JetHT2016G.root"))
options.isData=1
options.globalTag="80X_dataRun2_2016LegacyRepro_v4"
options.edmOut="testFullSkim_out.root"
options.maxEvents=1000
options.dumpPython=1


# -- must be called at the beginning
process = createProcess("DIJET", num_threads=1)


enableVerboseLogging(process)

# ignore errors from HLTPrescaleProvider (issued when
# no unique L1 prescale can be found for a HLT path)
process.MessageLogger.categories.append("HLTPrescaleProvider")
process.MessageLogger.cerr.HLTPrescaleProvider = cms.untracked.PSet(
    limit = cms.untracked.int32(5),
)

# -- configure CMSSW modules

from DijetAnalysis.Skimming.TriggerObjectCollectionProducer_cfi import dijetTriggerObjectCollectionProducer
from DijetAnalysis.Skimming.JetCollectionProducer_cfi import dijetJetCollectionProducer
from DijetAnalysis.Skimming.EventProducer_cfi import dijetEventProducer

process.dijetEvents = dijetEventProducer
process.path *= process.dijetEvents

process.dijetJets = dijetJetCollectionProducer
process.path *= process.dijetJets

process.dijetTriggerObjects = dijetTriggerObjectCollectionProducer
process.path *= process.dijetTriggerObjects


# -- must be called at the end
finalizeAndRun(process, outputCommands=['keep *_*_*_DIJET'])

