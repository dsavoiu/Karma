import os

import FWCore.ParameterSet.Config as cms

from Karma.DijetAnalysis.Configuration import dijetAnalysis_94X_Run2016_17Jul2018_cff
from Karma.Common.Tools import KarmaOptions, KarmaProcess


# set up and parse command-line options
if not os.getenv("GC_VERSION"):
    # -- *not* running in grid -> simple test
    options = (
        dijetAnalysis_94X_Run2016_17Jul2018_cff.register_options(KarmaOptions())
            .setDefault('inputFiles', "root://cmsxrootd-redirectors.gridka.de//store/user/dsavoiu/Dijet/skims/KarmaSkim_ZJetsToNuNu_Zpt-100to200_RunIISummer16MiniAODv3_2019-07-03/job_0_output.root")
            .setDefault('outputFile', "testFullMCAnalysis_out.root")
            .setDefault('maxEvents', 1000)#.setDefault('maxEvents', -1)
            .setDefault('isData', False)
            .setDefault('globalTag', "94X_mcRun2_asymptotic_v3")
            .setDefault('dumpPython', True)
            .setDefault('numThreads', 1)
            #.setDefault('jecVersion', "Summer16_07Aug2017_V11")
            .setDefault('jerVersion', "Summer16_25nsV1")
            .setDefault('jerMethod', "stochastic")
            .setDefault('weightForStitching', 1.0)  # ignore for testing
            .setDefault('jecFromGlobalTag', True)
            .setDefault('edmOut', True)
    ).parseArguments()
else:
    # -- running on grid node -> "production" config
    options = (
        dijetAnalysis_94X_Run2016_17Jul2018_cff.register_options(KarmaOptions())
            .setDefault('inputFiles', [__FILE_NAMES__])
            .setDefault('outputFile', "output.root")
            .setDefault('isData', __IS_DATA__)
            .setDefault('globalTag', "__GLOBALTAG__")
            .setDefault('maxEvents', -1)
            .setDefault('dumpPython', False)
            .setDefault('reportEvery', 10000)
            .setDefault('numThreads', 1)
            .setDefault('jecVersion', "__JEC_VERSION__")
            .setDefault('jerVersion', "__JER_VERSION__")
            .setDefault('jerMethod', "stochastic")
            .setDefault('weightForStitching', float(__CROSS_SECTION__) / float(__NUMBER_OF_EVENTS__))
            .setDefault('jecFromGlobalTag', True)
            .setDefault('edmOut', False)
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
