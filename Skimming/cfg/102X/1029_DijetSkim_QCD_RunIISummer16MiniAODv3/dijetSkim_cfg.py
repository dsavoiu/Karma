import math
import os
import sys

import FWCore.ParameterSet.Config as cms

from Karma.Skimming.Configuration.MiniAOD import dijetSkim_94X_Run2016_17Jul2018
from Karma.Common.Tools import KarmaOptions, KarmaProcess


# set up and parse command-line options
if not os.getenv("GC_VERSION"):
    # -- *not* running in grid -> simple test
    options = (
        dijetSkim_94X_Run2016_17Jul2018.register_options(KarmaOptions())
            #.setDefault('inputFiles', "file:///storage/9/dsavoiu/test_miniAOD/test_QCD_Pt_600to800_RunIISummer16MiniAOVv3_MINIAOD_10events.root")
            .setDefault('inputFiles', "root://xrootd-cms.infn.it//store/mc/RunIISummer16MiniAODv3/QCD_Pt_15to30_TuneCUETP8M1_13TeV_pythia8/MINIAODSIM/PUMoriond17_94X_mcRun2_asymptotic_v3-v2/110000/7EEC82AC-41DF-E811-899D-0CC47AF973C2.root")
            .setDefault('outputFile', "testFullMCSkim_out_12events.root")
            .setDefault('isData', False)
            .setDefault('globalTag', "94X_mcRun2_asymptotic_v3")
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
        dijetSkim_94X_Run2016_17Jul2018.register_options(KarmaOptions())
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
dijetSkim_94X_Run2016_17Jul2018.configure(process, options)

# dump expanded cmsRun configuration
if options.dumpPython:
    process.dump_python('.'.join(options.outputFile.split('.')[:-1]) + '_dump.py', overwrite=True)

# print out configuration before running
process.print_configuration()
