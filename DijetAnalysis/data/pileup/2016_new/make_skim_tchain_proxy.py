#!/usr/bin/env python
import os
import ROOT

from argparse import ArgumentParser

if __name__ == "__main__":
    _ap = ArgumentParser(description="""
    Create a proxy ROOT file with TChains that link all the TTrees in the input files together using their XRootD paths.
    The input files are assumed to have the same structure: the top level contains directories which each contain
    one or more TTrees. The TTree names must be the same in all directories and in all files.
    """)

    _ap.add_argument('output_file', help="Destination file that will contain the TTrees", metavar='OUTPUT_FILE')
    _ap.add_argument('files', nargs='+', help='Input files to be merged. They must have an identical structure. Only trees one directory deep will be merged as a TChain over XRootD.', metavar='FILE')

    _ap.add_argument('-c', '--check', help="check that the linking was successful by calling GetEntries on the resulting TChain", action='store_true')
    _ap.add_argument('-f', '--overwrite', help="overwrite an existing output file", action='store_true')

    args = _ap.parse_args()

    # retrieve directories and tree names from first file
    _f = ROOT.TFile.Open(args.files[0])
    _trees = list(_k.GetName() for _k in _f.GetListOfKeys())
    _f.Close()
    
    if not args.overwrite and os.path.exists(args.output_file):
        raise IOError("File '{}' exists and `--overwrite` is not set. Aborting.".format(args.output_file))

    _f_out = ROOT.TFile(args.output_file, "RECREATE")
    for _tree in _trees:
        _tchain = ROOT.TChain(_tree)
        _full_tree_path = "{}".format(_tree)
    
        print("[INFO] Linking trees in {} files under '{}'...".format(len(args.files), _full_tree_path))
        for _file in args.files:
            if not _tchain.AddFile(_file, ROOT.TTree.kMaxEntries, _full_tree_path):
                raise RuntimeError('[ERROR] Could not connect tree {} in file {} to TChain!'.format(_full_tree_path, _file))
        # test the links
        if args.check:
            _num_entries = _tchain.GetEntries()
            print("[INFO] Linking successful. Combined TChain yielded {} entries.".format(_num_entries))
        _tchain.Write()

    _f_out.Close()
