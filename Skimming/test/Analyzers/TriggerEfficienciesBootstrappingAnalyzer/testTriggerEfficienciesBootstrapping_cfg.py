from Karma.Common.Tools import KarmaOptions, KarmaProcess


# -- override CLI options for test
options.inputFiles=["file://{}".format(os.path.realpath("../../../data/test_JetHT2016G.root")), "file://{}".format(os.path.realpath("../../../data/test_JetHT2016G.root"))]
#options.inputFiles="file://{}".format(os.path.realpath("../../../data/test_JetHT2016G.root"))
options.isData=1
options.globalTag="80X_dataRun2_2016LegacyRepro_v4"
options.outputFile="testTriggerEfficiencies_out.root"
#options.maxEvents=10000 #100
options.maxEvents=-1
options.dumpPython=1


# -- must be called at the beginning
#process = createProcess("DIJET", num_threads=1)
process = createProcess("DIJET", num_threads=2)


# -- route more detailed output to log files
process.MessageLogger.destinations.extend(cms.untracked.vstring(
    'detailedInfo', 'critical', 'out',
))
process.MessageLogger.categories.extend(cms.untracked.vstring(
    'TriggerEfficienciesBootstrappingAnalyzer', 'GlobalCacheWithOutputFile',
))
process.MessageLogger.out = cms.untracked.PSet(
    threshold = cms.untracked.string('WARNING'),
    FwkReport = cms.untracked.PSet(
        reportEvery = cms.untracked.int32(3),
    ),
)
process.MessageLogger.detailedInfo = cms.untracked.PSet(
    threshold = cms.untracked.string('INFO'),
    FwkReport = cms.untracked.PSet(
        reportEvery = cms.untracked.int32(1),
    ),
)
process.MessageLogger.critical = cms.untracked.PSet(
    threshold = cms.untracked.string('ERROR'),
)

# -- configure CMSSW modules

from Karma.Skimming.TriggerEfficienciesBootstrappingAnalyzer_cfi import dijetTriggerEfficienciesBootstrappingAnalyzer

process.triggerEfficiencies = dijetTriggerEfficienciesBootstrappingAnalyzer
process.path *= process.triggerEfficiencies


# -- must be called at the end
finalizeAndRun(process)

