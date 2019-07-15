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
import yaml
#import ROOT

from contextlib import contextmanager
from tqdm import tqdm

__all__ = ["LumberjackInterfaceBase", "LumberjackCLI"]


def product_dict(**kwargs):
    """Cartesian product of iterables in dictionary"""
    import itertools
    _keys = kwargs.keys()
    for instance in itertools.product(*kwargs.values()):
        yield dict(zip(_keys, instance))

def group_by(iterable, n):
    '''Return list of iterables of elements of `iterable`, grouped in batches of at most `n`'''
    _l = len(iterable)
    _n_groups = _l//n + (_l%n>0)
    _grouped_iterable = [iterable[_i*n:min(_l,(_i+1)*n)] for _i in range(_n_groups)]
    return _grouped_iterable


class StreamDup:
    def __init__(self, streams):
        self._streams = streams

    def write(self, *args, **kwargs):
        for _s in self._streams:
            _s.write(*args, **kwargs)

    def flush(self):
        for _s in self._streams:
            _s.flush()

    def close(self):
        for _s in self._streams:
            _s.close()


@contextmanager
def log_stdout_to_file(filename):
    if filename is None:
        yield
    else:
        _old_stdout = sys.stdout
        with open(filename, 'w') as _log:
            sys.stdout = StreamDup([sys.stdout, _log])
            yield
            sys.stdout.flush()
        sys.stdout = _old_stdout


class LumberjackInterfaceBase(object):

    RE_SPLITTING_KEY_SPEC = re.compile(r"([^[]]*)(\[(.*)\])?")

    def __init__(self, **kwargs):
        # retrieve runner arguments and analysis config
        self._args, self._config = self._get_args_config(**kwargs)

    @abc.abstractmethod
    def _get_args_config(self, **kwargs):
        '''parse CLI arguments and retrieve analysis config'''
        raise NotImplementedError  # implement in derived classes

    def _prepare_bare_data_frame(self):

        import ROOT  # do this here to avoid ROOT overriding standard Python behavior

        # determine correct ROOT DataFrame class
        try:
            ROOT_DF_CLASS = ROOT.ROOT.RDataFrame
        except AttributeError:
            ROOT_DF_CLASS = ROOT.ROOT.Experimental.TDataFrame

        ROOT_MACROS = self._config.ROOT_MACROS

        # -- enable multithreading
        if int(self._args.jobs) > 1:
            print("[INFO] Enabling multithreading with {} threads...".format(self._args.jobs))
            ROOT.ROOT.EnableImplicitMT(int(self._args.jobs))

        # -- set up data frame
        print("[INFO] Setting up data frame...")
        print("[INFO] Sample file: {}".format(self._args.input_file))

        # exit if input file does not exist
        if not os.path.exists(self._args.input_file):
            print("[ERROR] Input file does not exist: '{}'".format(self._args.input_file))
            exit(1)

        # exit if tree does not exist in file
        _f = ROOT.TFile(self._args.input_file, "READ")
        _tree = _f.Get(self._args.tree)
        if not isinstance(_tree, ROOT.TTree):
            print("[ERROR] Input file does not contain TTree '{}'".format(self._args.input_file))
            exit(1)
        self._df_size = _tree.GetEntries()
        _f.Close()

        print("[INFO] Sample type: {}".format(self._args.input_type))
        self._df_bare = ROOT_DF_CLASS(self._args.tree, self._args.input_file)

        print("[INFO] Defining ROOT macros...")

        ROOT.gInterpreter.Declare(ROOT_MACROS)

    def _prepare_data_frame(self):

        from Karma.PostProcessing.Lumberjack import apply_defines, apply_filters, define_quantities

        QUANTITIES = self._config.QUANTITIES
        DEFINES = self._config.DEFINES
        SELECTIONS = self._config.SELECTIONS

        # -- limit the number of processed events
        if self._args.num_events >= 0:
            print("[INFO] Limiting number of processed events to: ".format(self._args.num_events))
            self._df_bare = self._df_bare.Range(0, int(self._args.num_events))
            self._df_size = min(self._df_size, int(self._args.num_events))
            self._df_count_increment = max(self._df_size//100, 10)

        # -- set up event counter (for progress reporting)
        self._df_count = self._df_bare.Count()
        self._df_count_increment = 100000

        if self._args.progress:
            self._progress = tqdm(
                unit=" events",
                unit_scale=False,
                dynamic_ncols=True,
                desc="Event loop progress",
                total=self._df_size,
            )
            def _progress_callback(count):
                self._progress.update(self._df_count_increment)

            _func_basename = "my_callback_py_f"
            _func_idstring = hashlib.md5(hex(id(_progress_callback))).hexdigest()  # unique ID
            _func_fullname = _func_basename + '_' + _func_idstring
            _func_slotcallback_fullname = _func_basename + '_slot_' + _func_idstring

            import ROOT

            # black magic to obtain pointer to Python function in ROOT's interpreter
            ROOT.gInterpreter.ProcessLine("#include <Python.h>")
            ROOT.gInterpreter.ProcessLine("long long "+_func_fullname+"_addr = " + hex(id(_progress_callback)) + ";")
            ROOT.gInterpreter.ProcessLine("PyObject* "+_func_fullname+" = reinterpret_cast<PyObject*>("+_func_fullname+"_addr);")
            ROOT.gInterpreter.ProcessLine("Py_INCREF("+_func_fullname+");")  # prevent garbage collection

            # define a thread-safe std::function for the progress callback and register it
            ROOT.gInterpreter.ProcessLine("std::mutex partialResultMutex_"+_func_idstring+";")
            ROOT.gInterpreter.ProcessLine(
                "std::function<void(unsigned int, ULong64_t&)> "+_func_slotcallback_fullname+" = [](unsigned int /*slot*/, ULong64_t& count) { "
                    "std::lock_guard<std::mutex> lock(partialResultMutex_"+_func_idstring+"); "
                    "PyEval_CallObject("+_func_fullname+", Py_BuildValue(\"(i)\", count)); "
                "};"
            )
            self._df_count.OnPartialResultSlot(self._df_count_increment, getattr(ROOT, _func_slotcallback_fullname))

        # -- apply basic analysis selection

        self._df = self._df_bare  #start from "bare" DataFrame (without defines)

        print("[INFO] Defining quantities...")
        # "main" quantities (with binning)
        _quantities =  dict(QUANTITIES['global'], **QUANTITIES.get(self._args.input_type, {}))
        self._df = define_quantities(self._df, _quantities)

        # other quantities (only given as expressions, no binning)
        self._df = apply_defines(self._df, DEFINES['global'])
        if self._args.input_type in DEFINES:
            self._df = apply_defines(self._df, DEFINES[self._args.input_type])

        if self._args.selections is not None:
            for _sel in self._args.selections:
                if _sel not in SELECTIONS:
                    print("[ERROR] Applying global selection '{}'...".format(_sel))
                    raise ValueError("Unknown selection '{}'".format(_sel))
                print("[INFO] Applying global selection '{}': {}".format(_sel, ' && '.join(SELECTIONS[_sel])))
                self._df = apply_filters(self._df, SELECTIONS[_sel])

    def _cleanup_data_frame(self):
        pass  # what to do here?


    def _expand_subtasks(self, task_configs):
        '''replace single task with subtasks, if slicing a particular splitting is enabled'''
        SPLITTINGS = self._config.SPLITTINGS

        _expansions_left = True
        while _expansions_left:
            _expansions_left = False
            _tasks_with_subtasks = []
            for _task_name, _task_spec in task_configs:
                for _i_splitting_key, _splitting_key in enumerate(_task_spec['splittings']):
                    if '@' in _splitting_key:
                        _splitting_key, _n_splittings_per_subtask = _splitting_key.split('@', 1)
                        _n_splittings_per_subtask = int(_n_splittings_per_subtask)

                        # retrieve splittings for task
                        if _splitting_key not in SPLITTINGS:
                            raise KeyError("[ERROR] Cannot find splitting for key '{}'".format(_splitting_key))
                        _splitting_subkeys = SPLITTINGS[_splitting_key].keys()

                        # split into subtasks
                        _expansions_left = True  # flag need for another iteration
                        _splitting_subkey_groups = group_by(_splitting_subkeys, _n_splittings_per_subtask)
                        break

                if _expansions_left:
                    for _i_subtask, _splitting_subkey_group in enumerate(_splitting_subkey_groups):
                        _subtask_splitting_string = "{}[{}]".format(_splitting_key, ",".join(_splitting_subkey_group))
                        _new_splittings = _task_spec['splittings'][:]
                        # replace '@' syntax with '[]' syntax specifying subkeys explicitly
                        _new_splittings[_i_splitting_key] = _subtask_splitting_string

                        _subtask_filename = _task_spec['_filename'].split('.')
                        _subtask_filename[-2] += '_' + str(_i_subtask)
                        _subtask_filename = '.'.join(_subtask_filename)

                        _subtask_log_filename = _task_spec.get('_log_filename', None)
                        if _subtask_log_filename is not None:
                            _subtask_log_filename = _subtask_log_filename.split('.')
                            _subtask_log_filename[-2] += '_' + str(_i_subtask)
                            _subtask_log_filename = '.'.join(_subtask_log_filename)

                        _tasks_with_subtasks.append((
                            "{}_{}".format(_task_name, _i_subtask),
                            dict(_task_spec,
                                splittings=_new_splittings,
                                _filename=_subtask_filename,
                                _log_filename=_subtask_log_filename,
                            ),
                        ))
                else:
                    _tasks_with_subtasks.append((_task_name, _task_spec))

            task_configs = _tasks_with_subtasks

        return task_configs


    def _run_tasks(self, task_configs):

        from Karma.PostProcessing.Lumberjack import PostProcessor, Timer

        SPLITTINGS = self._config.SPLITTINGS

        task_configs = self._expand_subtasks(task_configs)

        # -- run all queued tasks
        for _task_name, _task_spec in task_configs:

            # skip task if output file exists
            if os.path.exists(_task_spec['_filename']) and not self._args.overwrite:
                print("[INFO] Task output file exists: '{}' and `--overwrite` not set. Skipping...".format(_task_spec['_filename']))
                continue
            # dump task configuration to yml
            if self._args.dump_yaml:
                _yaml_dump_filename = ".".join(_task_spec['_filename'].split('.')[:-1]) + "_configdump.yml"
                #_yaml_dump_filename = "{}_configdump.yml".format(self._args.output_file.split('.', 1)[0])
                with open(_yaml_dump_filename, 'w') as _f:
                    yaml.dump(_task_spec, _f, default_flow_style=False)

            with log_stdout_to_file(_task_spec['_log_filename']):
                print("[INFO] Running task '{}'...".format(_task_name))

                # apply defines, basic selection, etc.
                self._prepare_data_frame()

                _splittings_key_specs = _task_spec.get('splittings')

                _splitting_specs = {}
                _splittings_keys = []
                for _key_spec in _splittings_key_specs:
                    # support for slicing of individual splittings
                    # key can be '<name>' (no slicing) or '<name>[<splitting_value_1>,<splitting_value_2>,...]'
                    _key_spec_groups = re.match(self.RE_SPLITTING_KEY_SPEC, _key_spec).groups()
                    if _key_spec_groups[2] is None:
                        _key = _key_spec
                        # no slicing -> direct lookup
                        if _key not in SPLITTINGS:
                            raise KeyError("[ERROR] Cannot find splitting for key '{}'".format(_key))
                        _splitting_specs[_key] = SPLITTINGS[_key]
                    else:
                        # slicing -> lookup and slice
                        _key = _key_spec_groups[0]
                        if _key not in SPLITTINGS:
                            raise KeyError("[ERROR] Cannot find splitting for key '{}'".format(_key))

                        _subkeys = [_subkey.strip() for _subkey in _key_spec_groups[2].split(',')]
                        try:
                            _splitting_specs[_key] = {_subkey: SPLITTINGS[_key][_subkey] for _subkey in _subkeys}
                        except KeyError as e:
                            raise KeyError("[ERROR] Cannot find splitting for subkey '{}[{}]'".format(_key, e))

                    _splittings_keys.append(_key)  # store key w/o slicing syntax

                # create combined splitting specification out of the cross product
                # of specified keys
                _combined_splittings = {}
                for _splitting_combination in product_dict(**_splitting_specs):
                    _splitting_dict = {}
                    for _key in _splittings_keys:
                        _splitting_dict.update(SPLITTINGS[_key][_splitting_combination[_key]])
                    _splitting_name = "/".join([_key + ':' + _splitting_combination[_key] for _key in _splittings_keys])

                    _combined_splittings[_splitting_name] = _splitting_dict

                _hs = _task_spec.get('histograms', None)
                _ps = _task_spec.get('profiles', None)

                if _hs is None and _ps is None:
                    print("[ERROR] No `histograms` or `profiles` configured for task '{}': skipping...".format(_task_name))
                    continue


                if _hs:
                    print("[INFO] Requested histograms:")
                    for _h in _hs:
                        print("    - {}".format(_h))
                else:
                    print("[INFO] Requested histograms: <none>")

                if _ps:
                    print("[INFO] Requested profiles:")
                    for _p in _ps:
                        print("    - {}".format(_p))
                else:
                    print("[INFO] Requested profiles: <none>")

                print("[INFO] Setting up PostProcessor...")
                _pp = PostProcessor(
                    data_frame=self._df,
                    splitting_spec=_combined_splittings,
                    quantities=_task_spec['_quantities'],
                )

                _n_obj = 0
                if _hs is not None:
                    _pp.add_histograms(_hs)
                    _n_obj += len(_hs)
                if _ps is not None:
                    _pp.add_profiles(_ps)
                    _n_obj += len(_ps)

                _n_subdiv = np.prod([len(_splitting) for _splitting in _splitting_specs.values()])

                print("[INFO] Running Task '{}':".format(_task_name))
                print("    - splitting RDataFrame by keys: {}".format(
                    ", ".join(["{} ({} subdivisions)".format(_key, len(_splitting)) for _key, _splitting in _splitting_specs.iteritems()])
                ))
                print("        -> total number of subdivisions: {}\n".format(_n_subdiv))
                print("    - requested number of objects per subdivision: {}\n".format(_n_obj))
                print("    -> total number of objects: {}\n".format(_n_obj * _n_subdiv))
                print("    - output file: {}".format(_task_spec['_filename']))

                # run PostProcessor and time execution
                with Timer(_task_name) as _t:
                    if self._args.dry_run:
                        print("[INFO] `--dry-run` has been specified: not running task '{}'".format(_task_name))
                        time.sleep(0.1)
                    else:
                        _pp.run(output_file_path=_task_spec['_filename'])

                # print report
                if not self._args.dry_run:
                    print("[INFO] Processed a total of {} events.".format(self._df_count.GetValue()))
                _t.report()

                print("[INFO] Cleaning up after task '{}'...".format(_task_name))
                self._cleanup_data_frame()


    # -- subcommand methods

    def _subcommand_freestyle(self):

        from Karma.PostProcessing.Lumberjack import apply_defines, apply_filters, define_quantities, PostProcessor, Timer

        QUANTITIES = self._config.QUANTITIES

        # -- configure and queue freestyle task

        # exit if output filename exists
        if os.path.exists(self._args.output_file) and not self._args.overwrite:
            print("[INFO] Output file exists: '{}' and `--overwrite` not set. Exiting...".format(self._args.output_file))
            exit(1)

        # configure single 'Freestyle' task
        _task_spec = dict(
            _filename = self._args.output_file,
            _log_filename = "{}.log".format(self._args.output_file.split('.', 1)[0]) if self._args.log else None,
            _quantities =  dict(QUANTITIES['global'], **QUANTITIES.get(self._args.input_type, {})),
            splittings = self._args.SPLITTING_KEY,
            histograms = self._args.histograms,
            profiles = self._args.profiles,
        )
        _tasks = [("Freestyle", _task_spec)]

        self._prepare_bare_data_frame()
        self._run_tasks(_tasks)


    def _subcommand_task(self):

        QUANTITIES = self._config.QUANTITIES
        TASKS = self._config.TASKS

        # -- determine output filename suffix
        _suffix = self._args.output_file_suffix
        if _suffix is None:
            _suffix = "{}".format(datetime.datetime.now().strftime("%Y-%m-%d"))

        # -- configure and queue task(s)
        _tasks = []
        for _task_name in self._args.TASK_NAME:
            _task_spec = TASKS.get(_task_name, None)
            if _task_spec is None:
                raise ValueError("[ERROR] Unknown task '{}': expected one of {}".format(_task, set(TASKS.keys())))


            # add task to queue
            _task_spec['_filename'] = "{}_{}.root".format(_task_name, _suffix)
            _task_spec['_log_filename'] = "{}_{}.log".format(_task_name, _suffix) if self._args.log else None
            _task_spec['_quantities'] = dict(QUANTITIES['global'], **QUANTITIES.get(self._args.input_type, {}))
            _tasks.append((_task_name, _task_spec))

        if not _tasks:
            print("[INFO] No tasks in queue. Exiting...")
            exit(1)

        self._prepare_bare_data_frame()
        self._run_tasks(_tasks)


    # -- public API

    def run(self):

        if self._args.subparser_name == 'task':
            self._subcommand_task()

        elif self._args.subparser_name == 'freestyle':
            self._subcommand_freestyle()

        else:
            raise ValueError("Unknown operation '{}'! Exiting...".format(_args.subparser_name))


class LumberjackCLI(LumberjackInterfaceBase):

    class _LumberjackCLIHelpAction(argparse._HelpAction):
        '''custom help action: display help for parsers and subparsers at the same time'''

        def __call__(self, parser, namespace, values, option_string=None):

            # print top parser help
            parser.print_help()
            print

            # retrieve subcommand action
            _subcommand_actions = [
                action for action in parser._actions
                if action.dest == 'subparser_name'
            ]
            assert len(_subcommand_actions) == 1

            # print subcommands help
            for _subcommand_name, _subcommand_parser in _subcommand_actions[0].choices.items():
                _heading = "Subcommand '{}'".format(_subcommand_name)
                print(_heading)
                print('='*len(_heading))
                print
                print(_subcommand_parser.format_help())

            parser.exit()

    def __init__(self):
        super(LumberjackCLI, self).__init__()  # no kwargs

    def _get_args_config(self):
        '''parse CLI arguments and retrieve analysis config'''
        import importlib
        import pkgutil

        import Karma.PostProcessing.Lumberjack.cfg as cfg_module

        # retrieve a list of available configuration modules for Lumberjack
        _available_analysis_configs = [
            _name for _, _name, _ in pkgutil.iter_modules(cfg_module.__path__)
        ]

        # -- pre-parser: read only the '--analysis'/'-a' flag
        _pre_parser = argparse.ArgumentParser(
            add_help=False,  # turn off default help action
        )
        _pre_parser.add_argument(
            '-a', '--analysis', metavar='ANALYSIS_NAME', type=str,
            choices=_available_analysis_configs,
            nargs='?')

        _analysis_name = _pre_parser.parse_known_args()[0].analysis

        # -- main parser: read other flags and populate help based on content of '--analysis' flag

        _top_parser = argparse.ArgumentParser(
            description='Split an input TTree into subsamples and produce ROOT files containing TH1D, TH2D or TProfile objects for each subdivision.',
            add_help=False,  # turn off default help action
        )

        _required_args = _top_parser.add_argument_group('required arguments', '')
        _required_args.add_argument(
            '-a', '--analysis', metavar='ANALYSIS_NAME', type=str,
            help="Name of the analysis configuration to load (must have a configuration module under 'Lumberjack/cfg/ANALYSIS_NAME')",
            required=True,
            choices=_available_analysis_configs)
        _required_args.add_argument('-i', '--input-file', metavar='FILE', type=str, help='Input file', required=True)
        _required_args.add_argument('--selections', metavar='SELECTION', help='Specification of event selection cuts', nargs='+')

        _optional_args = _top_parser.add_argument_group('optional arguments', '')
        _optional_args.add_argument('-h', '--help', action=self.__class__._LumberjackCLIHelpAction, help="Display help and exit")
        _optional_args.add_argument('-t', '--tree', metavar='TREE', help="Name of the TTree containng the ntuple (default: 'Events')", default='Events')
        _optional_args.add_argument('-j', '--jobs', help="Number of jobs (threads) to use with EnableImplicitMT (default: 1)", default=1)
        _optional_args.add_argument('-n', '--num-events', help="Number of events to process. Incompatible with multithreading. Use 0 or negative for all (default)", default=-1)
        _optional_args.add_argument('--dry-run', help="Set up post-processing tasks, but do not execute", action='store_true')
        _optional_args.add_argument('--overwrite', help="Overwrite output file, if it exists.", action='store_true')
        _optional_args.add_argument('--log', help="Whether to output a log file.", action="store_true")
        _optional_args.add_argument('--dump-yaml', help="Whether to dump the task configuration as a YAML file.", action="store_true")
        _optional_args.add_argument('--progress', help="Whether to show a progress bar.", action="store_true")

        # retrieve analysis config (tasks, splittings, quantities, etc.)
        if _analysis_name is not None:
            _analysis_config = importlib.import_module("{}.{}".format(cfg_module.__name__, _analysis_name))
            for _required_config_key in ('TASKS', 'SPLITTINGS', 'QUANTITIES'):
                try:
                    getattr(_analysis_config, _required_config_key)
                except AttributeError:
                    raise AttributeError("Bad configuration for analysis '{}': "
                                        "mandatory key '{}' not defined!".format(_analysis_name, _required_config_key))
            TASKS = _analysis_config.TASKS.keys()
            SPLITTINGS = _analysis_config.SPLITTINGS.keys()
            _allowed_input_types = set(_analysis_config.QUANTITIES.keys()) - {"global"}
        else:
            TASKS = None
            SPLITTINGS = None
            _allowed_input_types = set()

        _required_args.add_argument('--input-type', metavar='TYPE', type=str, help='Sample type. Choices: {%(choices)s}', choices=_allowed_input_types, required=True)

        _subparsers = _top_parser.add_subparsers(help='Operation to perform. Available: {%(choices)s}', dest='subparser_name', metavar='SUBCOMMAND')
        _subparsers.required = True

        _parsers = {}

        # subcommand 'task' for executing pre-defined tasks
        _parsers['task'] = _subparsers.add_parser('task', help='Perform a pre-defined task')
        _parsers['task'].add_argument('TASK_NAME', type=str, help='Name of task(s) to perform. Choices: {%(choices)s}', nargs='+', choices=TASKS, metavar='TASK')
        #_parsers['task'].add_argument('--input-type', metavar='TYPE', type=str, help='Sample type Choices: {%(choices)s}', choices=_allowed_input_types, required=True)
        _parsers['task'].add_argument('--output-file-suffix', help="Suffix to append to output filename(s). If none is provided, the current date is used instead.", default=None)

        # subcommand 'freestyle' for manually specifying histograms and profiles
        _parsers['freestyle'] = _subparsers.add_parser('freestyle', help='Specify desired objects by hand')
        #_parsers['freestyle'].add_argument('--input-type', metavar='TYPE', type=str, help='Sample type Choices: {%(choices)s}', choices=_allowed_input_types, required=True)
        _parsers['freestyle'].add_argument('SPLITTING_KEY', type=str, help='Key(s) which identify the set of cuts used for '
                                           'separating the sample into subsamples. Choices: {%(choices)s}', nargs='+', choices=SPLITTINGS, metavar='SPLITTING')
        _parsers['freestyle'].add_argument('--histograms', metavar='HISTOGRAM', help='Specification of histograms', nargs='+')
        _parsers['freestyle'].add_argument('--profiles', metavar='PROFILE', help='Specification of profiles', nargs='+')
        _parsers['freestyle'].add_argument('--output-file', metavar='OUTPUT', help="Name of the output file.", required=True)

        _args = _top_parser.parse_args()

        return _top_parser.parse_args(), _analysis_config
