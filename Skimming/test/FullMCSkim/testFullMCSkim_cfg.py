import os

import FWCore.ParameterSet.Config as cms

from Karma.Common.Tools import KarmaOptions, KarmaProcess
from Karma.Skimming.Configuration.MiniAOD import karmaSkim_94X_Run2016_17Jul2018_cff


# set up and parse command-line options
options = (
    karmaSkim_94X_Run2016_17Jul2018_cff.register_options(KarmaOptions())
        .setDefault('inputFiles', "file:///storage/9/dsavoiu/test_miniAOD/test_DY1JetsToLL_RunIISummer16MiniAODv3.root")
        .setDefault('outputFile', "testFullMCSkim_out.root")
        .setDefault('isData', False)
        .setDefault('globalTag', "94X_mcRun2_asymptotic_v3")
        .setDefault('maxEvents', 1000)#.setDefault('maxEvents', -1)
        .setDefault('dumpPython', True)
        .setDefault('useHLTFilter', False)
        .setDefault('jsonFilterFile', "")
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
