import os

import FWCore.ParameterSet.Config as cms

from Karma.Common.Tools import KarmaOptions, KarmaProcess
from Karma.DijetAnalysis.Configuration import dijetAnalysis_94X_Run2016_17Jul2018_cff


# set up and parse command-line options
options = (
    dijetAnalysis_94X_Run2016_17Jul2018_cff.register_options(KarmaOptions())
        .setDefault('inputFiles', "file://{}/{}".format(os.getenv("CMSSW_BASE"), "src/Karma/Skimming/test/FullMCSkim/testFullMCSkim_out.root"))
        .setDefault('outputFile', "testFullMCAnalysis_out.root")
        .setDefault('isData', False)
        .setDefault('globalTag', "94X_mcRun2_asymptotic_v3")
        .setDefault('maxEvents', 1000)#.setDefault('maxEvents', -1)
        .setDefault('dumpPython', True)
        .setDefault('numThreads', 1)
        .setDefault('jecVersion', "Summer16_07Aug2017_V11")
        .register('edmOut',
                  type_=bool,
                  default=False,
                  description="(for testing only) Write out EDM file.")
).parseArguments()


# create the process
process = KarmaProcess(
    "DIJETANA",
    input_files=options.inputFiles,
    max_events=options.maxEvents,
    global_tag=options.globalTag,
    edm_out='.'.join(options.outputFile.split('.')[:-1]) + "_edmOut.root" if options.edmOut else None,
    num_threads=options.numThreads,
)

process.enable_verbose_logging()  # for testing

# configure the process
dijetAnalysis_94X_Run2016_17Jul2018_cff.configure(process, options)

# dump expanded cmsRun configuration
if options.dumpPython:
    process.dump_python('.'.join(options.outputFile.split('.')[:-1]) + '_dump.py', overwrite=True)

# print out configuration before running
process.print_configuration()
