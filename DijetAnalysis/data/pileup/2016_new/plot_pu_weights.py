# -*- coding: utf8 -*-
import datetime
import itertools

from Karma.PostProcessing.Palisade import InputROOT, PlotProcessor

#from rootpy.plotting.hist import Hist, Hist2D


@InputROOT.add_function(override=True)
def normalize(th1d):
    #th1d = th1d.Clone()
    #th1d.Scale(1.0/th1d.Integral())
    return th1d / th1d.Integral()

def get_config(args):

    assert len(args.filenames_data) == len(args.filenames_mc) == len(args.labels) == len(args.colors)

    _input_files = {}
    for _i, (_fd, _fm) in enumerate(zip(args.filenames_data, args.filenames_mc)):
        _input_files['d_{}'.format(_i)] = _fd
        _input_files['m_{}'.format(_i)] = _fm

    return {
        'input_files': _input_files,
        'figures': [
            {
                'filename': args.output_filename,
                'figsize': (6, 4),
                'subplots': [
                    dict(
                        expression='normalize("d_{0}:pileup") / normalize("m_{0}:pileup")'.format(_i),
                        plot_method='step', #'errorbar',
                        label=_l,
                        color=_c
                        #marker='o',
                    )
                    for _i, (_l, _c) in enumerate(zip(args.labels, args.colors))
                ],
                'pads': [
                    {
                        'y_range': (0, 10),
                    }
                ]
            }
        ],
        'expansions' : {}
    }


def cli(argument_parser):
    '''command-line interface. builds on an existing `argparse.ArgumentParser` instance.'''

    # define CLI arguments
    argument_parser.add_argument('-d', '--filenames-data', help="files containing pileup profiles for data", metavar="FILE_DATA", nargs='+')
    argument_parser.add_argument('-m', '--filenames-mc', help="files containing pileup profiles for MC", metavar="FILE_MC", nargs='+')
    argument_parser.add_argument('-l', '--labels', help="legend label for each subplot", metavar="LABEL", nargs='+')
    argument_parser.add_argument('-c', '--colors', help="legend label for each subplot", metavar="COLOR", nargs='*')

    argument_parser.add_argument('--output-dir', help="directory in which to place outputs", default=None)
    argument_parser.add_argument('-o', '--output-filename', help="file containing pileup weight plot", metavar="FILE_OUT", required=True)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    cli(ap)
    args = ap.parse_args()

    assert args.output_dir is not None
    _n_filenames = list(map(len, [args.filenames_data, args.filenames_mc, args.labels, args.colors]))
    _nontrivial_n_filenames = set(_n_filenames).difference({1})
    if len(_nontrivial_n_filenames) > 1:
        raise ValueError("Number of arguments for 'data' ({}), 'mc' ({}), 'labels' ({}) and 'colors' ({}) must match or be 1!'".format(
            len(args.filenames_data), len(args.filenames_mc), len(args.labels), len(args.colors)
        ))

    _n_filenames = max(_n_filenames)

    if not args.colors:
        args.colors = [None] * _n_filenames

    for arg_name in ('filenames_data', 'filenames_mc', 'labels', 'colors'):
        if len(getattr(args, arg_name)) == 1:
            setattr(args, arg_name, getattr(args, arg_name) * _n_filenames)

    print "Running..."
    _cfg = get_config(args)

    p = PlotProcessor(_cfg, output_folder=args.output_dir)
    p.run()
