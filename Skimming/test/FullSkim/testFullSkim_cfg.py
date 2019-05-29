import os

import FWCore.ParameterSet.Config as cms

from Karma.Common.Tools import KarmaOptions, KarmaProcess
from Karma.Skimming.Configuration.MiniAOD import karmaSkim_94X_Run2016_17Jul2018_cff


# set up and parse command-line options
options = (
    karmaSkim_94X_Run2016_17Jul2018_cff.register_options(KarmaOptions())
        .setDefault('inputFiles', "root://xrootd-cms.infn.it//store/data/Run2016G/JetHT/MINIAOD/17Jul2018-v1/60000/06E6B214-5D91-E811-A1AF-0025905C2CBE.root")
        .setDefault('outputFile', "testFullSkim_out.root")
        .setDefault('isData', True)
        .setDefault('globalTag', "94X_dataRun2_v10")
        .setDefault('maxEvents', 1000)#.setDefault('maxEvents', -1)
        .setDefault('dumpPython', True)
        .setDefault('useHLTFilter', False)
        .setDefault('jsonFilterFile', "")
        #.setDefault('jsonFilterFile', "{}/src/Karma/Skimming/data/json/2016/Cert_271036-284044_13TeV_PromptReco_Collisions16_JSON.json".format(os.getenv("CMSSW_BASE")))
        .setDefault('withPATCollections', False)
        .setDefault('numThreads', 1)
).parseArguments()


# create the process
process = KarmaProcess(
    "KARMASKIM",
    input_files=options.inputFiles,
    max_events=options.maxEvents,
    global_tag=options.globalTag,
    edm_out=options.outputFile,
    num_threads=options.numThreads,
)

process.enable_verbose_logging()  # for testing

# configure the process
karmaSkim_94X_Run2016_17Jul2018_cff.configure(process, options)

# dump expanded cmsRun configuration
if options.dumpPython:
    process.dump_python('.'.join(options.outputFile.split('.')[:-1]) + '_dump.py', overwrite=True)

# print out configuration before running
process.print_configuration()
