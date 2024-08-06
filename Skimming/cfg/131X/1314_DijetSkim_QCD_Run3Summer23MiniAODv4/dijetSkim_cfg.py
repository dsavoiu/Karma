import math
import os
import sys

import FWCore.ParameterSet.Config as cms

from Karma.Skimming.Configuration.MiniAOD import dijetSkim_131X_Run2023_Summer23MiniAODv4
from Karma.Common.Tools import KarmaOptions, KarmaProcess

# set up and parse command-line options
if not os.getenv("GC_VERSION"):
    # -- *not* running in grid -> simple test
    options = (
        dijetSkim_131X_Run2023_Summer23MiniAODv4.register_options(KarmaOptions())
            #.setDefault('inputFiles', "davs://dcache-cms-webdav-wan.desy.de:2880/pnfs/desy.de/cms/tier2/store/mc/Run3Summer23MiniAODv4/QCD_PT-1800to2400_TuneCP5_13p6TeV_pythia8/MINIAODSIM/130X_mcRun3_2023_realistic_v14-v2/50000/3c23a1f0-11f7-403b-8272-2fff5ed5fc61.root")
            .setDefault('inputFiles', "file:/nfs/dust/cms/user/dsavoiu/tmp/3c23a1f0-11f7-403b-8272-2fff5ed5fc61.root")
            .setDefault('outputFile', "testFullMCSkim_out_12events.root")
            .setDefault('isData', False)
            .setDefault('globalTag', "130X_mcRun3_2023_realistic_v14")
            .setDefault('maxEvents', 12)
            .setDefault('dumpPython', True)
            .setDefault('metFiltersProcess', 'PAT')
            .setDefault('useHLTFilter', False)
            .setDefault('jsonFilterFile', "")  # no filter in MC
            .setDefault('withPATCollections', False)
            .setDefault('numThreads', 1)
    ).parseArguments()
else:
    # -- running on grid node -> "production" config
    options = (
        dijetSkim_131X_Run2023_Summer23MiniAODv4.register_options(KarmaOptions())
            .setDefault('inputFiles', [__FILE_NAMES__])
            .setDefault('outputFile', "output.root")
            .setDefault('isData', __IS_DATA__)
            .setDefault('globalTag', "__GLOBALTAG__")
            .setDefault('maxEvents', -1)
            .setDefault('dumpPython', False)
            .setDefault('metFiltersProcess', 'PAT')
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

#process.enable_verbose_logging()  # for testing

# configure the process
dijetSkim_131X_Run2023_Summer23MiniAODv4.configure(process, options)

# dump expanded cmsRun configuration
if options.dumpPython:
    process.dump_python('.'.join(options.outputFile.split('.')[:-1]) + '_dump.py', overwrite=True)

# print out configuration before running
process.print_configuration()
