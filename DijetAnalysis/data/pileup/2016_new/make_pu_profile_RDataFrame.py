#!/usr/bin/env python
import hashlib
import os
import tqdm
import ROOT

from argparse import ArgumentParser
from array import array

# determine correct ROOT DataFrame class
try:
    ROOT_DF_CLASS = ROOT.ROOT.RDataFrame
    ROOT_TH1D_MODEL_CLASS = ROOT.RDF.TH1DModel
    DO_PROGRESS = True
except AttributeError:
    print("[WARNING] ROOT version {} only contains experimental implementation of RDataFrames. Moderate to severe "
          "performance penalties may be encountered. Consider switching to a newer version of ROOT (>=6.14).".format(
              ROOT.gROOT.GetVersion()))
    DO_PROGRESS = False
    try:
        ROOT_DF_CLASS = ROOT.ROOT.Experimental.TDataFrame
        ROOT_TH1D_MODEL_CLASS = ROOT.ROOT.Experimental.TDF.TH1DModel
    except AttributeError:
        print("[ERROR] ROOT version {} does not contain an implementation of RDataFrames. Please switch to a newer "
              "version of ROOT (>=6.14).".format(ROOT.gROOT.GetVersion()))
        exit(1)

def _setup_progress_bar(df, df_size=None, df_count_increment=10000):
    df_count = df.Count()  # set up simple event counter
    _progress = tqdm.tqdm(
        unit=" events",
        unit_scale=False,
        dynamic_ncols=True,
        desc="Event loop progress",
        total=df_size,
        mininterval=1,
    )
    def _progress_callback(count):
        _progress.update(df_count_increment)

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
    df_count.OnPartialResultSlot(df_count_increment, getattr(ROOT, _func_slotcallback_fullname))


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

    # handle TChains a little differently
    if isinstance(_tree, ROOT.TChain):
        # loading TTrees from a TChain can take a while -> inform user
        print("[INFO] Input tree is a TChain. Loading underlying TTrees to compute the total number of entries...")
        _df_size = _tree.GetEntries()
        # disown TChain so it persists when file is closed
        _tree.SetDirectory(0)
        _f.Close()
        df = ROOT_DF_CLASS(_tree)
    else:
        _df_size = _tree.GetEntries()
        df = ROOT_DF_CLASS('Events', args.input_proxy_file)

    print("[INFO] Input tree contains {} entries.".format(_df_size))
    if DO_PROGRESS:
        _setup_progress_bar(df, df_size=_df_size, df_count_increment=10000)

    _binning = list(range(args.bins+1))
    _hist_model = ROOT_TH1D_MODEL_CLASS("pileup", "pileup", len(_binning)-1, array('f', _binning))
    #_hist = df.Histo1D(_hist_model, "dijetEvents.nPUTrue")
    #_hist = df.Histo1D(_hist_model, "karmaEvents.nPUTrue")
    _hist = df.Histo1D(_hist_model, "karmaEvent_karmaEvents__KARMASKIM.obj.nPUTrue")

    _f_out = ROOT.TFile(args.output_file, "RECREATE")
    _f_out.cd()
    _hist.Write()
    _f_out.Close()
