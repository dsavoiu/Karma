# -*- coding: utf8 -*-
import datetime
import itertools

from Karma.PostProcessing.Palisade import ContextValue, LiteralString, PlotProcessor

from Karma.PostProcessing.Lumberjack.cfg.zjet_excalibur import SPLITTINGS, QUANTITIES
from Karma.PostProcessing.Palisade.cfg.zjet_excalibur import EXPANSIONS

from matplotlib.font_manager import FontProperties

def build_expression(source_type, quantity_x, quantity_y, run_period=None):
    '''convenience function for putting together paths in input ROOT file'''
    source_type = source_type.strip().lower()
    assert source_type in ('data', 'mc')
    if source_type == 'data':
        return '"{0}_{{corr_level[{0}]}}:{1}/{{eta[name]}}/{y}/p_{x}_weight"'.format(source_type, run_period, x=quantity_x, y=quantity_y)
    elif source_type == 'mc':
        return '"{0}_{{corr_level[{0}]}}:MC/{{eta[name]}}/{y}/p_{x}_weight"'.format(source_type, x=quantity_x, y=quantity_y)


LOOKUP_MC_CORR_LEVEL = {
    'L1L2Res' : 'L1L2L3',
    'L1L2L3Res' : 'L1L2L3',
}
LOOKUP_CHANNEL_LABEL = {
    'mm' : r'Z$\rightarrow\mathrm{{\bf \mu\mu}}$',
    'ee' : r'Z$\rightarrow\mathrm{{\bf ee}}$',
}
LOOKUP_QUANTITY_EXPANSION = {}
for _q in EXPANSIONS['quantity']:
    LOOKUP_QUANTITY_EXPANSION[_q['name']] = _q


def get_config(channel, sample_name, jec_name, run_periods, quantity_pairs,
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

    # raise exception if specified x or y quantities are unknown
    _unknown_quantities = set([qp[0] for qp in quantity_pairs]).difference(QUANTITIES['global'].keys()).union(
                          set([qp[1] for qp in quantity_pairs]).difference(QUANTITIES['global'].keys()))
    if _unknown_quantities:
        raise ValueError("Unknown quantities: {}".format(', '.join(_unknown_quantities)))

    # -- expansions
    _expansions = {
        'corr_level' : _corr_level_dicts,
        'eta' : [
            dict(name=_k, label=r"${}\leq|\eta^{{\mathrm{{jet1}}}}|<{}$".format(_v['absjet1eta'][0], _v['absjet1eta'][1]))
            for _k, _v in SPLITTINGS['eta_wide_barrel'].iteritems()
        ],
        'quantity_pair' : [
            dict(
                {   'y_'+_k : _v
                    for _k ,_v in LOOKUP_QUANTITY_EXPANSION[_qy].iteritems()
                },
                name="{}_vs_{}".format(_qy, _qx),
                **{   'x_'+_k : _v
                    for _k ,_v in LOOKUP_QUANTITY_EXPANSION[_qx].iteritems()
                }
            )
            for _qx, _qy in quantity_pairs
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
                        expression=build_expression('data', "{quantity_pair[x_name]}", "{quantity_pair[y_name]}", run_period=_rp['name']),
                        label=r'Data ({})'.format(_rp['name']), plot_method='errorbar', color=_rp['color'],
                        marker="o", marker_style="full", pad=0, mask_zero_errors=True)
                    for _rp in EXPANSIONS['run'] if _rp['name'] in run_periods
                ] + [
                    # MC
                    dict(
                        expression=build_expression('mc', "{quantity_pair[x_name]}", "{quantity_pair[y_name]}"),
                        label=r'MC', plot_method='errorbar', color="k", pad=0, zorder=-99, mask_zero_errors=True)
                ] + [
                    # Ratio Data/MC
                    dict(expression="h({})/h({})".format(
                            build_expression('data', "{quantity_pair[x_name]}", "{quantity_pair[y_name]}", run_period=_rp['name']),
                            build_expression('mc', "{quantity_pair[x_name]}", "{quantity_pair[y_name]}")),
                         label=None, plot_method='errorbar', color=_rp['color'],
                         marker='o', marker_style="full", pad=1, mask_zero_errors=True)
                     for _rp in EXPANSIONS['run'] if _rp['name'] in run_periods
                ] + [
                    # Ratio MC/MC (for displaying errors)
                    dict(expression="h({})/discard_errors(h({}))".format(
                            build_expression('mc', "{quantity_pair[x_name]}", "{quantity_pair[y_name]}"),
                            build_expression('mc', "{quantity_pair[x_name]}", "{quantity_pair[y_name]}")),
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
                        'x_range' : ContextValue('quantity_pair[x_range]'),
                        'x_scale' : '{quantity_pair[x_scale]}',
                        'y_label' : '{quantity_pair[y_label]}',
                        'y_range' : ContextValue('quantity_pair[y_profile_range]'),
                        'x_ticklabels' : [],
                        'axhlines' : ContextValue('quantity_pair[y_expected_values]'),
                        'y_scale' : 'linear',
                        'legend_kwargs': dict(loc='upper right'),
                    },
                    # ratio pad
                    {
                        'height_share' : 1,
                        'x_label' : '{quantity_pair[x_label]}',
                        'x_range' : ContextValue('quantity_pair[x_range]'),
                        'x_scale' : '{quantity_pair[x_scale]}',
                        'y_label' : 'Data/MC',
                        'y_range' : (0.85, 1.15),
                        'axhlines' : [1.0],
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
    argument_parser.add_argument('-q', '--quantity-pairs', help="pairs of quantities to plot. Format: '{x_quantity}:{y_quantity}'", nargs='+', metavar="QUANTITY_PAIR")
    argument_parser.add_argument('--basename-data', help="prefix of ROOT files containing Data histograms", required=True)
    argument_parser.add_argument('--basename-mc', help="prefix of ROOT files containing MC histograms", required=True)
    # optional parameters
    argument_parser.add_argument('--output-format', help="format string indicating full path to output plot", default='Profiles/{jec}/{sample}/{corr_level}/{channel}/{eta}/{quantity_pair}.png')


def run(args):

    if args.output_dir is None:
        args.output_dir = "plots_{}".format(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%f"))

    # make quantity pair tuples from list of colon-separated specifications
    _quantity_pairs = []
    for _qp in args.quantity_pairs:
        if ':' not in _qp:
            raise ValueError("Invalid quantity pair specification: '{}'. Valid format: '{{x_quantity}}:{{y_quantity}}'".format(_qp))
        _qx, _qy = _qp.split(':', 1)
        if _qx not in QUANTITIES['global']:
            raise ValueError("Unknown `x` quantity requested: '{}'".format(_qx))
        _quantity_pairs.append((_qx, _qy))

    for channel in args.channels:
        print "Making plots for channel '{}'...".format(channel)
        _cfg = get_config(
            channel=channel,
            sample_name=args.sample,
            jec_name=args.jec,
            corr_levels=args.corr_levels,
            run_periods=args.run_periods,
            quantity_pairs=_quantity_pairs,
            basename_data=args.basename_data,
            basename_mc=args.basename_mc,
            output_format=args.output_format)
        p = PlotProcessor(_cfg, output_folder=args.output_dir)
        p.run()
