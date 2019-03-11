# -*- coding: utf8 -*-
import datetime
import itertools

from Karma.PostProcessing.Palisade import ContextValue, LiteralString, PlotProcessor

from Karma.PostProcessing.Lumberjack.cfg.zjet_excalibur import SPLITTINGS, QUANTITIES
from Karma.PostProcessing.Palisade.cfg.zjet_excalibur import EXPANSIONS

from matplotlib.font_manager import FontProperties

def build_expression(source_type, quantity_name, run_period=None):
    '''convenience function for putting together paths in input ROOT file'''
    source_type = source_type.strip().lower()
    assert source_type in ('data', 'mc')
    if source_type == 'data':
        return '"{0}_{{corr_level[{0}]}}:{1}/{{eta[name]}}/h_{2}_weight"'.format(source_type, run_period, quantity_name)
    elif source_type == 'mc':
        return '"{0}_{{corr_level[{0}]}}:MC/{{eta[name]}}/h_{1}_weight"'.format(source_type, quantity_name)


LOOKUP_MC_CORR_LEVEL = {
    'L1L2Res' : 'L1L2L3',
    'L1L2L3Res' : 'L1L2L3',
}
LOOKUP_CHANNEL_LABEL = {
    'mm' : r'Z$\rightarrow\mathrm{{\bf \mu\mu}}$',
    'ee' : r'Z$\rightarrow\mathrm{{\bf ee}}$',
}


def get_config(channel, sample_name, jec_name, run_periods, quantities,
               corr_levels,
               basename_data,
               basename_mc,
               output_format):

    # -- construct list of input files and correction level expansion dicts
    _input_files = dict()
    _corr_level_dicts = []
    for _cl in corr_levels:
        _input_files['data_{}'.format(_cl)] = "{}_Z{}_{}_{}_{}.root".format(
            basename_data, channel, sample_name, jec_name, _cl
        )

        # MC: lookup sample w/o residuals first
        _cl_for_mc = LOOKUP_MC_CORR_LEVEL.get(_cl, _cl)
        _input_files['mc_{}'.format(_cl)] = _input_files['mc_{}'.format(_cl_for_mc)] = "{}_Z{}_{}_{}_{}.root".format(
            basename_mc, channel, sample_name, jec_name, _cl_for_mc
        )

        _corr_level_dicts.append(
            dict(name=_cl, data=_cl, mc=_cl_for_mc)
        )

    # raise exception if quantities specified are unknown
    _unknown_quantities = set(quantities).difference(QUANTITIES['global'].keys())
    if _unknown_quantities:
        raise ValueError("Unknown quantities: {}".format(', '.join(_unknown_quantities)))

    # -- expansions
    _expansions = {
        'corr_level' : _corr_level_dicts,
        'eta' : [
            dict(name=_k, label=r"${}\leq|\eta^{{\mathrm{{jet1}}}}|<{}$".format(_v['absjet1eta'][0], _v['absjet1eta'][1]))
            for _k, _v in SPLITTINGS['eta_wide_barrel'].iteritems()
        ],
        'quantity' : [
            _q_dict
            for _q_dict in EXPANSIONS['quantity']
            if _q_dict['name'] in quantities
        ]
    }

    # append '[name]' to format keys that correspond to above expansion keys
    output_format = output_format.format(
        channel=channel,
        sample=sample_name,
        jec=jec_name,
        # get other possible replacements from expansions definition
        **{_expansion_key : "{{{0}[name]}}".format(_expansion_key) for _expansion_key in _expansions.keys()}
    )

    return {
        'input_files': _input_files,
        'figures': [
            {
                'filename' : output_format,
                'subplots' : [
                    # Data
                    dict(
                        expression='normalize_to_ref({}, {})'.format(
                            build_expression('data', "{quantity[name]}", run_period=_rp['name']),
                            build_expression('mc', "{quantity[name]}")),
                        label=r'Data ({})'.format(_rp['name']), plot_method='errorbar', color=_rp['color'],
                        marker="o", marker_style="full", pad=0)
                    for _rp in EXPANSIONS['run'] if _rp['name'] in run_periods
                ] + [
                    # MC
                    dict(expression='discard_errors({})'.format(build_expression('mc', "{quantity[name]}")),
                         label=r'MC', plot_method='bar', color="lightgray", pad=0, zorder=-99, alpha=0.5)
                ] + [
                    # Ratio Data/MC
                    dict(expression="({})/({})".format(
                            'normalize_to_ref({}, {})'.format(
                                build_expression('data', "{quantity[name]}", run_period=_rp['name']),
                                build_expression('mc', "{quantity[name]}")),
                            build_expression('mc', "{quantity[name]}")
                         ),
                         label=None, plot_method='errorbar', color=_rp['color'],
                         marker='o', marker_style="full", pad=1)
                     for _rp in EXPANSIONS['run'] if _rp['name'] in run_periods
                ] + [
                    # Ratio MC/MC (for displaying errors)
                    dict(expression="({})/discard_errors({})".format(
                            build_expression('mc', "{quantity[name]}"),
                            build_expression('mc', "{quantity[name]}")),
                         label=None, plot_method='step', show_yerr_as='band', color='lightgray', pad=1, zorder=-99)
                ],
                'pad_spec' : {
                    'right': 0.95,
                    'bottom': 0.15,
                    'top': 0.925,
                    'hspace': 0.075,
                },
                'pads': [
                    # top pad
                    {
                        'height_share' : 3,
                        'x_range' : ContextValue('quantity[range]'),
                        'x_scale' : '{quantity[scale]}',
                        'y_label' : 'arb. units',
                        #'y_range' : (1e-3, 1e9),
                        'axvlines' : ContextValue('quantity[expected_values]'),
                        'x_ticklabels' : [],
                        'y_scale' : 'linear',
                        'legend_kwargs': dict(loc='upper right'),
                    },
                    # ratio pad
                    {
                        'height_share' : 1,
                        'x_label' : '{quantity[label]}',
                        'x_range' : ContextValue('quantity[range]'),
                        'x_scale' : '{quantity[scale]}',
                        'y_label' : 'Data/MC',
                        'y_range' : (0.8, 1.2),
                        'axhlines' : [1.0],
                        'axvlines' : ContextValue('quantity[expected_values]'),
                        'y_scale' : 'linear',
                        'legend_kwargs': dict(loc='upper right'),
                    },
                ],
                'texts' : [
                    dict(xy=(.04, 1.0 - .15*0.75), text=LOOKUP_CHANNEL_LABEL.get(channel, channel), transform='axes',
                        fontproperties=FontProperties(
                            weight='bold',
                            family='Nimbus Sans',
                            size=12,
                        )),
                    dict(xy=(.04, 1.0 - .25*0.75), text="{corr_level[data]}", transform='axes',
                        fontproperties=FontProperties(
                            weight='bold',
                            family='Nimbus Sans',
                            size=12,
                        )),
                    dict(xy=(.04, 1.0 - .35*0.75), text="$\\alpha<0.3$", transform='axes'),
                    dict(xy=(.04, 1.0 - .45*0.75), text="{eta[label]}", transform='axes'),
                ],
                'upper_label' : jec_name,
            },
        ],
        'expansions' : _expansions
    }


def cli(argument_parser):
    '''command-line interface. builds on an existing `argparse.ArgumentParser` instance.'''

    # define CLI arguments
    argument_parser.add_argument('-s', '--sample', help="name of the sample, e.g. '17Sep2018'", required=True)
    argument_parser.add_argument('-j', '--jec', help="name of the JEC, e.g. 'Autumn18_JECV5'", required=True)
    argument_parser.add_argument('-r', '--run-periods', help="names of the run periods, e.g. 'Run2018A'", required=True, nargs='+')
    argument_parser.add_argument('-c', '--channels', help="name of the JEC, e.g. 'Autumn18_JECV5'", nargs='+', default=['mm', 'ee'], choices=['mm', 'ee'], metavar="CHANNEL")
    argument_parser.add_argument('-l', '--corr-levels', help="name of the JEC correction levels to include, e.g. 'L1L2L3'", nargs='+', choices=['L1', 'L1L2L3', 'L1L2L3Res', 'L1L2Res'], metavar="CORR_LEVEL")
    argument_parser.add_argument('-q', '--quantities', help="quantities to plot", nargs='+', choices=QUANTITIES['global'].keys(), metavar="QUANTITY")
    argument_parser.add_argument('--basename-data', help="prefix of ROOT files containing Data histograms", required=True)
    argument_parser.add_argument('--basename-mc', help="prefix of ROOT files containing MC histograms", required=True)
    # optional parameters
    argument_parser.add_argument('--output-format', help="format string indicating full path to output plot", default='Shapes/{jec}/{sample}/{corr_level}/{channel}/{eta}/{quantity}.png')


def run(args):

    if args.output_dir is None:
        args.output_dir = "plots_{}".format(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%f"))

    for channel in args.channels:
        print "Making plots for channel '{}'...".format(channel)
        _cfg = get_config(
            channel=channel,
            sample_name=args.sample,
            jec_name=args.jec,
            corr_levels=args.corr_levels,
            run_periods=args.run_periods,
            quantities=args.quantities,
            basename_data=args.basename_data,
            basename_mc=args.basename_mc,
            output_format=args.output_format)
        p = PlotProcessor(_cfg, output_folder=args.output_dir)
        p.run()
