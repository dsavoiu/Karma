# -*- coding: utf8 -*-
import datetime
import itertools

from Karma.PostProcessing.Palisade import InputROOT, AnalyzeProcessor

#from rootpy.plotting.hist import Hist, Hist2D


@InputROOT.add_function(override=True)
def normalize(th1d):
    #th1d = th1d.Clone()
    #th1d.Scale(1.0/th1d.Integral())
    return th1d / th1d.Integral()

def get_config(args):

    assert len(args.filenames_data) == len(args.filenames_mc) == len(args.filenames_output)

    _input_files = {}
    for _i, (_fd, _fm) in enumerate(zip(args.filenames_data, args.filenames_mc)):
        _input_files['d_{}'.format(_i)] = _fd
        _input_files['m_{}'.format(_i)] = _fm

    return {
        'input_files': _input_files,
        'tasks': [
            dict(
                filename=_fo,
                subtasks=[
                    dict(
                        expression='normalize("d_{0}:pileup") / normalize("m_{0}:pileup")'.format(_i),
                        output_path="pileupWeight",
                    )
                ]
            )
            for _i, _fo in enumerate(args.filenames_output)
        ],
        'expansions' : {}
    }


def cli(argument_parser):
    '''command-line interface. builds on an existing `argparse.ArgumentParser` instance.'''

    # define CLI arguments
    argument_parser.add_argument('-d', '--filenames-data', help="files containing pileup profiles for data", metavar="FILE_DATA", nargs='+')
    argument_parser.add_argument('-m', '--filenames-mc', help="files containing pileup profiles for MC", metavar="FILE_MC", nargs='+')
    argument_parser.add_argument('-o', '--filenames-output', help="files containing pileup weights", metavar="FILE_OUT", nargs='+')

    argument_parser.add_argument('--output-dir', help="directory in which to place outputs", default=None)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    cli(ap)
    args = ap.parse_args()

    assert args.output_dir is not None
    _n_filenames = list(map(len, [args.filenames_data, args.filenames_mc, args.filenames_output]))
    _nontrivial_n_filenames = set(_n_filenames).difference({1})
    if len(_nontrivial_n_filenames) > 1:
        raise ValueError("Number of filenames for 'data' ({}), 'mc' ({}) and 'output' ({}) must match or be 1!'".format())

    _n_filenames = max(_n_filenames)
    for arg_name in ('filenames_data', 'filenames_mc', 'filenames_output'):
        if len(getattr(args, arg_name)) == 1:
            setattr(args, arg_name, getattr(args, arg_name) * _n_filenames)

    print "Running..."
    _cfg = get_config(args)

    p = AnalyzeProcessor(_cfg, output_folder=args.output_dir)
    p.run()
