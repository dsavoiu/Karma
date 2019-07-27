from __future__ import print_function

import abc
import argparse
import datetime
import hashlib
import time
import numpy as np
import os
import re
import sys

from contextlib import contextmanager
from tqdm import tqdm

__all__ = ["PalisadeCLI"]


class PalisadeCLI(object):

    class _PalisadeCLIHelpAction(argparse._HelpAction):
        '''custom help action: display help for parsers and subparsers at the same time'''

        @staticmethod
        def _fill_choices(parser, namespace):
            """change parser actions' `choices` and `help` attributes depending on context"""
            _is_incomplete = True

            # check in we are in the correct subparser (i.e. 'task')
            if not hasattr(namespace, 'ANALYSIS'):
                return _is_incomplete

            import pkgutil
            import Karma.PostProcessing.Palisade.cfg as cfg_module

            # retrieve built-in analysis configuration modules for Palisade
            _available_analysis_configs = {
                _name : _importer
                for _importer, _name, _ in pkgutil.iter_modules(cfg_module.__path__)
            }

            # retrieve a list of external configuration modules for Palisade
            _external_path_list = (os.getenv('PALISADE_CONFIGPATH') or "").split(':')
            _available_analysis_configs.update({
                _name: _importer
                for _importer, _name, _ in pkgutil.iter_modules(_external_path_list)
            })

            if namespace.TASK is None:
                if namespace.ANALYSIS is None or namespace.ANALYSIS not in sorted(_available_analysis_configs.keys()):
                    # populate ANALYSIS choices
                    for _a in parser._actions:
                        if _a.dest == 'ANALYSIS':
                            _a.choices = sorted(_available_analysis_configs.keys())
                            _a.help += " Choices: {%(choices)s}"
                            break
                else:
                    if namespace.ANALYSIS not in sorted(_available_analysis_configs.keys()):
                        return _is_incomplete

                    # retrieve tasks for analysis
                    _available_tasks = {
                        _name : _importer.find_module(_name).load_module(_name)
                        for _importer, _name, _ in pkgutil.iter_modules(_available_analysis_configs[namespace.ANALYSIS].find_module(namespace.ANALYSIS).load_module(namespace.ANALYSIS).tasks.__path__)
                    }

                    for _a in parser._actions:
                        if _a.dest == 'TASK':
                            _a.choices = sorted(_available_tasks.keys())
                            _a.help += " Choices: {%(choices)s}"
                        elif _a.dest == 'ANALYSIS':
                            _a.help += " Chosen: '{}'".format(namespace.ANALYSIS)
            else:
                for _a in parser._actions:
                    if _a.dest == 'TASK':
                        _a.help += " Chosen: '{}'".format(namespace.TASK)
                    elif _a.dest == 'ANALYSIS':
                        _a.help += " Chosen: '{}'".format(namespace.ANALYSIS)
                _is_incomplete = False

        def __call__(self, parser, namespace, values, option_string=None):

            # complete help output using partial information in namespace
            _is_incomplete = self._fill_choices(parser, namespace)

            # don't exit if 'ANALYSIS' or 'TASK' are both specified
            if _is_incomplete:
                # print top parser help
                parser.print_help()
                parser.exit()


    def __init__(self):
        # retrieve runner arguments and analysis config
        self._args, self._task_module = self._get_cli_args_and_task()

    def _get_cli_args_and_task(self):
        '''parse CLI arguments'''
        import pkgutil
        import sys

        import Karma.PostProcessing.Palisade.cfg as cfg_module

        # retrieve available analysis configuration modules for Palisade
        _available_analysis_configs = {
            _name : _importer
            for _importer, _name, _ in pkgutil.iter_modules(cfg_module.__path__)
        }

        # retrieve a list of external configuration modules for Palisade
        _external_path_list = (os.getenv('PALISADE_CONFIGPATH') or "").split(':')
        _available_analysis_configs.update({
            _name: _importer
            for _importer, _name, _ in pkgutil.iter_modules(_external_path_list)
        })

        # -- pre-parser: read only the first positional arguments (=subcommands)
        _pre_parser = argparse.ArgumentParser(add_help=False)
        _pre_parser.add_argument('-h', '--help', action=self.__class__._PalisadeCLIHelpAction, help="Display help and exit")

        _subparsers = _pre_parser.add_subparsers(help='Operation to perform. Available: {%(choices)s}', dest='subparser_name', metavar='SUBCOMMAND')
        #_subparsers.required = True

        _pre_parsers = {}

        # subcommand 'task' for executing pre-defined tasks
        _pre_parsers['task'] = _subparsers.add_parser('task', help='Perform a pre-defined task', add_help=False)
        _pre_parsers['task'].add_argument('-h', '--help', action=self.__class__._PalisadeCLIHelpAction, help="Display help and exit")
        _pre_parsers['task'].add_argument(
            'ANALYSIS', metavar='ANALYSIS',
            help="the analysis to which the Palisade task belongs.",
            type=str,
            choices=sorted(_available_analysis_configs.keys())
        )
        _task_action = _pre_parsers['task'].add_argument(
            'TASK', metavar='TASK',
            help="the Palisade task to run.",
            type=str,
            nargs='?',
            default=None
        )

        # subcommand 'task' for executing pre-defined tasks
        _pre_parsers['config'] = _subparsers.add_parser('config', help='Use a Python file as configuration', add_help=False)
        _pre_parsers['config'].add_argument(
            'FILE_NAME',
            help="path to a Python file to use as Palisade configuration",
            type=str
        )

        _pre_args = _pre_parser.parse_known_args()[0]

        # -- find task/file based on _pre_args

        if _pre_args.subparser_name == 'config':
            raise NotImplementedError("Using config files has not been implemented yet...")
        elif _pre_args.subparser_name == 'task':

            # -- check for analysis
            if _pre_args.ANALYSIS not in _available_analysis_configs:
                _pre_parsers['task'].print_help()
                raise ValueError("Unknown analysis '{}'!".format(_pre_args.ANALYSIS))

            # check if 'tasks' submodule exists
            if not hasattr(_available_analysis_configs[_pre_args.ANALYSIS].find_module(_pre_args.ANALYSIS).load_module(_pre_args.ANALYSIS), 'tasks'):
                raise ValueError("Analysis '{}' has no 'tasks' submodule (looked in "
                                 "{})".format(_pre_args.ANALYSIS,
                                              _available_analysis_configs[_pre_args.ANALYSIS].find_module(_pre_args.ANALYSIS).load_module(_pre_args.ANALYSIS).__path__))

            # retrieve tasks for analysis
            _available_tasks = {
                _name : _importer.find_module(_name).load_module(_name)
                for _importer, _name, _ in pkgutil.iter_modules(_available_analysis_configs[_pre_args.ANALYSIS].find_module(_pre_args.ANALYSIS).load_module(_pre_args.ANALYSIS).tasks.__path__)
            }

            _task_action.choices = sorted(_available_tasks.keys())
            _task_action.help += " Choices: {%(choices)s}"

            # check for task
            if _pre_args.TASK is None:
                _pre_parser.parse_known_args()
                _pre_parsers['task'].print_help()
                _pre_parsers['task'].exit()
            elif _pre_args.TASK not in _available_tasks:
                _pre_parsers['task'].print_help()
                raise ValueError("Task '{}' not found for analysis '{}'. "
                                 "Available: {}".format(
                                    _pre_args.TASK, _pre_args.ANALYSIS,
                                    sorted(_available_tasks.keys())))

            _task_module = _available_tasks[_pre_args.TASK]

            for _mandatory_func in ('cli', 'run'):
                if not hasattr(_task_module, _mandatory_func):
                    raise ValueError("Task '{}' does not define mandatory function '{}' (looked in "
                                     "{})".format(_pre_args.TASK, _mandatory_func,
                                                  _task_module.__file__))

            # new parser for task-specific CLI arguments
            _task_cli_parser = argparse.ArgumentParser()
            _task_cli_parser.add_argument('-o', '--output-dir', help="Directory in which to place the task result.")

            # task-specific parser configuration
            _task_module.cli(_task_cli_parser)

            # ignore "global" arguments
            _task_cli_args = _task_cli_parser.parse_args(sys.argv[4:])

            return _task_cli_args, _task_module
        else:
            # no subcommand specified, presumably called for help only
            _pre_parser.print_help()
            _pre_parser.exit()

    # -- public API

    def run(self):

        if self._task_module is None:
            raise NotImplemented
        else:
            # run the task
            self._task_module.run(self._args)
