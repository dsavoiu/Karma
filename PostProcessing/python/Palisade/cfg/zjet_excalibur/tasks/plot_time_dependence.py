# -*- coding: utf8 -*-
import datetime
import itertools

from Karma.PostProcessing.Palisade import ContextValue, LiteralString, PlotProcessor

from Karma.PostProcessing.Lumberjack.cfg.zjet_excalibur import SPLITTINGS, QUANTITIES
from Karma.PostProcessing.Palisade.cfg.zjet_excalibur import EXPANSIONS

from matplotlib.font_manager import FontProperties

def build_expression(source_type, run_period, time_quantity, quantity):
    '''convenience function for putting together paths in input ROOT file'''
    source_type = source_type.strip().lower()
    assert source_type in ('data', 'mc')
    if source_type == 'data':
        return '"{0}_{{corr_level[{0}]}}:{1}/{{eta[name]}}/{y}/p_{x}"'.format(source_type, run_period, x=time_quantity, y=quantity)
    elif source_type == 'mc':
        raise ValueError("Cannot build time dependence expression for MC!")


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


def get_config(channel, sample_name, jec_name, time_quantity, run_periods, quantities,
               corr_levels,
               basename,
               output_format):

    # -- construct list of input files and correction level expansion dicts
    _input_files = dict()
    _corr_level_dicts = []
    for _cl in corr_levels:
        _input_files['data_{}'.format(_cl)] = "{}_Z{}_{}_{}_{}.root".format(
            basename, channel, sample_name, jec_name, _cl
        )

        _corr_level_dicts.append(
            dict(name=_cl, data=_cl)
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
            LOOKUP_QUANTITY_EXPANSION[_qy]
            for _qy in quantities
        ],
        'time_quantity' : [
            LOOKUP_QUANTITY_EXPANSION[_qy]
            for _qy in [time_quantity]
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
                        expression=build_expression('data', _rp['name'], time_quantity, "{quantity[name]}"),
                        label=r'Data ({})'.format(_rp['name']), plot_method='errorbar', color=_rp['color'],
                        marker="o", marker_style="full", mask_zero_errors=True)
                    for _rp in EXPANSIONS[time_quantity] if _rp['name'] in run_periods
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
                        'x_range' : ContextValue('time_quantity[range]'),
                        'x_scale' : 'linear',
                        'x_label' : '{time_quantity[label]}',
                        'y_label' : '{quantity[label]}',
                        'y_scale' : 'linear',
                        'y_range' : ContextValue('quantity[uniform_range]'),
                        'legend_kwargs': dict(loc='upper right'),
                        #'axhlines' : [1.0],
                    },
                ],
                'texts' : [
                    dict(xy=(.04, 1.0 - .1*0.8), text=LOOKUP_CHANNEL_LABEL.get(channel, channel), transform='axes',
                        fontproperties=FontProperties(
                            weight='bold',
                            family='Nimbus Sans',
                            size=12,
                        )),
                    dict(xy=(.04, 1.0 - .2*0.8), text="{corr_level[data]}", transform='axes',
                        fontproperties=FontProperties(
                            weight='bold',
                            family='Nimbus Sans',
                            size=12,
                        )),
                    dict(xy=(.04, 1.0 - .3*0.8), text="$\\alpha<0.3$", transform='axes'),
                    dict(xy=(.04, 1.0 - .4*0.8), text="{eta[label]}", transform='axes'),
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
    argument_parser.add_argument('-q', '--quantities', help="quantities to plot.", nargs='+', metavar="QUANTITY")
    argument_parser.add_argument('-x', '--time-quantity', help="quantity to interpret as time (on x axis)", metavar="TIME_QUANTITY")
    argument_parser.add_argument('--basename', help="prefix of ROOT files containing time dependence profiles", required=True)
    # optional parameters
    argument_parser.add_argument('--output-format', help="format string indicating full path to output plot", default='TimeDependence/{jec}/{sample}/{corr_level}/{channel}/{eta}/{quantity}_vs_{time_quantity}.png')


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
            time_quantity=args.time_quantity,
            quantities=args.quantities,
            basename=args.basename,
            output_format=args.output_format)
        p = PlotProcessor(_cfg, output_folder=args.output_dir)
        p.run()
