#!/usr/bin/env python
import ROOT
import os
from copy import deepcopy
import argparse



class PUMCCalculator(object):
    """
    Read skim outputs and write out their combined pile-up profile.

    Output: a ROOT file with a TH1D containing the pile-up profile.
    """

    def __init__(self, skim_output_dirs):
        self._skim_output_dirs = []
        for _dir in skim_output_dirs:
            if not os.path.isdir(_dir):
                raise OSError("Skim directory not found: {}".format(_dir))
            self._skim_output_dirs.append(os.path.normpath(_dir))

    def produce_mc_pileup(self, target_file, read_max_n_skim_files=None):

        # -- do not overwrite
        if os.path.exists(target_file):
            raise OSError("Cannot write MC PU: file exists ('{}')".format(target_file))

        # -- obtain file list from skim output directory
        _files = []
        for _dir in self._skim_output_dirs:
            _files.extend([os.path.join(_dir, _file) for _file in os.listdir(_dir)])

        if read_max_n_skim_files is not None:
            _files = _files[:read_max_n_skim_files]

        print "Producing MC PU distribution from {} skim output files...".format(len(_files))

        # -- create a TChain and a TH1D for storing results
        _tmp_chain = ROOT.TChain("Events")
        _mc_pu_hist = ROOT.TH1D("pileup", "True Number of Pile-Up Interactions;nputruth;events", 80, 0, 80)

        # -- add TTree from each skim output to TChain
        for _file in _files:
            print "Getting PU distribution from file '{}'".format(_file)
            _tmp_chain.Add(_file)

        print "Merging PU distributions..."
        _tmp_chain.Draw("dijetEvents.nPUTrue >> pileup", "", "goff")

        print "Writing PU distribution from {} skim output files to file '{}'".format(len(_files), target_file)
        _tmp_target_rootfile = ROOT.TFile(target_file, "RECREATE")
        _mc_pu_hist.Write()
        _tmp_target_rootfile.Close()


class PUWeightsCalculator(object):
    """
    Calculate weights for reweighting a MC pile-up (PU) profile to a
    specified Data PU profile.

    Output: a ROOT file with a TH1D containing the Data/MC weights
    """

    def __init__(self, pu_data_file, pu_mc_file):
        #self._pu_data = os.path.join(PILEUP_DATA_DIR, pu_data_file)
        self._pu_data = pu_data_file
        if not os.path.exists(self._pu_data):
            raise OSError("Data file not found: {}".format(self._pu_data))

        #self._pu_mc = os.path.join(PILEUP_DATA_DIR, pu_mc_file)
        self._pu_mc = pu_mc_file
        if not os.path.exists(self._pu_mc):
            raise OSError("MC file not found: {}".format(self._pu_mc))

    def produce_pileup_weights(self, target_file):
        #_pu_weights_outfile = os.path.join(PILEUP_DATA_DIR, target_file)

        # -- obtain normalized Data Pileup profile
        print "Loading data PU distribution from file '{}'...".format(self._pu_data)
        _pu_data_input_rootfile = ROOT.TFile(self._pu_data, "READ")
        _pu_data_hist = _pu_data_input_rootfile.Get("pileup")
        _pu_data_hist.Scale(1.0/_pu_data_hist.Integral())
        _pu_data_hist = deepcopy(_pu_data_hist)
        _pu_data_input_rootfile.Close()

        # -- obtain normalized MC Pileup profile
        print "Loading MC PU distribution from file '{}'...".format(self._pu_mc)
        _pu_mc_input_rootfile = ROOT.TFile(self._pu_mc, "READ")
        _pu_mc_hist = _pu_mc_input_rootfile.Get("pileup")
        _pu_mc_hist.Scale(1.0/_pu_mc_hist.Integral())
        _pu_mc_hist = deepcopy(_pu_mc_hist)
        _pu_mc_input_rootfile.Close()

        # -- compute weights as Data/MC ratio
        _pu_data_hist.Divide(_pu_mc_hist)

        print "Writing Data/MC PU weights to file '{}'...".format(target_file)
        _pu_weights_output_rootfile = ROOT.TFile(target_file, "RECREATE")
        _pu_data_hist.Write()
        _pu_weights_output_rootfile.Close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Compute weights for Data/MC PU reweighting')

    subparsers = parser.add_subparsers(help='Which subcommand to run',
                                       dest='which')

    mc_pu_prof_parser = subparsers.add_parser('mc_pu_prof')
    mc_pu_prof_parser.add_argument(
        '-s', '--skim-dirs',
        type=str,
        help="Directory containing KAPPA skim outputs for MC sample",
        nargs='+',
        required=True,
    )
    mc_pu_prof_parser.add_argument(
        '-o', '--output',
        type=str,
        required=True,
        help="Output file containing the MC PU profile",
    )
    mc_pu_prof_parser.add_argument(
        '-n', '--number-of-files',
        type=int,
        help="Number of MC files to use for computing MC PU profile",
        default=None,
        required=False
    )

    datamc_pu_weights_parser = subparsers.add_parser('datamc_pu_weights')
    datamc_pu_weights_parser.add_argument(
        '-d', '--data',
        type=str,
        required=True,
        help="Name of the file containing the data PU profile."
    )
    datamc_pu_weights_parser.add_argument(
        '-m', '--mc',
        type=str,
        required=True,
        help="Name of the file containing the MC PU profile.",
    )
    datamc_pu_weights_parser.add_argument(
        '-o', '--output',
        type=str,
        required=True,
        help="Output file containing the Data/MC PU profile.",
    )

    args = parser.parse_args()

    if args.which == 'mc_pu_prof':
        _pu_mc_calc = PUMCCalculator(skim_output_dirs=args.skim_dirs)
        _pu_mc_calc.produce_mc_pileup(target_file=args.output,
                                      read_max_n_skim_files=args.number_of_files)
    elif args.which == 'datamc_pu_weights':
        _pu_weights_calc = PUWeightsCalculator(pu_data_file=args.data,
                                               pu_mc_file=args.mc)
        _pu_weights_calc.produce_pileup_weights(target_file=args.output)
    else:
        raise ValueError("Invalid subcommand '{}': expected one of {}".format(args.which, set('mc_pu_prof', 'datamc_pu_weights')))
