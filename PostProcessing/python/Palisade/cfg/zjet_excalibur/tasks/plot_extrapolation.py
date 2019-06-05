# -*- coding: utf8 -*-
import datetime
import itertools

from Karma.PostProcessing.Palisade import ContextValue, LiteralString, PlotProcessor, AnalyzeProcessor

from Karma.PostProcessing.Lumberjack.cfg.zjet_excalibur import SPLITTINGS, QUANTITIES
from Karma.PostProcessing.Palisade.cfg.zjet_excalibur import EXPANSIONS

from Karma.PostProcessing.Palisade.cfg.zjet_excalibur.jec_definitions import *

from matplotlib.font_manager import FontProperties

# def build_expression(source_type, quantity_x, quantity_y, run_period=None):
#     '''convenience function for putting together paths in input ROOT file'''
#     source_type = source_type.strip().lower()
#     assert source_type in ('data', 'mc')
#     if source_type == 'data':
#         return '"{0}_{{corr_level[{0}]}}:{1}/{{eta[name]}}/{y}/p_{x}_weight"'.format(source_type, run_period, x=quantity_x, y=quantity_y)
#     elif source_type == 'mc':
#         return '"{0}_{{corr_level[{0}]}}:MC/{{eta[name]}}/{y}/p_{x}_weight"'.format(source_type, x=quantity_x, y=quantity_y)

def build_expression(source_type, quantity_name, run_period=None ):
    """
    :param quantity_name:
    :return:
    convenience function for putting together paths in input ROOT file
    """
    if source_type == 'data':
        if run_period is None:
            print("Please enter a value for run_period!")
        else:
            return '"{0}_{{corr_level[{0}]}}:{1}/{{eta[name]}}/{{zpt[name]}}/{2}/p_alpha"'.format(source_type, run_period, quantity_name)
    elif source_type == 'mc':
        return '"{0}_{{corr_level[{0}]}}:MC/{{eta[name]}}/{{zpt[name]}}/{1}/p_alpha"'.format(source_type, quantity_name)
    else:
        print('incorrect source_type')

    # print('"data:{0}/{{eta[name]}}/{{zpt[name]}}/{1}/p_alpha"'.format(run_period, quantity_name))
    # return '"data:{0}/{{eta[name]}}/{{zpt[name]}}/{1}/h2d_alpha"'.format(run_period, quantity_name)


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


def get_config(channel, sample_name, jec_name, run_periods, quantities, corr_levels, colors, basename_mc, basename_data,
               output_format, testcase, root):

    # -- construct list of input files and correction level expansion dicts
    _input_files = dict()
    _corr_level_dicts = []
    for _cl in corr_levels:
        print (_cl)
        _input_files['data_{}'.format(_cl)] = "{}_Z{}_{}_{}_{}.root".format(
            basename_data, channel, sample_name, jec_name, _cl
        )

        # MC: lookup sample w/o residuals first
        _cl_for_mc = LOOKUP_MC_CORR_LEVEL.get(_cl, _cl)
        _input_files['mc_{}'.format(_cl)] = _input_files['mc_{}'.format(_cl_for_mc)] = "{}_Z{}_{}_{}_{}.root".format(
            basename_mc, channel, sample_name, jec_name, _cl_for_mc
        )

        _corr_level_dicts.append(
            dict(name=_cl, data=_cl, mc=_cl)
        )

    # _input_files['data'] = "{basename}_Z{channel}_{sample_name}_{jec_name}_{corr_level}.root".format(
    #     channel=channel,
    #     basename=basename_data,
    #     sample_name=sample_name,
    #     jec_name=jec_name,
    #     corr_level=corr_level
    # )


    alpha_min, alpha_max = SPLITTINGS['alpha_exclusive']['alpha_all']['alpha']
    alpha_max = 0.3

    # -- expansions
    if testcase:
        _expansions = {
            'corr_level' : _corr_level_dicts,
            'zpt': [
                # dict(name="zpt_gt_30", label=dict(zpt=(30, 100000))),
                # dict(name="zpt_30_50", label=dict(zpt=(30, 100000))),
                # dict(name="zpt_700_1500", label=dict(zpt=(30, 100000))),
                dict(name=_k, label="zpt_{}_{}".format("{:02d}".format(int(round(10 * _v['zpt'][0]))),
                                                       "{:02d}".format(int(round(10 * _v['zpt'][1])))))
                for _k, _v in SPLITTINGS['zpt'].iteritems()
            ],
            'eta': [
                dict(name="absEta_all", label=dict(absjet1eta=(0, 5.191))),
                # dict(name="absEta_0000_0522", label=dict(absjet1eta=(0, 5.191))),
                # dict(name="absEta_1305_1740", label=dict(absjet1eta=(0, 5.191))),
                # dict(name=_k, label="eta_{}_{}".format("{:02d}".format(int(round(10 * _v['absjet1eta'][0]))),
                #                                        "{:02d}".format(int(round(10 * _v['absjet1eta'][1])))))
                # for _k, _v in SPLITTINGS['eta_wide'].iteritems()
            ],
            'quantity': [
                dict(name=_quantity, label=_quantity) for _quantity in quantities
            ],
        }

    else:
        _expansions = {
            'corr_level': _corr_level_dicts,
            'zpt': [
                dict(name=_k, label="zpt_{}_{}".format("{:02d}".format(int(round(10 * _v['zpt'][0]))),
                                                       "{:02d}".format(int(round(10 * _v['zpt'][1])))))
                for _k, _v in SPLITTINGS['zpt'].iteritems()
            ],
            'eta': [
                dict(name=_k, label="eta_{}_{}".format("{:02d}".format(int(round(10 * _v['absjet1eta'][0]))),
                                                       "{:02d}".format(int(round(10 * _v['absjet1eta'][1])))))
                for _k, _v in SPLITTINGS['eta'].iteritems()
            ],
            'quantity': [
                dict(name=_quantity, label=_quantity) for _quantity in quantities
            ],
        }

    import pprint
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(_expansions)
    pp.pprint({_expansion_key: "{{{0}[name]}}".format(_expansion_key) for _expansion_key in _expansions.keys()})


    # append '[name]' to format keys that correspond to above expansion keys
    output_format = output_format.format(
        channel=channel,
        sample=sample_name,
        jec=jec_name,
        # corr_level = corr_levels,
        # get other possible replacements from expansions definition
        **{_expansion_key : "{{{0}[name]}}".format(_expansion_key) for _expansion_key in _expansions.keys()}
    )

    for _rp in EXPANSIONS['iov']:
        if _rp['name'] in run_periods:
            print(_rp['name'])

    return {
        'input_files': _input_files,
        'figures': [
            {
                'filename' : output_format,
                'subplots' : [
                    # Data
                    dict(
                        expression='{quantity}'.format(quantity=build_expression('data', _quantity, _rp['name'])),
                        label=r'{0} Data {1}'.format(_quantity, _rp['name']), plot_method='errorbar', color=_color, marker="o",
                        marker_style="full", pad=0)
                    # for _quantity, _color in zip(quantities, colors) for _rp in EXPANSIONS['iov'] if _rp['name'] in run_periods
                    for _quantity in quantities for _rp, _color in zip(EXPANSIONS['iov'],colors) if _rp['name'] in run_periods

                 ] + [
                    # MC
                    dict(
                        expression='{quantity}'.format(quantity=build_expression('mc', _quantity)),
                        label=r'MC', plot_method='errorbar', color="k", pad=0, zorder=-99, mask_zero_errors=True)
                        for _quantity in quantities
                ] + [
                        # Fit-results of Data values
                    dict(
                        expression='tgrapherror_from_poly1_fit({quantity}, 0., 0.3)'.format(quantity=build_expression("data", _quantity, run_period=_rp['name'])),
                        label=None, plot_method='step', show_yerr_as='band', color=_color, pad=0, mask_zero_errors=True,
                        zorder=-99)
                    for _quantity in quantities for _rp, _color in zip(EXPANSIONS['iov'], colors) if
                    _rp['name'] in run_periods
                ] + [
                     # Fit-results of  MC values
                     dict(
                         expression='tgrapherror_from_poly1_fit({quantity}, 0., 0.3)'.format(
                             quantity=build_expression("mc", _quantity)),
                         label=None, plot_method='step', show_yerr_as='band', color=_color, pad=0,
                         zorder=-99)
                    for _quantity in quantities

                ] + [
                    # Ratio Data/MC
                    dict(expression='{}/{}'.format(
                            build_expression('data', _quantity, run_period=_rp['name']),
                            build_expression('mc',_quantity)),
                         label=None, plot_method='errorbar', color=_color,
                         marker='o', marker_style="full", pad=1, mask_zero_errors=True)
                    for _quantity in quantities for _rp, _color in zip(EXPANSIONS['iov'], colors) if
                    _rp['name'] in run_periods

                ] + [
                    # Fit-results of Data values
                    dict(
                        expression='tgrapherror_from_poly1_fit({}/{}, 0., 0.3)'.format(
                            build_expression('data', _quantity, run_period=_rp['name']),
                            build_expression('mc', _quantity)),
                        label=None, plot_method='step', show_yerr_as='band', color=_color, pad=1, mask_zero_errors=True,
                        zorder=-99)
                           for _quantity in quantities for _rp, _color in zip(EXPANSIONS['iov'], colors) if
                           _rp['name'] in run_periods
                # ] + [
                #     # Ratio MC/MC (for displaying errors)
                #     dict(expression="{}/{}".format(
                #             build_expression('mc', _quantity),
                #             build_expression('mc', _quantity)),
                #          label=None, plot_method='errorbar', color='lightgray', pad=1, zorder=-99)
                #     for _quantity in quantities

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
                        'height_share': 3,
                        'x_range': [alpha_min, alpha_max],
                        # 'x_scale': '{quantity[scale]}',
                        'y_label': 'Jet Response',
                        'y_range': (0.5, 1.5),
                        # 'axvlines': ContextValue('quantity[expected_values]'),
                        'x_ticklabels': [],
                        'y_scale': 'linear',
                        'legend_kwargs': dict(loc='upper right'),
                    },
                    # ratio pad
                    {
                        'height_share': 1,
                        'x_label': 'Second-jet activity',
                        'x_range': [alpha_min, alpha_max],
                        # 'x_scale' : '{quantity[scale]}',
                        'y_label': 'JEC Data/MC',
                        'y_range': (0.75, 1.25),
                        'axhlines': [dict(values=[1.0])],
                        # 'axvlines': ContextValue('quantity[expected_values]'),
                        'y_scale': 'linear',
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
                    #         size=12,
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
    argument_parser.add_argument('-r', '--run-periods', help="names of the run periods, e.g. 'Run2018A'", required=True,
                                 nargs='+')
    argument_parser.add_argument('-c', '--channels', help="name of the JEC, e.g. 'Autumn18_JECV5'", nargs='+',
                                 default=['mm', 'ee'], choices=['mm', 'ee'], metavar="CHANNEL")
    argument_parser.add_argument('-l', '--corr-levels', help="name of the JEC correction levels to include, e.g. 'L1L2L3'",
                                 nargs='+', choices=['L1', 'L1L2L3', 'L1L2L3Res', 'L1L2Res'], metavar="CORR_LEVEL")

    argument_parser.add_argument('-q', '--quantities', help="quantities to plot", nargs='+',
                                 metavar="QUANTITY")
    argument_parser.add_argument('-f', '--colors', help="colors of quantities to plot", nargs='+', metavar="COLOR")
    argument_parser.add_argument('--basename-data', help="prefix of ROOT files containing Data histograms",
                                 required=True)
    argument_parser.add_argument('--basename-mc', help="prefix of ROOT files containing MC histograms", required=True)
    # optional parameters
    argument_parser.add_argument('--output-format', help="format string indicating full path to output plot",
                                 default='JEC_Extrapolations_Z{channel}_{jec}_{sample}_{corr_level}/{zpt}-{eta}.pdf')
    argument_parser.add_argument('--test', help="plot only one plot for testing configuration", dest='test',
                                 action='store_true')
    argument_parser.add_argument('--root', help="Switch output to root files instead of plots ", dest='root',
                                 action='store_true')

def run(args):


    if args.output_dir is None:
        args.output_dir = "plots_{}".format(datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%f"))

    # # make quantity pair tuples from list of colon-separated specifications
    # _quantity_pairs = []
    # for _qp in args.quantity_pairs:
    #     if ':' not in _qp:
    #         raise ValueError("Invalid quantity pair specification: '{}'. Valid format: '{{x_quantity}}:{{y_quantity}}'".format(_qp))
    #     _qx, _qy = _qp.split(':', 1)
    #     if _qx not in QUANTITIES['global']:
    #         raise ValueError("Unknown `x` quantity requested: '{}'".format(_qx))
    #     _quantity_pairs.append((_qx, _qy))

    for channel in args.channels:
        print "Making plots for channel '{}'...".format(channel)
        _cfg = get_config(
            channel=channel,
            sample_name=args.sample,
            jec_name=args.jec,
            corr_levels=args.corr_levels,
            run_periods=args.run_periods,
            # quantities=(args.quantities if args.quantities else ['ptbalance-data', 'ptbalance-mc', 'pli-mc', 'zres-mc', 'jer-gen-mc']),
            quantities=args.quantities,
            colors=(args.colors if args.colors else ['grey', 'royalblue', 'springgreen', 'forestgreen', 'orange']),
            basename_mc=args.basename_mc,
            basename_data=args.basename_data,
            output_format=(args.output_format if not args.root else 'JEC_Extrapolations_Z{channel}_{jec}_{sample}_{corr_level}.root'),
            testcase = (args.test if args.test else False),
            root = (args.root if args.root else False),
        )
        import pprint
        pp = pprint.PrettyPrinter(indent=2)
        pp.pprint(_cfg)
        p = PlotProcessor(_cfg, output_folder=args.output_dir)
        p.run()
