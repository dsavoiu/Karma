#!/usr/bin/env python
import argparse
import itertools
import numpy as np
import os
import ROOT

from DijetAnalysis.PostProcessing.PP import SPLITTINGS, QUANTITY_BINNINGS
from DijetAnalysis.PostProcessing.PP import parse_args, basic_selection, PostProcessor

try:
    RDataFrame = ROOT.ROOT.RDataFrame
except AttributeError:
    RDataFrame = ROOT.ROOT.Experimental.TDataFrame


def product_dict(**kwargs):
    """Cartesian product of iterables in dictionary"""
    _keys = kwargs.keys()
    for instance in itertools.product(*kwargs.values()):
        yield dict(zip(_keys, instance))


if __name__ == "__main__":

    args = parse_args()

    # -- process arguments

    if os.path.exists(args.output_file) and not args.overwrite:
        raise Exception("Output file exists: '{}' and `--overwrite` not set".format(args.output_file))

    # retrieve splittings
    try:
        _splitting_specs = {_key : SPLITTINGS[_key] for _key in args.SPLITTING_KEY}
    except KeyError as e:
        raise KeyError("Cannot find splitting for key {}".format(e))

    # create combined splitting specification out of the cross product
    # of specified keys
    _combined_splittings = {}
    for _splitting_combination in product_dict(**_splitting_specs):
        _splitting_dict = {}
        for _key in args.SPLITTING_KEY:
            _splitting_dict.update(SPLITTINGS[_key][_splitting_combination[_key]])
        _splitting_name = "/".join([_splitting_combination[_key] for _key in args.SPLITTING_KEY])

        _combined_splittings[_splitting_name] = _splitting_dict

    _hs = args.histograms
    _ps = args.profiles

    if _hs is None and _ps is None:
        print "[INFO] No `histograms` or `profiles` specified: nothing to do..."
        exit(1)

    # enable multithreading
    if args.jobs > 1:
        ROOT.ROOT.EnableImplicitMT(int(args.jobs))

    _df_bare = RDataFrame(args.tree, args.FILE)

    # -- apply basic analysis selection
    _df = basic_selection(_df_bare)

    # -- limit the number of processed events
    if args.num_events >= 0:
        _df = _df.Range(0, args.num_events)

    _pp = PostProcessor(
        data_frame=_df,
        splitting_spec=_combined_splittings,
        quantity_binnings=QUANTITY_BINNINGS
    )

    if _hs is not None:
        _pp.add_histograms(_hs)
    if _ps is not None:
        _pp.add_profiles(_ps)

    _pp.run(output_file_path=args.output_file)

