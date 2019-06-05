import ROOT
import numpy as np

from array import array
from rootpy import asrootpy
import root_numpy

from Karma.PostProcessing.Palisade import InputROOT
from Karma.PostProcessing.Palisade._input import _ROOTObjectFunctions

from termcolor import colored


@InputROOT.add_function
def poly1_fit(tobject, x_min, x_max):
    # new_tobject = _ROOTObjectFunctions._project_or_clone(tobject, "e")
    _skip = True
    _parameter = [0., 0.]
    _parameter_errors = [0., 0.]
    if len(root_numpy.hist2array(tobject, include_overflow=False, copy=True, return_edges=False)[:-1]) < 3:
        print(colored("WARNING: Skipping histogram due to low statistic! Setting parameters to zero!", "yellow"))
    else:
        _fit = ROOT.TF1('fit_function', "[0]+[1]*x", x_min, x_max)
        _fit.SetParameters(0., 0.)
        _fit.SetParNames("m", "c")
        # fit.SetParLimits(0, 1. - 0.01 * 1., 1. + 0.01 * 1.)
        # fit.SetParLimits(1, 1. - 0.01 * 1., 1. + 0.01 * 1.)
        _results = tobject.Fit(_fit, 'S', '', x_min, x_max)
        # Check if TFitResult is not empty by testing if TFitResultPtr is not -1
        if int(_results) >= 0:
            _skip = False
            _parameter = _fit.GetParameters()
            _parameter_errors = _fit.GetParErrors()
        else:
            print(colored("WARNING: Skipping fit due to empty fit results! Setting parameters to zero!", "yellow"))
    return _skip, _parameter, _parameter_errors


#
# @InputROOT.add_function
# def histogram_from_linear_extrapolation(tobjects, x_bins, x_min, x_max):
#     """
#     :param tobjects:
#     :param x_bins:
#     :param x_min:
#     :param x_max:
#     :return:
#     Create new histogram from fitted parameters of a
#     """
#     # create binning for histogram
#     x_binning = [min([x[0] for x in x_bins])] + sorted([x[1] for x in x_bins])
#     # x_min = min([x[0] for x in x_bins])
#     # x_max = max([x[1] for x in x_bins])
#     # clone tobjects to avoid data corruption
#     _tobjects = []
#     for _tobject in tobjects:
#         _tobjects.append(_ROOTObjectFunctions._project_or_clone(_tobject, "e"))
#     # create new histogram to fill results into
#     _new_tobject = ROOT.TH1D("hist_rms_", "hist_rms", len(_tobjects), array('d',x_binning))
#     # access x_axis of new histogram for bin by bin access
#     _x_axis = _new_tobject.GetXaxis()
#     # Fit function to each histogram
#     for index, (_tobject, x_bin) in enumerate(zip(_tobjects, x_bins)):
#         _bin_index = _x_axis.FindBin((x_bin[0]+x_bin[1])/2.)
#         skip, _parameter, _parameter_errors = poly1_fit(_tobject, x_min, x_max)
#         _new_tobject.SetBinContent(_bin_index, _parameter[0])
#         _new_tobject.SetBinError(_bin_index, _parameter_errors[0])
#         print('Linear extrapolation to {} +/- {}'.format(_parameter[0], _parameter_errors[0]))
#     return asrootpy(_new_tobject)

@InputROOT.add_function
def tgrapherror_from_poly1_fit(tobject, x_min, x_max):
    _tobject = _ROOTObjectFunctions._project_or_clone(tobject, "e")
    sampling_points = 100
    _confidence_interval = ROOT.TGraphErrors(sampling_points)
    for _bin_index, x_value in enumerate(np.arange(x_min, x_max, (float(x_max) - float(x_min)) / sampling_points)):
        _confidence_interval.SetPoint(_bin_index, x_value, 0)
        _confidence_interval.SetPointError(_bin_index, 0., 0)
    skip, _parameter, _parameter_errors = poly1_fit(_tobject, x_min, x_max)
    if not skip:
        ROOT.TVirtualFitter.GetFitter().GetConfidenceIntervals(_confidence_interval, 0.683)
    return asrootpy(_confidence_interval)
