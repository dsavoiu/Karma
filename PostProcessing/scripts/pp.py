#!/usr/bin/env python
import datetime
import time
import numpy as np
import os
import ROOT


def product_dict(**kwargs):
    """Cartesian product of iterables in dictionary"""
    import itertools
    _keys = kwargs.keys()
    for instance in itertools.product(*kwargs.values()):
        yield dict(zip(_keys, instance))


class PostProcessingCLI(object):

    def __init__(self):

        # determine correct ROOT DataFrame class
        try:
            self._df_class = ROOT.ROOT.RDataFrame
        except AttributeError:
            self._df_class = ROOT.ROOT.Experimental.TDataFrame

        self._parse_args()


    def _parse_args(self):
        import argparse

        from DijetAnalysis.PostProcessing.PP import TASKS, SPLITTINGS

        self._top_parser = argparse.ArgumentParser(description='Split an input TTree into subsamples and produce ROOT files containing TH1D, TH2D or TProfile objects for each subdivision.')
        self._top_parser.add_argument('-i', '--input-file', metavar='FILE', type=str, help='Input file', required=True)
        self._top_parser.add_argument('-t', '--tree', metavar='TREE', help="Name of the TTree containng the ntuple (default: 'Events')", default='Events')
        self._top_parser.add_argument('--type', metavar='TYPE', type=str, help='Sample type', choices=['data', 'mc'], required=True)
        self._top_parser.add_argument('-j', '--jobs', help="Number of jobs (threads) to use with EnableImplicitMT (default: 1)", default=1)
        self._top_parser.add_argument('-n', '--num-events', help="Number of events to process. Incompatible with multithreading. Use 0 or negative for all (default)", default=-1)
        self._top_parser.add_argument('--dry-run', help="Set up post-processing tasks, but do not execute", action='store_true')
        self._top_parser.add_argument('--overwrite', help="Overwrite output file, if it exists.", action='store_true')

        self._subparsers = self._top_parser.add_subparsers(help='Operation to perform', dest='subparser_name')
        self._subparsers.required = True

        self._parsers = {}

        # subcommand 'task' for executing pre-defined tasks
        self._parsers['task'] = self._subparsers.add_parser('task', help='Perform a pre-defined task')
        self._parsers['task'].add_argument('TASK_NAME', type=str, help='Name of task(s) to perform', nargs='+', choices=TASKS.keys())
        self._parsers['task'].add_argument('--output-file-suffix', help="Suffix to append to output filenames. If none is privided, the current date is used instead.", default=None)

        # subcommand 'freestyle' for manually specifying histograms and profiles
        self._parsers['freestyle'] = self._subparsers.add_parser('freestyle', help='Specify desired objects by hand')
        self._parsers['freestyle'].add_argument('SPLITTING_KEY', type=str, help='Key(s) which identify the set of cuts used for separating the sample into subsamples', nargs='+', choices=SPLITTINGS.keys())
        self._parsers['freestyle'].add_argument('--histograms', metavar='HISTOGRAM', help='Specification of histograms', nargs='+')
        self._parsers['freestyle'].add_argument('--profiles', metavar='PROFILE', help='Specification of profiles', nargs='+')
        self._parsers['freestyle'].add_argument('--output-file', metavar='OUTPUT', help="Name of the output file.", required=True)

        self._args = self._top_parser.parse_args()


    def _prepare_data_frame(self):

        from DijetAnalysis.PostProcessing.PP import QUANTITIES, DEFINES, BASIC_SELECTION
        from DijetAnalysis.PostProcessing.PP import apply_defines, apply_filters, define_quantities

        # -- enable multithreading
        if self._args.jobs > 1:
            print "[INFO] Enabling multithreading with {} threads...".format(self._args.jobs)
            ROOT.ROOT.EnableImplicitMT(int(self._args.jobs))

        # -- set up data frame
        print "[INFO] Setting up data frame..."
        print "[INFO] Sample file: {}".format(self._args.input_file)

        # exit if input file does not exits exists
        if not os.path.exists(self._args.input_file):
            print("[ERROR] Input file does not exist: '{}'".format(self._args.input_file))
            exit(1)

        # exit if tree does not exist in file
        _f = ROOT.TFile(self._args.input_file, "READ")
        _tree = _f.Get(self._args.tree)
        if not isinstance(_tree, ROOT.TTree):
            print("[ERROR] Input file does not contain TTree '{}'".format(self._args.input_file))
            exit(1)
        _f.Close()

        print "[INFO] Sample type: {}".format(self._args.type)
        self._df = self._df_class(self._args.tree, self._args.input_file)

        # -- apply basic analysis selection
        print "[INFO] Defining quantities..."
        self._df = apply_defines(self._df, DEFINES['global'])
        if self._args.type in DEFINES:
            self._df = apply_defines(self._df, DEFINES[self._args.type])

        _quantities =  dict(QUANTITIES['global'], **QUANTITIES.get(self._args.type, {}))
        self._df = define_quantities(self._df, _quantities)

        print "[INFO] Applying global selection..."
        self._df = apply_filters(self._df, BASIC_SELECTION)


    def _run_tasks(self, task_configs):

        from DijetAnalysis.PostProcessing.PP import SPLITTINGS
        from DijetAnalysis.PostProcessing.PP import PostProcessor, Timer

        # -- run all queued tasks
        for _task_name, _task_spec in task_configs:
            print "[INFO] Running task '{}'...".format(_task_name)

            _splittings_keys = _task_spec.get('splittings')
            # retrieve splittings for task
            try:
                _splitting_specs = {_key : SPLITTINGS[_key] for _key in _splittings_keys}
            except KeyError as e:
                raise KeyError("[ERROR] Cannot find splitting for key '{}'".format(e))

            # create combined splitting specification out of the cross product
            # of specified keys
            _combined_splittings = {}
            for _splitting_combination in product_dict(**_splitting_specs):
                _splitting_dict = {}
                for _key in _splittings_keys:
                    _splitting_dict.update(SPLITTINGS[_key][_splitting_combination[_key]])
                _splitting_name = "/".join([_splitting_combination[_key] for _key in _splittings_keys])

                _combined_splittings[_splitting_name] = _splitting_dict

            _hs = _task_spec.get('histograms', None)
            _ps = _task_spec.get('profiles', None)

            if _hs is None and _ps is None:
                print "[ERROR] No `histograms` or `profiles` configured for task '{}': skipping...".format(_task_name)
                continue

            # -- limit the number of processed events
            if self._args.num_events >= 0:
                print "[INFO] Limiting number of processed events to: ".format(self._args.num_events)
                _df = _df.Range(0, self._args.num_events)

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
                if self._args.dry_run:
                    print "[INFO] `--dry-run` has been specified: not running task '{}'".format(_task_name)
                    time.sleep(0.1)
                else:
                    _pp.run(output_file_path=_task_spec['_filename'])

            # print time report
            _t.report()


    # -- subcommand methods

    def _subcommand_freestyle(self):

        from DijetAnalysis.PostProcessing.PP import QUANTITIES, DEFINES, BASIC_SELECTION, SPLITTINGS
        from DijetAnalysis.PostProcessing.PP import apply_defines, apply_filters, define_quantities, PostProcessor, Timer

        # -- configure and queue freestyle task

        # exit if output filename exists
        if os.path.exists(self._args.output_file) and not self._args.overwrite:
            print("[INFO] Output file exists: '{}' and `--overwrite` not set. Exiting...".format(self._args.output_file))
            exit(1)

        print dict(QUANTITIES['global'], **QUANTITIES.get(self._args.type, {}))

        # configure single 'Freestyle' task
        _task_spec = dict(
            _filename = self._args.output_file,
            _quantities =  dict(QUANTITIES['global'], **QUANTITIES.get(self._args.type, {})),
            splittings = self._args.SPLITTING_KEY,
            histograms = self._args.histograms,
            profiles = self._args.profiles,
        )
        _tasks = [("Freestyle", _task_spec)]

        self._prepare_data_frame()
        self._run_tasks(_tasks)


    def _subcommand_task(self):

        from DijetAnalysis.PostProcessing.PP import QUANTITIES, TASKS

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

            # skip task if output filename exists
            _output_filename = "{}_{}.root".format(_task_name, _suffix)
            if os.path.exists(_output_filename) and not self._args.overwrite:
                print("[INFO] Task '{}' output file exists: '{}' and `--overwrite` not set. Skipping...".format(_task_name, _output_filename))
                continue

            # add task to queue
            _task_spec['_filename'] = _output_filename
            _task_spec['_quantities'] =  dict(QUANTITIES['global'], **QUANTITIES.get(self._args.type, {}))
            _tasks.append((_task_name, _task_spec))

        if not _tasks:
            print "[INFO] No tasks in queue. Exiting..."
            exit(1)


        self._prepare_data_frame()
        self._run_tasks(_tasks)


    # -- public API

    def run(self):

        if self._args.subparser_name == 'task':
            self._subcommand_task()

        elif self._args.subparser_name == 'freestyle':
            self._subcommand_freestyle()

        else:
            raise ValueError("Unknown operation '{}'! Exiting...".format(_args.subparser_name))


if __name__ == "__main__":

    _cli = PostProcessingCLI()

    _cli.run()
