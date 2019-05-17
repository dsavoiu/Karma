#
# karmaProcess
# ------------
#
#   Provide a `KarmaProcess` class that inherits from `cms.Process` and
#   adds some convenience functionality to the API. This class should
#   always be used for Karma skims instead of `cms.Process`.
#
#   This file should be included first in every top-level configuration
#   file. It is best included in the top-level namespace, i.e.:
#
#     from Karma.Common.Tools.karmaProcess_cfi import KarmaProcess
#
#     # create the process
#     process = KarmaProcess(...)
#
#     # then, use `process` like any normal `cms.Process`

import os

import FWCore.ParameterSet.Config as cms
import FWCore.PythonUtilities.LumiList as LumiList

from FWCore.ParameterSet.SequenceTypes import ExpandVisitor

__all__ = ['KarmaProcess']


class KarmaProcess(cms.Process):

    def __init__(self,
                 name, input_files, num_threads, max_events, global_tag,
                 edm_out=None, report_every=1000, *args, **kwargs):
        super(KarmaProcess, self).__init__(name, *args, **kwargs)

        # create the main path and an output EndPath
        self.outputPath = cms.EndPath()

        ## set explicit schedule?
        #self.schedule = cms.Schedule(self.mainPath, self.outputPath)

        # limit the number of processed events (or set to -1 for no limit)
        self.maxEvents = cms.untracked.PSet(
            input=cms.untracked.int32(max_events)
        )

        # configure process with options
        self.options = cms.untracked.PSet(
            wantSummary=cms.untracked.bool(True),
            allowUnscheduled=cms.untracked.bool(True),  # some modules need the unscheduled mode!
            emptyRunLumiMode=cms.untracked.string('doNotHandleEmptyRunsAndLumis'),
            #SkipEvent=cms.untracked.vstring('ProductNotFound')   # only for debugging
            numberOfThreads=cms.untracked.uint32(num_threads),
            numberOfStreams=cms.untracked.uint32(num_threads),
            #Rethrow=cms.untracked.vstring('StdException'),
        )

        # set the input files
        self.source = cms.Source("PoolSource",
            fileNames=cms.untracked.vstring(input_files)
        )

        # -- print process configuration
        print "\n----- Process configuration -----"
        print "input:          ", (self.source.fileNames[0] if len(self.source.fileNames) else ""), ("... (%d files)" % len(self.source.fileNames) if len(self.source.fileNames) > 1 else "")
        print "file type:      ", "miniAOD"
        print "global tag:     ", global_tag
        print "max events:     ", (str(self.maxEvents.input)[20:-1])
        print "cmssw version:  ", os.environ["CMSSW_VERSION"]
        print "---------------------------------\n"

        #################
        # CMSSW modules #
        #################

        # -- CMSSW message logger
        self.load("FWCore.MessageLogger.MessageLogger_cfi")
        self.MessageLogger.cerr.FwkReport.reportEvery = report_every

        # ~ self.MessageLogger.default = cms.untracked.PSet(
            # ~ ERROR=cms.untracked.PSet(limit=cms.untracked.int32(5)),
        # ~ )

        # -- CMSSW geometry and detector conditions
        # (These are needed for some PAT tuple production steps)
        self.load("Configuration.Geometry.GeometryRecoDB_cff")  # new phase-1 geometry
        self.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
        self.load("Configuration.StandardSequences.MagneticField_cff")
        self.GlobalTag.globaltag = cms.string(global_tag)

        # write out original collections to a slimmed miniAOD file
        if edm_out:
            self.edmOut = cms.OutputModule("PoolOutputModule",
                fileName = cms.untracked.string(edm_out),
                outputCommands = cms.untracked.vstring()
            )
            self.outputPath *= self.edmOut

    @staticmethod
    def _print_path(path_or_self, path_name):
        '''convenience. print the modules contained in a CMSSW path'''

        if isinstance(path_or_self, KarmaProcess):
            path = path_or_self.paths[path_name]
        else:
            path = path_or_self

        _v = ExpandVisitor(type(path))
        path.visit(_v)
        print "\n[karmaProcess] CMSSW modules in {} '{}':".format(type(path).__name__, path_name)
        for _module in _v.l:
            print('\t{}'.format(_module))
        if _v.taskLeaves:
            print "\n[karmaProcess] CMSSW modules on tasks associated to {} '{}':".format(type(path).__name__, path_name)
            for _task_module in sorted([str(_t) for _t in _v.taskLeaves]):
                print('\t{}'.format(_task_module))

    # -- public API

    def enable_verbose_logging(self):
        '''Increade verbosity of error messages in output.'''
        # create a MessageLogger service instance, if none exists
        if not hasattr(self, 'MessageLogger'):
            self.load("FWCore.MessageLogger.MessageLogger_cfi")

        # -- route more detailed output to log files
        self.MessageLogger.destinations.extend(cms.untracked.vstring(
            'detailedInfo', 'critical', 'out',
        ))
        self.MessageLogger.categories.extend(cms.untracked.vstring(
            'EventProducer',
        ))
        self.MessageLogger.out = cms.untracked.PSet(
            threshold = cms.untracked.string('WARNING'),
            FwkReport = cms.untracked.PSet(
                reportEvery = cms.untracked.int32(3),
            ),
        )
        self.MessageLogger.detailedInfo = cms.untracked.PSet(
            threshold = cms.untracked.string('INFO'),
            FwkReport = cms.untracked.PSet(
                reportEvery = cms.untracked.int32(1),
            ),
        )
        self.MessageLogger.critical = cms.untracked.PSet(
            threshold = cms.untracked.string('ERROR'),
        )

    def enable_json_lumi_filter(self, file_path):
        '''Only process certified runs and luminosity blocks (data only)'''

        # add filter to accept only the luminosity blocks is the certification JSON
        self.source.lumisToProcess = LumiList.LumiList(
            filename = os.path.realpath(file_path)
        ).getVLuminosityBlockRange()

    def enable_selective_writeout(self, *paths):
        if not hasattr(self, 'edmOut'):
            raise ValueError("Cannot enable selective writeout: no EDM output requested in the first place!")

        _declared_paths = set(self.paths)
        _unknown_paths = set(paths) - _declared_paths
        if _unknown_paths:
            raise ValueError("Cannot enable selective writeout: unknown paths {}".format(list(_unknown_paths)))

        if hasattr(self.edmOut, 'SelectEvents') and self.edmOut.SelectEvents:
            print(
                "[karmaProcess] WARNING: selective writeout requested for paths {}, "
                "but it has already been enabled for paths {}!".format(
                    paths,
                    self.edmOut.SelectEvents
                )
            )

        # enable selective writeout based on path decisions
        self.edmOut.SelectEvents = cms.untracked.PSet(
            SelectEvents = cms.vstring(paths)
        )

    def add_module(self, module_name, module, write_out=None, overwrite=False, on_path=None):
        '''Convenience function for adding a module to the process.'''

        # check if not added already
        if hasattr(self, module_name) and not overwrite:
            raise ValueError("Cannot add module '{}': already exists!".format(module_name))

        # register module in the process
        setattr(self, module_name, module)

        # add module to path, if requested
        if on_path is not None:
            if on_path not in self.paths:
                raise ValueError("Cannot add module '{}' to path '{}': path does not exist!".format(module_name, on_path))

            _path = getattr(self, on_path)
            _path *= getattr(self, module_name)

        # determine writeout behavior automatically on 'None'
        if write_out is None:
            write_out = hasattr(self, 'edmOut')

        # enable/disable writing out the collection in OutputModule
        if write_out:
            self.add_output_commands("keep *_{}_*_{}".format(module_name, self.name_()))

    def add_path(self, name, path=None):
        '''Add a Path to the process. Checks if it exists. Returns the added path'''
        if hasattr(self, name):
            raise ValueError("Cannot add path '{}': name is reserved or already exists! Aborting.".format(name))

        if path is None:
            setattr(self, name, cms.Path())
            # default: add empty path
        else:
            # add existing path
            if not isinstance(path, cms.Path):
                raise ValueError("Cannot add path '{}': expected type 'cms.Path' but got '{}'! Aborting.".format(name, type(path)))

            setattr(self, name, path)

        return getattr(self, name)

    def add_output_commands(self, *commands):
        '''Add an output command to the EDM output module on the endpath.'''
        try:
            _output_module = self.edmOut
        except AttributeError as _err:
            raise ValueError("Cannot add output command: no EDM output requested!")
        else:
            _output_module.outputCommands.extend(commands)

    def print_configuration(self):

        # paths
        print "\n[karmaProcess] CMSSW Paths configured: {}".format(', '.join(list(self.paths)))
        for _path_name, _path in self.paths.items():
            self._print_path(_path, _path_name)

        # endpaths
        print "\n[karmaProcess] CMSSW EndPaths configured: {}".format(', '.join(list(self.endpaths)))
        for _endpath_name, _endpath in self.endpaths.items():
            self._print_path(_endpath, _endpath_name)

    def dump_python(self, filename, overwrite=False):
        '''for debugging: dump entire cmsRun python configuration'''

        print "[karmaProcess] Dumping Python configuration to file '{}'...".format(filename)
        if os.path.exists(filename) and not overwrite:
            raise IOError("Cannot dump Python: file '{}' exists and 'overwrite' not given!".format(filename))

        with open(filename, 'w') as f:
            f.write(self.dumpPython())
