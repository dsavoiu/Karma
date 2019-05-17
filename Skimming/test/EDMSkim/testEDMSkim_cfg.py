import os

import FWCore.ParameterSet.Config as cms

import FWCore.PythonUtilities.LumiList as LumiList

from Karma.Common.Tools import KarmaOptions, KarmaProcess

# set up and parse command-line options
options = (
    KarmaOptions()
        .setDefault('inputFiles', "file:///storage/9/dsavoiu/test_miniAOD/test_DoubleEG_Run2016G_17Jul2018_MINIAOD_10events.root")
        .setDefault('isData', True)
        .setDefault('globalTag', "94X_dataRun2_v10")
        .setDefault('outputFile', "testEDMSkim_out.root")
        .setDefault('maxEvents', 100)
        .setDefault('dumpPython', True)
).parseArguments()


# create the process
process = KarmaProcess(
    "EDMSKIM",
    input_files=options.inputFiles,
    max_events=options.maxEvents,
    global_tag=options.globalTag,
    edm_out=options.outputFile,
    num_threads=1
)

# create the main module path
process.add_path('path')

# enable verbose log file output
#enableVerboseLogging(process)


# == configure CMSSW modules ==========================================
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
