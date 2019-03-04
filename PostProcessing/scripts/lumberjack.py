#!/usr/bin/env python
import abc
import datetime
import hashlib
import time
import numpy as np
import os
import re
import sys
import ROOT

from contextlib import contextmanager
from tqdm import tqdm


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


# determine correct ROOT DataFrame class
try:
    ROOT_DF_CLASS = ROOT.ROOT.RDataFrame
except AttributeError:
    ROOT_DF_CLASS = ROOT.ROOT.Experimental.TDataFrame

import DijetAnalysis.PostProcessing.Lumberjack as lj_module
ROOT_MACRO_FILENAME = os.path.join(os.path.dirname(lj_module.__file__), "_root_macros.C")


class PostProcessingInterfaceBase(object):

    RE_SPLITTING_KEY_SPEC = re.compile(r"([^[]]*)(\[(.*)\])?")

    def __init__(self, **kwargs):
        self._config = self._get_config(**kwargs)

    @abc.abstractmethod
    def _get_config(self, **kwargs):
        raise NotImplementedError  # implement in derived classes

    def _prepare_bare_data_frame(self):

        # -- enable multithreading
        if int(self._config.jobs) > 1:
            print "[INFO] Enabling multithreading with {} threads...".format(self._config.jobs)
            ROOT.ROOT.EnableImplicitMT(int(self._config.jobs))

        # -- set up data frame
        print "[INFO] Setting up data frame..."
        print "[INFO] Sample file: {}".format(self._config.input_file)

        # exit if input file does not exits exists
        if not os.path.exists(self._config.input_file):
            print("[ERROR] Input file does not exist: '{}'".format(self._config.input_file))
            exit(1)

        # exit if tree does not exist in file
        _f = ROOT.TFile(self._config.input_file, "READ")
        _tree = _f.Get(self._config.tree)
        if not isinstance(_tree, ROOT.TTree):
            print("[ERROR] Input file does not contain TTree '{}'".format(self._config.input_file))
            exit(1)
        self._df_size = _tree.GetEntries()
        _f.Close()

        print "[INFO] Sample type: {}".format(self._config.type)
        self._df_bare = ROOT_DF_CLASS(self._config.tree, self._config.input_file)

        print "[INFO] Defining ROOT macros..."

        with open(ROOT_MACRO_FILENAME, 'r') as _root_macro_file:
            ROOT.gInterpreter.Declare(''.join(_root_macro_file.readlines()))

    def _prepare_data_frame(self):

        from DijetAnalysis.PostProcessing.Lumberjack import QUANTITIES, DEFINES, SELECTIONS
        from DijetAnalysis.PostProcessing.Lumberjack import apply_defines, apply_filters, define_quantities

        # -- limit the number of processed events
        if self._config.num_events >= 0:
            print "[INFO] Limiting number of processed events to: ".format(self._config.num_events)
            self._df_bare = self._df_bare.Range(0, int(self._config.num_events))
            self._df_size = min(self._df_size, int(self._config.num_events))
            self._df_count_increment = max(self._df_size//100, 10)

        # -- set up event counter (for progress reporting)
        self._df_count = self._df_bare.Count()
        self._df_count_increment = 100000

        if self._config.progress:
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
        print "[INFO] Defining quantities..."
        self._df = apply_defines(self._df_bare, DEFINES['global'])
        if self._config.type in DEFINES:
            self._df = apply_defines(self._df, DEFINES[self._config.type])

        _quantities =  dict(QUANTITIES['global'], **QUANTITIES.get(self._config.type, {}))
        self._df = define_quantities(self._df, _quantities)

        if self._config.selections is not None:
            for _sel in self._config.selections:
                print "[INFO] Applying global selection '{}'...".format(_sel)
                if _sel not in SELECTIONS:
                    raise ValueError("Unknown selection '{}'".format(_sel))
                self._df = apply_filters(self._df, SELECTIONS[_sel])

    def _cleanup_data_frame(self):
        pass  # what to do here?

    @staticmethod
    def _expand_subtasks(task_configs):
        '''replace single task with subtasks, if slicing a particular splitting is enabled'''
        from DijetAnalysis.PostProcessing.Lumberjack import SPLITTINGS

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

        from DijetAnalysis.PostProcessing.Lumberjack import SPLITTINGS
        from DijetAnalysis.PostProcessing.Lumberjack import PostProcessor, Timer

        task_configs = self._expand_subtasks(task_configs)

        # -- run all queued tasks
        for _task_name, _task_spec in task_configs:

            # skip task if output file exists
            if os.path.exists(_task_spec['_filename']) and not self._config.overwrite:
                print("[INFO] Task output file exists: '{}' and `--overwrite` not set. Skipping...".format(_task_spec['_filename']))
                continue

            with log_stdout_to_file(_task_spec['_log_filename']):
                print "[INFO] Running task '{}'...".format(_task_name)

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
                    print "[ERROR] No `histograms` or `profiles` configured for task '{}': skipping...".format(_task_name)
                    continue

                print "[INFO] Setting up PostProcessor..."
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

                print "[INFO] Running Task '{}':".format(_task_name)
                print "    - splitting RDataFrame by keys: {}".format(
                    ", ".join(["{} ({} subdivisions)".format(_key, len(_splitting)) for _key, _splitting in _splitting_specs.iteritems()])
                )
                print "        -> total number of subdivisions: {}\n".format(_n_subdiv)
                print "    - requested number of objects per subdivision: {}\n".format(_n_obj)
                print "    -> total number of objects: {}\n".format(_n_obj * _n_subdiv)
                print "    - output file: {}".format(_task_spec['_filename'])

                # run PostProcessor and time execution
                with Timer(_task_name) as _t:
                    if self._config.dry_run:
                        print "[INFO] `--dry-run` has been specified: not running task '{}'".format(_task_name)
                        time.sleep(0.1)
                    else:
                        _pp.run(output_file_path=_task_spec['_filename'])

                # print report
                if not self._config.dry_run:
                    print "[INFO] Processed a total of {} events.".format(self._df_count.GetValue())
                _t.report()

                print "[INFO] Cleaning up after task '{}'...".format(_task_name)
                self._cleanup_data_frame()


    # -- subcommand methods

    def _subcommand_freestyle(self):

        from DijetAnalysis.PostProcessing.Lumberjack import QUANTITIES
        from DijetAnalysis.PostProcessing.Lumberjack import apply_defines, apply_filters, define_quantities, PostProcessor, Timer

        # -- configure and queue freestyle task

        # exit if output filename exists
        if os.path.exists(self._config.output_file) and not self._config.overwrite:
            print("[INFO] Output file exists: '{}' and `--overwrite` not set. Exiting...".format(self._config.output_file))
            exit(1)

        # configure single 'Freestyle' task
        _task_spec = dict(
            _filename = self._config.output_file,
            _log_filename = "{}.log".format(self._config.output_file.split('.', 1)[0]) if self._config.log else None,
            _quantities =  dict(QUANTITIES['global'], **QUANTITIES.get(self._config.type, {})),
            splittings = self._config.SPLITTING_KEY,
            histograms = self._config.histograms,
            profiles = self._config.profiles,
        )
        _tasks = [("Freestyle", _task_spec)]

        self._prepare_bare_data_frame()
        self._run_tasks(_tasks)


    def _subcommand_task(self):

        from DijetAnalysis.PostProcessing.Lumberjack import QUANTITIES, TASKS

        # -- determine output filename suffix
        _suffix = self._config.output_file_suffix
        if _suffix is None:
            _suffix = "{}".format(datetime.datetime.now().strftime("%Y-%m-%d"))

        # -- configure and queue task(s)
        _tasks = []
        for _task_name in self._config.TASK_NAME:
            _task_spec = TASKS.get(_task_name, None)
            if _task_spec is None:
                raise ValueError("[ERROR] Unknown task '{}': expected one of {}".format(_task, set(TASKS.keys())))


            # add task to queue
            _task_spec['_filename'] = "{}_{}.root".format(_task_name, _suffix)
            _task_spec['_log_filename'] = "{}_{}.log".format(_task_name, _suffix) if self._config.log else None
            _task_spec['_quantities'] = dict(QUANTITIES['global'], **QUANTITIES.get(self._config.type, {}))
            _tasks.append((_task_name, _task_spec))

        if not _tasks:
            print "[INFO] No tasks in queue. Exiting..."
            exit(1)

        self._prepare_bare_data_frame()
        self._run_tasks(_tasks)


    # -- public API

    def run(self):

        if self._config.subparser_name == 'task':
            self._subcommand_task()

        elif self._config.subparser_name == 'freestyle':
            self._subcommand_freestyle()

        else:
            raise ValueError("Unknown operation '{}'! Exiting...".format(_args.subparser_name))


class PostProcessingCLI(PostProcessingInterfaceBase):
    def __init__(self):
        super(PostProcessingCLI, self).__init__()  # no kwargs

    def _get_config(self):
        '''parse CLI arguments and store in self._config'''
        import argparse

        from DijetAnalysis.PostProcessing.Lumberjack import TASKS, SPLITTINGS

        _top_parser = argparse.ArgumentParser(description='Split an input TTree into subsamples and produce ROOT files containing TH1D, TH2D or TProfile objects for each subdivision.')
        _top_parser.add_argument('-i', '--input-file', metavar='FILE', type=str, help='Input file', required=True)
        _top_parser.add_argument('-t', '--tree', metavar='TREE', help="Name of the TTree containng the ntuple (default: 'Events')", default='Events')
        _top_parser.add_argument('--type', metavar='TYPE', type=str, help='Sample type', choices=['data', 'mc'], required=True)
        _top_parser.add_argument('-j', '--jobs', help="Number of jobs (threads) to use with EnableImplicitMT (default: 1)", default=1)
        _top_parser.add_argument('-n', '--num-events', help="Number of events to process. Incompatible with multithreading. Use 0 or negative for all (default)", default=-1)
        _top_parser.add_argument('--dry-run', help="Set up post-processing tasks, but do not execute", action='store_true')
        _top_parser.add_argument('--overwrite', help="Overwrite output file, if it exists.", action='store_true')
        _top_parser.add_argument('--log', help="Whether to output a log file.", action="store_true")
        _top_parser.add_argument('--progress', help="Whether to show a progress bar.", action="store_true")
        _top_parser.add_argument('--selections', metavar='SELECTION', help='Specification of event selection cuts', nargs='+')

        _subparsers = _top_parser.add_subparsers(help='Operation to perform', dest='subparser_name')
        _subparsers.required = True

        _parsers = {}

        # subcommand 'task' for executing pre-defined tasks
        _parsers['task'] = _subparsers.add_parser('task', help='Perform a pre-defined task')
        _parsers['task'].add_argument('TASK_NAME', type=str, help='Name of task(s) to perform', nargs='+', choices=TASKS.keys())
        _parsers['task'].add_argument('--output-file-suffix', help="Suffix to append to output filename(s). If none is provided, the current date is used instead.", default=None)

        # subcommand 'freestyle' for manually specifying histograms and profiles
        _parsers['freestyle'] = _subparsers.add_parser('freestyle', help='Specify desired objects by hand')
        _parsers['freestyle'].add_argument('SPLITTING_KEY', type=str, help='Key(s) which identify the set of cuts used for separating the sample into subsamples', nargs='+', choices=SPLITTINGS.keys())
        _parsers['freestyle'].add_argument('--histograms', metavar='HISTOGRAM', help='Specification of histograms', nargs='+')
        _parsers['freestyle'].add_argument('--profiles', metavar='PROFILE', help='Specification of profiles', nargs='+')
        _parsers['freestyle'].add_argument('--output-file', metavar='OUTPUT', help="Name of the output file.", required=True)

        return _top_parser.parse_args()


if __name__ == "__main__":

    _cli = PostProcessingCLI()

    _cli.run()
