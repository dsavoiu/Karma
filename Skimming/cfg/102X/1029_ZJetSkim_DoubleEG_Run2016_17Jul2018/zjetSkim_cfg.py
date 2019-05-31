import math
import os
import sys

import FWCore.ParameterSet.Config as cms

from Karma.Skimming.Configuration.MiniAOD import zjetSkim_94X_Run2016_17Jul2018
from Karma.Common.Tools import KarmaOptions, KarmaProcess


# set up and parse command-line options
if not os.getenv("GC_VERSION"):
    # -- *not* running in grid -> simple test
    options = (
        zjetSkim_94X_Run2016_17Jul2018.register_options(KarmaOptions())
            .setDefault('inputFiles', "root://xrootd-cms.infn.it//store/data/Run2016G/DoubleEG/MINIAOD/17Jul2018-v1/90000/FE301219-5895-E811-A333-0425C5DE7BEA.root")
            .setDefault('outputFile', "testFullSkim_out_12events.root")
            .setDefault('isData', True)
            .setDefault('globalTag', "94X_dataRun2_v10")
            .setDefault('maxEvents', 12)
            .setDefault('dumpPython', True)
            .setDefault('useHLTFilter', False)
            .setDefault('jsonFilterFile', os.path.realpath("{}/src/Karma/Skimming/data/json/2016/Cert_271036-284044_13TeV_PromptReco_Collisions16_JSON.json".format(os.getenv("CMSSW_BASE"))))
            .setDefault('withPATCollections', False)
            .setDefault('numThreads', 1)
    ).parseArguments()
else:
    # -- running on grid node -> "production" config
    options = (
        zjetSkim_94X_Run2016_17Jul2018.register_options(KarmaOptions())
            .setDefault('inputFiles', [__FILE_NAMES__])
            .setDefault('outputFile', "output.root")
            .setDefault('isData', __IS_DATA__)
            .setDefault('globalTag', "__GLOBALTAG__")
            .setDefault('maxEvents', -1)
            .setDefault('dumpPython', False)
            .setDefault('useHLTFilter', False)
            .setDefault('jsonFilterFile', "")  # no filter in MC
            .setDefault('withPATCollections', False)
            .setDefault('reportEvery', int(max(1, 10**(round(math.log(__MAX_EVENTS__)/math.log(10))-1))))
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

if not os.getenv("GC_VERSION"):
    process.enable_verbose_logging()  # for testing

# configure the process
zjetSkim_94X_Run2016_17Jul2018.configure(process, options)

# dump expanded cmsRun configuration
if options.dumpPython:
    process.dump_python('.'.join(options.outputFile.split('.')[:-1]) + '_dump.py', overwrite=True)

# print out configuration before running
process.print_configuration()
