#
# dijetPrelude
# ------------
#
#   This file should be included first in every top-level configuration
#   file. It is best included in the top-level namespace, i.e.:
#
#       from DijetAnalysis.Core.dijetPrelude_cff import *

import math
import os
import sys

import FWCore.ParameterSet.Config as cms


#################
# Options setup #
#################
#
# Define options for 'cmsRun' here. These can be accessed later in the
# script using 'options.<optionName>'
#
# Note: Some options are pre-defined by CMSSW. These include:
# ----
#       inputFiles      :  list of input filenames [default: <empty list>]
#       outputFile      :  name of the output file [default: "output.root"]
#       maxEvents       :  maximum number of events to process [default: -1 (=no limit)]

from DijetAnalysis.Core.optionsInterface import options, register_option

# specify some custom command-line arguments
register_option('isData',
                default=True,
                type_=bool,
                description="True if sample is data, False if Monte Carlo (default: True)")
register_option('globalTag',
                default='80X_dataRun2_2016LegacyRepro_v4',
                type_=str,
                description='Global tag')
register_option('reportEvery',
                default=1000,
                type_=int,
                description=("Print a message after each <reportEvery> "
                             "events processed (default: 1000)"))
register_option('edmOut',
                default='',
                type_=str,
                description=('(for testing only) write edm file (e.g miniAOD) to '
                             'this path (if empty/unset, no edm file is written).'))
register_option('dumpPython',
                default=False,
                type_=bool,
                description=('(for testing only) dump the full cmsRun Python config before '
                             'running.'))
register_option('configureOnly',
                default=False,
                type_=bool,
                description=('(for testing only) configure, but do not run.'))
register_option('weightForStitching',
                default=1.0,
                type_=float,
                description=('weight to use when stitching together MC samples'))


# parse the command-line arguments
options.parseArguments()


################
# Remote setup #
################

## if submitted with grid-control, assume this is a remote skimming job
## -> override the global tag and data/MC flag options
#if os.getenv("GC_VERSION"):
#    options.globalTag = "__GLOBALTAG__"
#    options.isData = __IS_DATA__
#    options.edmOut = options.outputFile  # FIXME #.split('.')[:-1] + "_edmOut.root"
#    options.dumpPythonAndExit = False
#    options.reportEvery = int(max(1, 10**(round(math.log(__MAX_EVENTS__)/math.log(10))-1)))
#
#    # temporary; gc later sets process.source.fileNames directly!
#    options.inputFiles = [__FILE_NAMES__]



########################
# Create CMSSW Process #
########################
def createProcess(process_name, num_threads=1):
    process = cms.Process(process_name)

    # CMSSW producers and analyzers will be added to the path
    process.path = cms.Path()

    # CMSSW output modules will be added to the endpath
    process.endpath = cms.EndPath()

    # limit the number of processed events (or set to -1 for no limit)
    process.maxEvents = cms.untracked.PSet(
        input=cms.untracked.int32(options.maxEvents)
    )

    # configure process with options
    process.options = cms.untracked.PSet(
        wantSummary=cms.untracked.bool(True),
        allowUnscheduled=cms.untracked.bool(True),  # some modules need the unscheduled mode!
        emptyRunLumiMode=cms.untracked.string('doNotHandleEmptyRunsAndLumis'),
        #SkipEvent=cms.untracked.vstring('ProductNotFound')   # only for debugging
        numberOfThreads=cms.untracked.uint32(num_threads),
        numberOfStreams=cms.untracked.uint32(num_threads),
        #Rethrow=cms.untracked.vstring('StdException'),
    )

    # set the input files
    process.source = cms.Source("PoolSource",
        fileNames=cms.untracked.vstring(options.inputFiles)
    )

    # -- print process configuration
    print "\n----- CMSSW configuration -----"
    print "input:          ", (process.source.fileNames[0] if len(process.source.fileNames) else ""), ("... (%d files)" % len(process.source.fileNames) if len(process.source.fileNames) > 1 else "")
    print "file type:      ", "miniAOD"
    print "data:           ", options.isData
    print "output:         ", options.outputFile
    print "global tag:     ", options.globalTag
    print "max events:     ", (str(process.maxEvents.input)[20:-1])
    print "cmssw version:  ", os.environ["CMSSW_VERSION"]
    print "---------------------------------\n"



    #################
    # CMSSW modules #
    #################

    # -- CMSSW message logger
    process.load("FWCore.MessageLogger.MessageLogger_cfi")
    process.MessageLogger.cerr.FwkReport.reportEvery = options.reportEvery

    # ~ process.MessageLogger.default = cms.untracked.PSet(
        # ~ ERROR=cms.untracked.PSet(limit=cms.untracked.int32(5)),
    # ~ )

    # -- CMSSW geometry and detector conditions
    # (These are needed for some PAT tuple production steps)
    process.load("Configuration.Geometry.GeometryRecoDB_cff")  # new phase-1 geometry
    process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
    process.load("Configuration.StandardSequences.MagneticField_cff")
    process.GlobalTag.globaltag = cms.string(options.globalTag)

    return process


def finalizeAndRun(process, outputCommands=[]):

    # write out original collections to a slimmed miniAOD file
    if options.edmOut and outputCommands:
        process.edmOut = cms.OutputModule("PoolOutputModule",
            fileName = cms.untracked.string(options.edmOut),
            outputCommands = cms.untracked.vstring(
                outputCommands
            )
        )
        process.endpath *= process.edmOut

    # final information:
    print
    print "[dijetPrelude] CMSSW modules in 'path':"
    for p in str(process.path).split('+'):
        print "  %s" % p
    print
    print "[dijetPrelude] CMSSW modules in 'endpath':"
    for p in str(process.endpath).split('+'):
        print "  %s" % p
    print

    print "[dijetPrelude] Configuring done!"

    # for debugging: dump entire cmsRun python configuration
    if options.dumpPython:
        print "[dijetPrelude] Dumping Python configuration..."
        with open('.'.join(options.outputFile.split('.')[:-1]) + '_dump.py', 'w') as f:
            f.write(process.dumpPython())

    if options.configureOnly:
        print "[dijetPrelude] Flag 'configureOnly' set: Exiting..."
        sys.exit(1)


def enableVerboseLogging(process):
    
    # create a MessageLogger service instance, if none exists
    if not hasattr(process, 'MessageLogger'):
        process.load("FWCore.MessageLogger.MessageLogger_cfi")

    # -- route more detailed output to log files
    process.MessageLogger.destinations.extend(cms.untracked.vstring(
        'detailedInfo', 'critical', 'out',
    ))
    process.MessageLogger.categories.extend(cms.untracked.vstring(
        'EventProducer',
    ))
    process.MessageLogger.out = cms.untracked.PSet(
        threshold = cms.untracked.string('WARNING'),
        FwkReport = cms.untracked.PSet(
            reportEvery = cms.untracked.int32(3),
        ),
    )
    process.MessageLogger.detailedInfo = cms.untracked.PSet(
        threshold = cms.untracked.string('INFO'),
        FwkReport = cms.untracked.PSet(
            reportEvery = cms.untracked.int32(1),
        ),
    )
    process.MessageLogger.critical = cms.untracked.PSet(
        threshold = cms.untracked.string('ERROR'),
    )
