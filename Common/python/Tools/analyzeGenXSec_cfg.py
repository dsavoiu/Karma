import os
import subprocess

import FWCore.ParameterSet.Config as cms

from Karma.Common.Tools import KarmaOptions


# -- get command-line options
options = (KarmaOptions()
    .register('sampleName',
          type_=str,
          default=None,
          description="DAS name of MC dataset (mutually exclusive with `inputFiles`).")
    .register('maxFiles',
          type_=int,
          default=0,
          description="Number of files from dataset to use. To process all files, use '0' (default).")
    .setDefault('isData', False)
).parseArguments()

# get list of dataset files
if options.sampleName is not None:
    assert not options.inputFiles, "Cannot specify both 'inputFiles' and 'sampleName'!"

    print("[INFO] 'sampleName' provided. Looking up sample files in DAS...")
    _query_command = "dasgoclient -query 'file dataset={sample_name}'".format(
        sample_name=options.sampleName
    )

    out, _ = subprocess.Popen(
        _query_command,
        shell=True,
        stdout=subprocess.PIPE,
    ).communicate()
 
    
    _input_files = ['root://xrootd-cms.infn.it/' + _path for _path in out.split()]
    assert _input_files, "No files found for dataset: {}!".format(options.sampleName)
    _n_found_files = len(_input_files)

    if options.maxFiles > 0:
        _input_files = _input_files[:min(options.maxFiles, len(_input_files))]

    print("[INFO] Using {}/{} files:".format(len(_input_files), _n_found_files))
    options.inputFiles = _input_files

    for _file in options.inputFiles:
        print("[INFO]   - {}".format(_file))

# make sure input files are provided
else:
    assert options.inputFiles, "No `inputFiles` provided!"

# set up CMSSW process
process = cms.Process('GENXSECANALYZER')

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.load('Configuration.StandardSequences.Generator_cff')
process.load('IOMC.EventVertexGenerators.VtxSmearedRealistic8TeVCollision_cfi')
process.load('GeneratorInterface.Core.genFilterSummary_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
# TODO: are they all needed??

# set global tag
process.GlobalTag.globaltag = cms.string(options.globalTag)

# handle max events
process.maxEvents = cms.untracked.PSet(
    input=cms.untracked.int32(options.maxEvents)
)

# configure message logging
process.load('FWCore.MessageService.MessageLogger_cfi')
process.MessageLogger = cms.Service("MessageLogger",
    categories = cms.untracked.vstring('FwkReport', 'JetPtMismatch', 'MissingJetConstituent', 'GenXSecAnalyzer', 'logFileAction'),
    destinations = cms.untracked.vstring('cerr', 'xsec'),
    cerr = cms.untracked.PSet(
            threshold = cms.untracked.string('WARNING'),
            JetPtMismatch = cms.untracked.PSet(limit = cms.untracked.int32(0)),
            MissingJetConstituent = cms.untracked.PSet(limit = cms.untracked.int32(0)),
            FwkReport = cms.untracked.PSet(reportEvery = cms.untracked.int32(1000)),
    ),
    # dump XSec to text file
    xsec = cms.untracked.PSet(
        threshold = cms.untracked.string('WARNING'),  # only report this severity or worse
        default	= cms.untracked.PSet(limit=cms.untracked.int32(0)),  # block all meassages
        GenXSecAnalyzer = cms.untracked.PSet(limit=cms.untracked.int32(1000000)), # except from GenXSecAnalyzer
        logFileAction = cms.untracked.PSet(limit=cms.untracked.int32(0)),  # block!
        filename = cms.untracked.string(options.outputFile),
    ),
)

# configure data source
process.source = cms.Source("PoolSource",
  fileNames = cms.untracked.vstring(
    options.inputFiles
  )
)

process.analyzer = cms.EDAnalyzer("GenXSecAnalyzer")

# Path and EndPath definitions
process.p = cms.Path(process.analyzer)

# Schedule definition
process.schedule = cms.Schedule(process.p)
