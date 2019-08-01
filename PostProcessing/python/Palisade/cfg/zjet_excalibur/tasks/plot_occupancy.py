# -*- coding: utf8 -*-
import numpy as np
import datetime
import itertools

from Karma.PostProcessing.Palisade import ContextValue, LiteralString, PlotProcessor

from Karma.PostProcessing.Lumberjack.cfg.zjet_excalibur import SPLITTINGS, QUANTITIES
from Karma.PostProcessing.Palisade.cfg.zjet_excalibur import EXPANSIONS

from matplotlib.font_manager import FontProperties
import matplotlib.colors as colors


class MidpointNormalize(colors.Normalize):
    """
    Colormap normalization for ensuring that the midpoint of the colormap is mapped to a particular value.
    """
    def __init__(self, midpoint, **kwargs):
        self._midpoint = midpoint
        super(MidpointNormalize, self).__init__(**kwargs)

    def __call__(self, value, clip=None):
        _absmax = max(abs(self.vmin or 0.0), abs(self.vmax or 0.0))
        x, y = [-_absmax, self._midpoint, _absmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y), np.isnan(value))


def build_expression(source_type, quantity_x, quantity_y, run_period=None):
    '''convenience function for putting together paths in input ROOT file'''
    source_type = source_type.strip().lower()
    assert source_type in ('data', 'mc', 'ratio', 'diff', 'asymm')

    if source_type == 'ratio':
        return "({0})/normalize_to_ref({1}, {0})".format(
            build_expression('data', quantity_x, quantity_y, run_period=run_period),
            build_expression('mc', quantity_x, quantity_y, run_period=run_period),
        )
    elif source_type == 'diff':
        return "(normalize_to_ref({0}, {1}) - {1})/({1})".format(
            build_expression('data', quantity_x, quantity_y, run_period=run_period),
            build_expression('mc', quantity_x, quantity_y, run_period=run_period),
        )
    elif source_type == 'asymm':
        return "(normalize_to_ref({0}, {1}) - {1})/(normalize_to_ref({0}, {1}) + {1})".format(
            build_expression('data', quantity_x, quantity_y, run_period=run_period),
            build_expression('mc', quantity_x, quantity_y, run_period=run_period),
        )

    _top_splitting_name = run_period if source_type == 'data' else 'MC'

    return '"{0}_{{corr_level[{0}]}}:{1}/{{split[name]}}/{y}/h2d_{x}_weight"'.format(
        source_type, _top_splitting_name,
        x=quantity_x, y=quantity_y)


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


def get_config(channel, sample_name, jec_name, run_periods, quantity_pairs, split_quantity,
               corr_levels,
               source_types,
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
            dict(name=_cl, data=_cl, mc=_cl_for_mc, ratio=_cl, diff=_cl, asymm=_cl)
        )

    # raise exception if specified x or y quantities are unknown
    _unknown_quantities = set([qp[0] for qp in quantity_pairs]).difference(QUANTITIES['global'].keys()).union(
                          set([qp[1] for qp in quantity_pairs]).difference(QUANTITIES['global'].keys()))
    if _unknown_quantities:
        raise ValueError("Unknown quantities: {}".format(', '.join(_unknown_quantities)))

    # -- expansions
    _expansions = {
        'corr_level' : _corr_level_dicts,
        'run_period' : [_rp for _rp in EXPANSIONS['iov'] if _rp['name'] in run_periods],
        'source' : [dict(name='{source}')],  # dummy expansion to pass through source type
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

    if split_quantity == 'eta':
        _expansions.update({'split' : [
            dict(name=_k+'/zpt_gt_30', label=r"${}\leq|\eta^{{\mathrm{{jet1}}}}|<{}$".format(_v['absjet1eta'][0], _v['absjet1eta'][1]))
            for _k, _v in SPLITTINGS['eta_wide_barrel'].iteritems()]})
    elif split_quantity == 'zpt':
        _expansions.update({'split' : [
            dict(name='absEta_0000_1300/'+_k, label=r"${}\leq p_{{\mathrm{{T}}}}^{{\mathrm{{Z}}}}/\mathrm{{GeV}}<{}$".format(_v['zpt'][0], _v['zpt'][1]))
            for _k, _v in SPLITTINGS['zpt'].iteritems()]})
    elif split_quantity is None:
        _expansions['split'] = [
            dict(name='absEta_0000_1300/zpt_gt_30', label=r"$p_{{\mathrm{{T}}}}^{{\mathrm{{Z}}}}\geq30 \mathrm{{GeV}}$, $|\eta^{{\mathrm{{jet1}}}}|<1.3$"),
            dict(name='absEta_all/zpt_gt_30', label=r"$p_{{\mathrm{{T}}}}^{{\mathrm{{Z}}}}\geq30 \mathrm{{GeV}}$"),
        ]
    else:
        print('[ERROR] Expansions not implemented for split quantity {}!'.format(split_quantity))


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
                'filename' : output_format.replace('{source[name]}', _source_type),
                'subplots' : [
                    dict(
                        expression=build_expression(_source_type, "{quantity_pair[x_name]}", "{quantity_pair[y_name]}",
                            run_period='{run_period[name]}'),
                        plot_method='pcolormesh',
                        cmap='RdBu' if _source_type in ('ratio', 'diff', 'asymm') else 'viridis',
                        norm=(
                            MidpointNormalize(midpoint=1.0) if _source_type == 'ratio' else
                            MidpointNormalize(midpoint=0.0) if _source_type == 'diff' else None),
                        vmin=(
                            0  if _source_type == 'ratio' else
                            -1 if _source_type == 'asymm' else
                            -1 if _source_type == 'diff' else None),
                        vmax=(
                            2  if _source_type == 'ratio' else
                            1  if _source_type == 'asymm' else
                            1  if _source_type == 'diff' else None),
                    )
                ],
                'pad_spec' : {
                    'right': 0.95,
                    'bottom': 0.15,
                    'top': 0.925,
                    'hspace': 0.075,
                },
                'pads': [
                    {
                        'x_label' : '{quantity_pair[x_label]}',
                        'x_range' : ContextValue('quantity_pair[x_range]'),
                        'x_scale' : '{quantity_pair[x_scale]}',
                        'y_label' : '{quantity_pair[y_label]}',
                        'y_range' : ContextValue('quantity_pair[y_range]'),
                        'y_scale' : 'linear',
                        'z_label' : 'Data/MC' if _source_type == 'ratio' else
                                    '(Data-MC)/MC' if _source_type == 'diff' else 
                                    '(Data-MC)/(Data+MC)' if _source_type == 'asymm' else 'arb. units',
                        'z_labelpad' : 25,
                        'axhlines' : [dict(values=ContextValue('quantity_pair[y_expected_values]'))],
                        'legend_kwargs': dict(loc='upper right'),
                    }
                ],
                'texts' : [
                    dict(xy=(.04, 1.0 - .15*0.75), text=LOOKUP_CHANNEL_LABEL.get(channel, channel), transform='axes',
                        fontproperties=FontProperties(
                            weight='bold',
                            family='Nimbus Sans',
                            size=12,
                        )),
                    dict(xy=(.04, 1.0 - .25*0.75), text="{corr_level["+_source_type+"]}", transform='axes',
                        fontproperties=FontProperties(
                            weight='bold',
                            family='Nimbus Sans',
                            size=12,
                        )),
                    dict(xy=(.04, 1.0 - .35*0.75), text="$\\alpha<0.3$", transform='axes'),
                    dict(xy=(.04, 1.0 - .45*0.75), text="{split[label]}", transform='axes'),
                ],
                'upper_label' : jec_name,
            }
            for _source_type in source_types
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
    argument_parser.add_argument('--source-types', help="sources to use for plots", nargs='+', default=['data', 'mc', 'asymm'], choices=('data', 'mc', 'diff', 'asymm'))
    argument_parser.add_argument('--split-quantity', help='split quantity, eta or zpt', choices=['eta', 'zpt'], default=None)
    argument_parser.add_argument('--output-format', help="format string indicating full path to output plot",
                                 default='Profiles/{jec}/{sample}/{corr_level}/{channel}/{split}/{quantity_pair}_{source}.png')

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
            split_quantity=args.split_quantity,
            source_types=args.source_types,
            basename_data=args.basename_data,
            basename_mc=args.basename_mc,
            output_format=args.output_format)
        p = PlotProcessor(_cfg, output_folder=args.output_dir)
        p.run()
