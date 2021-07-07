#!/usr/bin/env python
import hashlib
import os
import tqdm
import ROOT

from argparse import ArgumentParser
from array import array

if __name__ == "__main__":
    _ap = ArgumentParser(description="""
    Create a proxy ROOT file with TChains that link all the TTrees in the input files together using their XRootD paths.
    The input files are assumed to have the same structure: the top level contains directories which each contain
    one or more TTrees. The TTree names must be the same in all directories and in all files.
    """)

    _ap.add_argument('input_proxy_file', help="Source proxy file containing 'Events' TChain for entire skim.", metavar='INPUT_FILE')
    _ap.add_argument('output_file', help="Destination file that will contain the PU profiles", metavar='OUTPUT_FILE')
    _ap.add_argument('-b', '--bins', help="Number of pileup bins (== max pileup value)", metavar='BINS', type=int, default=80)
    _ap.add_argument('-j', '--jobs', help="Number of threads to use", metavar='JOBS', type=int, default=1)

    _ap.add_argument('-f', '--overwrite', help="overwrite an existing output file", action='store_true')

    args = _ap.parse_args()

    # enable multithreading
    if int(args.jobs) > 1:
        print("[INFO] Enabling multithreading with {} threads...".format(args.jobs))
        ROOT.ROOT.EnableImplicitMT(int(args.jobs))
    else:
        ROOT.ROOT.DisableImplicitMT()  # exlicitly disable multithreading


    _f = ROOT.TFile(args.input_proxy_file, "READ")
    _tree = _f.Get("Events")
    if not isinstance(_tree, ROOT.TTree):
        print("[ERROR] Input file does not contain TTree 'Events'")
        exit(1)

    _hist = ROOT.TH1D("pileup", "pileup", args.bins, 0, args.bins)
    print("[INFO] Running event loop...")
    #_tree.Draw("karmaEvent_karmaEvents__KARMASKIM.obj.nPUTrue >> pileup")
    _tree.Draw("karmaEvents.nPUTrue >> pileup", "", "GOFF")

    # disown hist so it persists when file is closed
    _hist.SetDirectory(0)
    _f.Close()

    _f_out = ROOT.TFile(args.output_file, "RECREATE")
    _f_out.cd()
    _hist.Write()
    _f_out.Close()
