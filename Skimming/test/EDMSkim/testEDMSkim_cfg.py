import FWCore.PythonUtilities.LumiList as LumiList

from Karma.Common.karmaPrelude_cff import *

# -- override CLI options for test
options.inputFiles="file://{}".format(os.path.realpath("../../data/test_JetHT2016G.root"))
options.isData=1
options.globalTag="80X_dataRun2_2016LegacyRepro_v4"
options.edmOut="testEDMSkim_out.root"
options.maxEvents=100 #10000
options.dumpPython=1


# -- must be called at the beginning
process = createProcess("DIJET", num_threads=1)

## enable verbose log file output
#enableVerboseLogging(process)

# -- configure CMSSW modules

# don't use JetToolbox to recluster jets
# addJetToolboxSequences(process,
#                        isData=options.isData,
#                        jet_algorithm_specs=('ak4',),
#                        pu_subtraction_methods=('', 'CHS'),
#                        do_pu_jet_id=False)


# -- must be called at the end
finalizeAndRun(process, outputCommands=[
    'drop *',
    'keep *_selectedPatTrigger_*_*'
])

# selective writeout based on path decisions
#process.edmOut.SelectEvents = cms.untracked.PSet(
#    SelectEvents = cms.vstring('path')
#)
