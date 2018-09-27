#!/usr/bin/env python
import argparse
import numpy as np
import os
import ROOT

from DijetAnalysis.PostProcessing.PP import SPLITTINGS, QUANTITY_BINNINGS
from DijetAnalysis.PostProcessing.PP import parse_args, basic_selection, split_df, create_histograms, create_profiles, write_to_file

try:
    RDataFrame = ROOT.ROOT.RDataFrame
except AttributeError:
    RDataFrame = ROOT.ROOT.Experimental.TDataFrame


if __name__ == "__main__":

    args = parse_args()

    # -- process arguments

    if os.path.exists(args.output_file) and not args.overwrite:
        raise Exception("Output file exists: '{}' and `--overwrite` not set".format(args.output_file))

    # retrieve splitting
    try:
        _splitting = SPLITTINGS[args.SPLITTING_KEY]
    except KeyError:
        raise KeyError("Cannot find splitting for key '{}'".format(args.SPLITTING_KEY))

    _xs = args.x_quantities
    _ys = args.y_quantities
    _ws = args.weights

    if _xs is None:
        print "[INFO] No `x-quantities` specified: nothing to do..."
        exit(1)

    # retrieve binnings for x quantities
    _unknown_keys = set(_xs) - set(QUANTITY_BINNINGS.keys())
    if _unknown_keys:
        raise KeyError("Unknown quantities specified in `x-quantities`: '{}'".format("', '".join(_unknown_keys)))
    _x_quantities_binnings = {_name: QUANTITY_BINNINGS[_name] for _name in _xs}

    # resolve weights
    if _ws is None:
        _ws = [None]
    elif None not in _ws:
        _ws = [None] + _ws

    # enable multithreading
    if args.jobs > 1:
        ROOT.ROOT.EnableImplicitMT(int(args.jobs))

    _df_bare = RDataFrame(args.tree, args.FILE)

    # -- apply basic analysis selection
    _df = basic_selection(_df_bare)

    # -- limit the number of processed events
    if args.num_events >= 0:
        _df = _df.Range(0, args.num_events)

    # -- split dataframe
    _split_dfs = split_df(_df, _splitting)

    # -- create quantity shape histograms for each split
    _hs = create_histograms(_split_dfs, _x_quantities_binnings, weights=_ws)

    # create profiles
    _ps = {}
    if _ys:
        _ps = create_profiles(_split_dfs, _x_quantities_binnings,
            vars_y=_ys)

    # -- write output
    write_to_file(args.output_file, histograms=_hs, profiles=_ps)

