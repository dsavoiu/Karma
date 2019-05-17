from Karma.Common.Tools import KarmaOptions, KarmaProcess


# -- override CLI options for test
options.inputFiles="file://{}".format(os.path.realpath("../../../data/test_JetHT2016G.root"))
options.isData=1
options.globalTag="80X_dataRun2_2016LegacyRepro_v4"
options.edmOut="testJetCollectionProducer_out.root"
options.maxEvents=1000
options.dumpPython=1


# -- must be called at the beginning
process = createProcess("DIJET", num_threads=1)


enableVerboseLogging(process)

# -- configure CMSSW modules

from Karma.Skimming.JetCollectionProducer_cfi import karmaJetCollectionProducer

process.dijetJets = karmaJetCollectionProducer
process.path *= process.dijetJets


# -- must be called at the end
finalizeAndRun(process, outputCommands=['keep *_*_*_DIJET'])

