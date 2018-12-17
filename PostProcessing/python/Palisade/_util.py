"""
module fragment containing some useful functions
"""

from ._definitions import EXPANSIONS
from .Processors import ContextValue, LiteralString

from matplotlib.font_manager import FontProperties
from matplotlib.colors import SymLogNorm


__all__ = ['xs_expression', 'xs_expression_mc', 'FIGURE_TEMPLATES', 'FONTPROPERTIES', 'TEXTS', 'ANALYZE_TASK_TEMPLATES']


_max_te = 'max(' + ', '.join([
    '"te:{ybys[name]}/'+_tpi['name']+'/jet1HLTAssignedPathEfficiency/p_{quantity[name]}"'
    for _tpi in EXPANSIONS['trigger']
    if _tpi['name'] != "all"
]) + ')'

_max_yield_99 = 'max(' + ', '.join([
    '"ey:{ybys[name]}/'+_tpi['name']+'/h_{quantity[name]}" * threshold("te:{ybys[name]}/'+_tpi['name']+'/jet1HLTAssignedPathEfficiency/p_{quantity[name]}", 0.99)'
    for _tpi in EXPANSIONS['trigger']
    if _tpi['name'] != "all"
]) + ')'

_max_te_99 = 'max(' + ', '.join([
    'h("te:{ybys[name]}/'+_tpi['name']+'/jet1HLTAssignedPathEfficiency/p_{quantity[name]}") * threshold("te:{ybys[name]}/'+_tpi['name']+'/jet1HLTAssignedPathEfficiency/p_{quantity[name]}", 0.99)'
    for _tpi in EXPANSIONS['trigger']
    if _tpi['name'] != "all"
]) + ')'


def xs_expression(ey_nick, tep_nick, ybys_dict, tp_dict, trigger_expansions, te_threshold=0.95):
    """Return expression for cross section with phase space partitioning choosing trigger path with maximal event yield."""
    # let outer expansion determine ybys slice
    if ybys_dict is None:
        ybys_dict = dict(name='{ybys[name]}')

    # get yield for trigger path which maximizes yield
    _max_yield_string = ('max(' +
        ', '.join([
            (
                '"{ey}:'+ybys_dict['name']+'/'+_tpi['name']+'/h_{{quantity[name]}}" * threshold('
                    '"{tep}:'+ybys_dict['name']+'/'+_tpi['name']+'/jet1HLTAssignedPathEfficiency/p_{{quantity[name]}}", ' +
                    str(te_threshold) +
                ')'
            )
            for _tpi in trigger_expansions
            if _tpi['name'] != "all"
        ]) + ')'
    )

    return (
        # only display point if the first argument maximal
        'mask_if_less('
            # event yield
            '"{ey}:{ybys[name]}/{tp[name]}/h_{{quantity[name]}}"'
            # but only if the corresponding trigger efficiency is >99%
            '* threshold('
                '"{tep}:{ybys[name]}/{tp[name]}/jet1HLTAssignedPathEfficiency/p_{{quantity[name]}}", ' +
                str(te_threshold) +
            '),' +
            # reference is the maximum of all clipped event yields
            _max_yield_string +
        ')'
        # divide by the trigger efficiency
        ' / discard_errors("{tep}:{ybys[name]}/{tp[name]}/jet1HLTAssignedPathEfficiency/p_{{quantity[name]}}")'
        # divide by the luminosity
        ' / ' + str(tp_dict['lumi_ub']/1e6)
    ).format(ey=ey_nick, tep=tep_nick, ybys=ybys_dict, tp=tp_dict)


def xs_expression_mc(ey_nick, ybys_dict, mc_subsample_expansions, event_number_threshold=20):
    """Return expression for MC cross section."""

    # let outer expansion determine ybys slice
    if ybys_dict is None:
        ybys_dict = dict(name='{ybys[name]}')

    return '(' + '+'.join([
        '((1.0*{mc_subsample[xs]}) / {mc_subsample[n_events]} * '
        'atleast("{ey}:{ybys[name]}/{mc_subsample[name]}/h_{{quantity[name]}}", {en_thres}))'.format(ey=ey_nick, ybys=ybys_dict, mc_subsample=_ms_dict, en_thres=event_number_threshold)
        for _ms_dict in mc_subsample_expansions
    ]) + ')'


FONTPROPERTIES = dict(
    big_bold=FontProperties(
        weight='bold',
        family='Nimbus Sans',
        size=20,
    ),
    small_bold=FontProperties(
        weight='bold',
        family='Nimbus Sans',
        size=12,
    ),
    italic=FontProperties(
        style='italic',
        family='Nimbus Sans',
        size=14,
    ),
)

TEXTS = {
    "CMS" : dict(xy=(.05, .9), text=r"CMS", transform='axes', fontproperties=FONTPROPERTIES['big_bold']),
    "PrivateWork" : dict(xy=(.17, .9), text=r"Private Work", transform='axes', fontproperties=FONTPROPERTIES['italic']),
    "AK4PFCHS" : dict(xy=(.03, .03), text=r"AK4PFCHS", transform='axes', fontproperties=FONTPROPERTIES['small_bold']),
}

FIGURE_TEMPLATES = {
    # -- DATA and MC

    # cross section in data and MC, colored by YBYS splitting
    'CrossSection': {
        'filename' : "CrossSection/{quantity[name]}.png",
        'figsize' : (12, 8),
        'subplots' : [
            {
                'expression': '10**({quantity[stagger_factors]['+_ybys['name']+']}) * ' + xs_expression('ey', 'te', ybys_dict=_ybys, tp_dict=_tp, trigger_expansions=EXPANSIONS['trigger']),
                'label': _ybys['label'] + r' ($\times$10$^{{{quantity[stagger_factors]['+_ybys['name']+']}}}$)' if _tp['name'] == "HLT_PFJet500" else None,
                'color': _ybys['color'],
                'marker': _ybys['marker'],
                'marker_style': _ybys['marker_style'],
                'plot_method': 'errorbar',
                'mask_zero_errors': True,
                'normalize_to_width': True,
            }
            for _tp in EXPANSIONS['trigger']
            for _ybys in EXPANSIONS['ybys_narrow']
            if (_tp['name'] != "all") and (_ybys['name'] != "inclusive")
        ] + [
            {
                'expression': '10**({quantity[stagger_factors]['+_ybys['name']+']}) * ' + xs_expression_mc("eymc", _ybys, mc_subsample_expansions=EXPANSIONS['mc_subsample']),
                'label': LiteralString("MC") if _ybys['name'] == EXPANSIONS['ybys_narrow'][1]['name'] else None,
                'color': 'k',
                'marker': ',',
                'marker_style': 'empty',
                'plot_method': 'errorbar',
                'mask_zero_errors': True,
                'normalize_to_width': True,
            }
            for _ybys in EXPANSIONS['ybys_narrow']
            if (_ybys['name'] != "inclusive")
        ],
        'pads' : [
            {
                'x_label' : '{quantity[label]}',
                'x_range' : (100, 25000), #ContextValue('quantity[range]'),
                'x_scale' : '{quantity[scale]}',
                'y_label' : '{quantity[xs_label]}', #LiteralString('Diff. cross section / pb GeV$^{-1}$'),
                'y_range' : ContextValue('quantity[xs_range]'),
                'y_scale' : 'log',
                'legend_kwargs': dict(loc='upper right'),
            },
        ],
        'pad_spec' : {
            'right': 0.95,
            'bottom': 0.15,
        },
    },

    # cross section in data and MC, colored by HLT path
    'CrossSection_HLTColor' : {
        'filename' : "CrossSection_HLTColor/{quantity[name]}.png",
        'figsize' : (12, 8),
        'subplots' : [
            {
                'expression': '10**({quantity[stagger_factors]['+_ybys['name']+']}) * ' + xs_expression('ey', 'te', ybys_dict=_ybys, tp_dict=_tp, trigger_expansions=EXPANSIONS['trigger']),
                'label': _tp['label'] if _ybys['name'] == EXPANSIONS['ybys_narrow'][1]['name'] else None,
                'color': _tp['color'],
                'marker': _tp['marker'],
                'marker_style': _tp['marker_style'],
                'plot_method': 'errorbar',
                'mask_zero_errors': True,
                'normalize_to_width': True,
            }
            for _tp in EXPANSIONS['trigger']
            for _ybys in EXPANSIONS['ybys_narrow']
            if (_tp['name'] != "all") and (_ybys['name'] != "inclusive")
        ] + [
            {
                'expression': '10**({quantity[stagger_factors]['+_ybys['name']+']}) * ' + xs_expression_mc("eymc", _ybys, mc_subsample_expansions=EXPANSIONS['mc_subsample']),
                'label': LiteralString("MC") if _ybys['name'] == EXPANSIONS['ybys_narrow'][1]['name'] else None,
                'color': 'k',
                'marker': ',',
                'marker_style': 'empty',
                'plot_method': 'errorbar',
                'mask_zero_errors': True,
                'normalize_to_width': True,
            }
            for _ybys in EXPANSIONS['ybys_narrow']
            if (_ybys['name'] != "inclusive")
        ],
        'pads' : [
            {
                'x_label' : '{quantity[label]}',
                'x_range' : (100, 25000), #ContextValue('quantity[range]'),
                'x_scale' : '{quantity[scale]}',
                'y_label' : '{quantity[xs_label]}', #LiteralString('Diff. cross section / pb GeV$^{-1}$'),
                'y_range' : ContextValue('quantity[xs_range]'),
                'y_scale' : 'log',
                'legend_kwargs': dict(loc='upper right'),
            },
        ],
        'pad_spec' : {
            'right': 0.95,
            'bottom': 0.15,
        },
    },
    'CrossSectionRatio': {
        'filename' : "CrossSectionRatio/{quantity[name]}/{ybys[name]}.png",
        'figsize' : (8, 2.5),
        'subplots' : [
            {
                'expression': '(' + xs_expression('ey', 'te', ybys_dict=None, tp_dict=_tp, trigger_expansions=EXPANSIONS['trigger']) + ')/(' + xs_expression_mc("eymc", None, mc_subsample_expansions=EXPANSIONS['mc_subsample']) + ')',
                'label': "{ybys[label]}" if _tp['name'] == "HLT_PFJet200" else None,
                'color': "{ybys[color]}",
                'marker': "{ybys[marker]}",
                'marker_style': "{ybys[marker_style]}",
                'plot_method': 'errorbar',
                'mask_zero_errors': True,
                'normalize_to_width': False,
            }
            for _tp in EXPANSIONS['trigger']
            if (_tp['name'] != "all")
        ],
        'pads' : [
            {
                'x_label' : '{quantity[label]}',
                'x_range' : ContextValue('quantity[range]'),
                'x_scale' : '{quantity[scale]}',
                'y_label' : 'Data/MC',
                'y_range' : (0.1, 1.9),
                'y_scale' : 'linear',
                'axhlines' : [1.0],
                'legend_kwargs': dict(loc='upper left'),
            },
        ],
    },
    'CrossSectionRatio_HLTColor': {
        'filename' : "CrossSectionRatio_HLTColor/{quantity[name]}/{ybys[name]}.png",
        'figsize' : (8, 2.5),
        'subplots' : [
            {
                'expression': '(' + xs_expression('ey', 'te', ybys_dict=None, tp_dict=_tp, trigger_expansions=EXPANSIONS['trigger']) + ')/(' + xs_expression_mc("eymc", None, mc_subsample_expansions=EXPANSIONS['mc_subsample']) + ')',
                'label': "{ybys[label]}" if _tp['name'] == "HLT_PFJet200" else None,
                'color': _tp['color'],
                'marker': _tp['marker'],
                'marker_style': _tp['marker_style'],
                'plot_method': 'errorbar',
                'mask_zero_errors': True,
                'normalize_to_width': False,
            }
            for _tp in EXPANSIONS['trigger']
            if (_tp['name'] != "all")
        ],
        'pads' : [
            {
                'x_label' : '{quantity[label]}',
                'x_range' : ContextValue('quantity[range]'),
                'x_scale' : '{quantity[scale]}',
                'y_label' : 'Data/MC',
                'y_range' : (0.1, 1.9),
                'y_scale' : 'linear',
                'axhlines' : [1.0],
                'legend_kwargs': dict(loc='upper left'),
            },
        ],
        'pad_spec' : {
            'right': 0.95,
            'bottom': 0.15,
        },
    },

    'OccupancyRatio': {
        'filename' : "OccupancyRatio/{ybys[name]}/{occupancy[name]}.png",
        'subplots' : [
            dict(expression='"oc:{ybys[name]}/HLT_PFJet450/{occupancy[y_quantity]}/h2d_{occupancy[x_quantity]}" / normalize_to_ref("ocmc:{ybys[name]}/{occupancy[y_quantity]}/h2d_{occupancy[x_quantity]}", "oc:{ybys[name]}/HLT_PFJet450/{occupancy[y_quantity]}/h2d_{occupancy[x_quantity]}")',
                 label=r'inclusive', plot_method='pcolormesh', cmap='bwr_r',
                 #norm=SymLogNorm(linthresh=0.03, linscale=0.03, vmin=-1e1, vmax=1e1)
                 vmin=0.1, vmax=1.9,
             ),
        ],
        'pads' : [
            {
                'x_label' : '{occupancy[x_label]}',
                'x_range' : ContextValue('occupancy[x_range]'),
                'x_scale' : '{occupancy[x_scale]}',
                'y_label' : '{occupancy[y_label]}',
                'y_range' : ContextValue('occupancy[y_range]'),
                'y_scale' : '{occupancy[x_scale]}',
                'z_scale' : 'linear',
                'z_label' : 'Data/MC',
                'z_labelpad' : 21.0,
            },
        ],
        'text_output': True,
    },


    'PFEnergyFractions': {
        'filename' : "PFEnergyFractions/{ybys[name]}/{quantity[name]}.png",
        'pad_spec' : {
            'right': 0.95,
            'bottom': 0.15,
            'top': 0.925,
            'hspace': 0.075,
        },
        'subplots' : [
            dict(expression='discard_errors("pfefmc:{ybys[name]}/jet1'+_pf['name']+'/p_{quantity[name]}")',
                 label=_pf['label'], plot_method='bar', color=_pf['color'],
                 stack='mc', show_yerr=False,
                 #mask_zero_errors=True  #TODO: fix bug
            )
            for _pf in EXPANSIONS['pf_fraction']
            if _pf['name'] not in ("HFEMFraction", "HFHadronFraction")
        ] + [
            dict(expression='"pfef:{ybys[name]}/jet1'+_pf['name']+'/p_{quantity[name]}"',
                 label=_pf['label'], plot_method='errorbar', marker=_pf['marker'], marker_style=_pf['marker_style'], color='k',
                 stack='data',
                 #mask_zero_errors=True  #TODO: fix bug
            )
            for _pf in EXPANSIONS['pf_fraction']
            if _pf['name'] not in ("HFEMFraction", "HFHadronFraction")
        ] + [
            dict(expression='100.0 * (h("pfef:{ybys[name]}/jet1'+_pf['name']+'/p_{quantity[name]}") - h("pfefmc:{ybys[name]}/jet1'+_pf['name']+'/p_{quantity[name]}"))',
                 label=None, plot_method='errorbar', marker=_pf['marker'], marker_style=_pf['marker_style'], color=_pf['color'],
                 stack=None,
                 #mask_zero_errors=True  #TODO: fix bug
                 pad=1
            )
            for _pf in EXPANSIONS['pf_fraction']
            if _pf['name'] not in ("HFEMFraction", "HFHadronFraction")
        ],
        'pads' : [
            {
                'height_share' : 3,
                'x_label' : None,
                'x_range' : ContextValue('quantity[range]'),
                'x_scale' : '{quantity[scale]}',
                'y_label' : 'PF Energy Fraction',
                'y_range' : (0, 1.5),
                'y_scale' : 'linear',
                'x_ticklabels' : [],
                'legend_kwargs': dict(loc='upper right', ncol=2),
            },
            {
                'height_share' : 1,
                'x_label' : '{quantity[label]}',
                'x_range' : ContextValue('quantity[range]'),
                'x_scale' : '{quantity[scale]}',
                'y_label' : 'Data-MC (%)',
                'y_range' : (-5, 5),
                'y_scale' : 'linear',
                'legend_kwargs': dict(loc='lower left', ncol=2),
            },
        ],
        'texts' : [
            dict(xy=(.04, .075), text="{ybys[yb_label]}", transform='axes'),
            dict(xy=(.04, .125), text="{ybys[ys_label]}", transform='axes'),
        ]
    },

    # -- Data

    'TriggerEfficiencies': {
        'filename' : "TriggerEfficiencies/{quantity[name]}/{ybys[name]}.png",
        'subplots' : [
            {
                'expression': '"te:{ybys[name]}/'+_tp['name']+'/jet1HLTAssignedPathEfficiency/p_{quantity[name]}"',
                'label': _tp['label'],
                'color': _tp['color'],
                'marker': _tp['marker'],
                'marker_style': _tp['marker_style'],
                'plot_method': 'errorbar',
                'mask_zero_errors': True,
            }
            for _tp in EXPANSIONS['trigger'] if _tp['name'] != "all"
        ],
        'pads' : [
            {
                'x_label' : '{quantity[label]}',
                'x_range' : ContextValue('quantity[range]'),
                'x_scale' : '{quantity[scale]}',
                'y_label' : 'Mean trigger efficiency',
                'y_range' : (0.97, 1.01),
                'y_scale' : 'linear',
                'axhlines' : [0.99, 1.0],
                'legend_kwargs': dict(loc='lower right'),
            },
        ],
    },
    'TriggerEfficienciesMax': {
        'filename' : "TriggerEfficienciesMax/{quantity[name]}/{ybys[name]}.png",
        'subplots' : [
            {
                'expression': 'mask_if_less("te:{ybys[name]}/'+_tp['name']+'/jet1HLTAssignedPathEfficiency/p_{quantity[name]}", '+_max_te+')',
                'label': _tp['label'],
                'color': _tp['color'],
                'marker': _tp['marker'],
                'marker_style': _tp['marker_style'],
                'plot_method': 'errorbar',
                #'mask_zero_errors': True,
            }
            for _tp in EXPANSIONS['trigger'] if _tp['name'] != "all"
        ],
        'pads' : [
            {
                'x_label' : '{quantity[label]}',
                'x_range' : ContextValue('quantity[range]'),
                'x_scale' : '{quantity[scale]}',
                'y_label' : 'Mean trigger efficiency',
                'y_range' : (0.97, 1.01),
                'y_scale' : 'linear',
                'axhlines' : [0.99, 1.0],
                'legend_kwargs': dict(loc='lower left'),
            },
        ],
    },
    'TriggerEfficienciesMaxMonochrome': {
        'filename' : "TriggerEfficienciesMaxMonochrome/{quantity[name]}/{ybys[name]}.png",
        'subplots' : [
            {
                'expression': _max_te,
                'label': "max. efficient trigger",
                'color': 'k',
                'marker': 'o',
                'marker_style': 'full',
                'plot_method': 'errorbar',
                #'mask_zero_errors': True,
            }
        ],
        'pads' : [
            {
                'x_label' : '{quantity[label]}',
                'x_range' : ContextValue('quantity[range]'),
                'x_scale' : '{quantity[scale]}',
                'y_label' : 'Mean trigger efficiency',
                'y_range' : (0.97, 1.01),
                'y_scale' : 'linear',
                'axhlines' : [0.99, 1.0],
                'legend_kwargs': dict(loc='lower right'),
            },
        ],
    },
    'EventYield': {
        'filename' : "EventYield/{quantity[name]}/{ybys[name]}.png",
        'subplots' : [
            {
                'expression': '"ey:{ybys[name]}/'+_tp['name']+'/h_{quantity[name]}"',
                'label': _tp['label'],
                'color': _tp['color'],
                'marker': _tp['marker'],
                'marker_style': _tp['marker_style'],
                'plot_method': 'errorbar',
                #'mask_zero_errors': True,
            }
            for _tp in EXPANSIONS['trigger_dijet'] if _tp['name'] != "all"
        ],
        'pads' : [
            {
                'x_label' : '{quantity[label]}',
                'x_range' : ContextValue('quantity[range]'),
                'x_scale' : '{quantity[scale]}',
                'y_label' : 'Events',
                'y_range' : (0.1, 1e9),
                'y_scale' : 'log',
                'axhlines' : [1.0],
                'legend_kwargs': dict(loc='upper right'),
            },
        ],
        'pad_spec' : {
            'right': 0.95,
            'bottom': 0.15,
        },
        'texts' : [
            dict(xy=(.04, 1.0 - .125), text="{ybys[yb_label]}", transform='axes'),
            dict(xy=(.04, 1.0 - .075), text="{ybys[ys_label]}", transform='axes'),
        ],
    },
    'EventYieldMaxTE': {
        'filename' : "EventYieldMaxTE/{quantity[name]}/{ybys[name]}.png",
        'subplots' : [
            {
                'expression': '"ey:{ybys[name]}/'+_tp['name']+'/h_{quantity[name]}" /mask_if_less("te:{ybys[name]}/'+_tp['name']+'/jet1HLTAssignedPathEfficiency/p_{quantity[name]}", '+_max_te+')',
                'label': _tp['label'],
                'color': _tp['color'],
                'marker': _tp['marker'],
                'marker_style': _tp['marker_style'],
                'plot_method': 'errorbar',
                #'mask_zero_errors': True,
            }
            for _tp in EXPANSIONS['trigger'] if _tp['name'] != "all"
        ],
        'pads' : [
            {
                'x_label' : '{quantity[label]}',
                'x_range' : ContextValue('quantity[range]'),
                'x_scale' : '{quantity[scale]}',
                'y_label' : 'Events',
                'y_range' : (0.1, 1e9),
                'y_scale' : 'log',
                'axhlines' : [1.0],
                'legend_kwargs': dict(loc='upper right'),
            },
        ],
        'pad_spec' : {
            'right': 0.95,
            'bottom': 0.15,
        },
        'texts' : [
            dict(xy=(.04, 1.0 - .125), text="{ybys[yb_label]}", transform='axes'),
            dict(xy=(.04, 1.0 - .075), text="{ybys[ys_label]}", transform='axes'),
        ],
    },
    'EventYieldTEOver99': {
        'filename' : "EventYieldTEOver99/{quantity[name]}/{ybys[name]}.png",
        'subplots' : [
            {
                'expression': '"ey:{ybys[name]}/'+_tp['name']+'/h_{quantity[name]}" / atleast("te:{ybys[name]}/'+_tp['name']+'/jet1HLTAssignedPathEfficiency/p_{quantity[name]}", 0.99)',
                'label': _tp['label'],
                'color': _tp['color'],
                'marker': _tp['marker'],
                'marker_style': _tp['marker_style'],
                'plot_method': 'errorbar',
                #'mask_zero_errors': True,
            }
            for _tp in EXPANSIONS['trigger'] if _tp['name'] != "all"
        ],
        'pads' : [
            {
                'x_label' : '{quantity[label]}',
                'x_range' : ContextValue('quantity[range]'),
                'x_scale' : '{quantity[scale]}',
                'y_label' : 'Events',
                'y_range' : (0.1, 1e9),
                'y_scale' : 'log',
                'axhlines' : [1.0],
                'legend_kwargs': dict(loc='upper right'),
            },
        ],
        'pad_spec' : {
            'right': 0.95,
            'bottom': 0.15,
        },
        'texts' : [
            dict(xy=(.04, 1.0 - .125), text="{ybys[yb_label]}", transform='axes'),
            dict(xy=(.04, 1.0 - .075), text="{ybys[ys_label]}", transform='axes'),
        ],
    },
    'EventYieldTEOver99_MaxYield': {
        'filename' : "EventYieldTEOver99_MaxYield/{quantity[name]}/{ybys[name]}.png",
        'subplots' : [
            {
                'expression': 'mask_if_less("ey:{ybys[name]}/'+_tp['name']+'/h_{quantity[name]}" * threshold("te:{ybys[name]}/'+_tp['name']+'/jet1HLTAssignedPathEfficiency/p_{quantity[name]}", 0.99), ' + _max_yield_99 + ')',
                'label': _tp['label'],
                'color': _tp['color'],
                'marker': _tp['marker'],
                'marker_style': _tp['marker_style'],
                'plot_method': 'errorbar',
                #'mask_zero_errors': True,
            }
            for _tp in EXPANSIONS['trigger'] if _tp['name'] != "all"
        ],
        'pads' : [
            {
                'x_label' : '{quantity[label]}',
                'x_range' : ContextValue('quantity[range]'),
                'x_scale' : '{quantity[scale]}',
                'y_label' : 'Events',
                'y_range' : (0.1, 1e9),
                'y_scale' : 'log',
                'axhlines' : [1.0],
                'legend_kwargs': dict(loc='upper right'),
            },
        ],
        'pad_spec' : {
            'right': 0.95,
            'bottom': 0.15,
        },
        'texts' : [
            dict(xy=(.04, 1.0 - .125), text="{ybys[yb_label]}", transform='axes'),
            dict(xy=(.04, 1.0 - .075), text="{ybys[ys_label]}", transform='axes'),
        ],
    },
    'EventYieldTEOver95_MaxYield': {
        'filename' : "EventYieldTEOver95_MaxYield/{quantity[name]}/{ybys[name]}.png",
        'subplots' : [
            {
                'expression': 'mask_if_less("ey:{ybys[name]}/'+_tp['name']+'/h_{quantity[name]}" * threshold("te:{ybys[name]}/'+_tp['name']+'/jet1HLTAssignedPathEfficiency/p_{quantity[name]}", 0.95), ' + _max_yield_99 + ')',
                'label': _tp['label'],
                'color': _tp['color'],
                'marker': _tp['marker'],
                'marker_style': _tp['marker_style'],
                'plot_method': 'errorbar',
                #'mask_zero_errors': True,
            }
            for _tp in EXPANSIONS['trigger'] if _tp['name'] != "all"
        ],
        'pads' : [
            {
                'x_label' : '{quantity[label]}',
                'x_range' : ContextValue('quantity[range]'),
                'x_scale' : '{quantity[scale]}',
                'y_label' : 'Events',
                'y_range' : (0.1, 1e9),
                'y_scale' : 'log',
                'axhlines' : [1.0],
                'legend_kwargs': dict(loc='upper right'),
            },
        ],
        'pad_spec' : {
            'right': 0.95,
            'bottom': 0.15,
        },
        'texts' : [
            dict(xy=(.04, 1.0 - .125), text="{ybys[yb_label]}", transform='axes'),
            dict(xy=(.04, 1.0 - .075), text="{ybys[ys_label]}", transform='axes'),
        ],
    },
    'EventYieldTEOver99_MaxTE': {
        'filename' : "EventYieldTEOver99_MaxTE/{quantity[name]}/{ybys[name]}.png",
        'subplots' : [
            {
                'expression': 'mask_if_less("ey:{ybys[name]}/'+_tp['name']+'/h_{quantity[name]}" * threshold("te:{ybys[name]}/'+_tp['name']+'/jet1HLTAssignedPathEfficiency/p_{quantity[name]}", 0.99), ' + _max_te_99 + ')',
                'label': _tp['label'],
                'color': _tp['color'],
                'marker': _tp['marker'],
                'marker_style': _tp['marker_style'],
                'plot_method': 'errorbar',
                #'mask_zero_errors': True,
            }
            for _tp in EXPANSIONS['trigger'] if _tp['name'] != "all"
        ],
        'pads' : [
            {
                'x_label' : '{quantity[label]}',
                'x_range' : ContextValue('quantity[range]'),
                'x_scale' : '{quantity[scale]}',
                'y_label' : 'Events',
                'y_range' : (0.1, 1e9),
                'y_scale' : 'log',
                'axhlines' : [1.0],
                'legend_kwargs': dict(loc='upper right'),
            },
        ],
        'pad_spec' : {
            'right': 0.95,
            'bottom': 0.15,
        },
        'texts' : [
            dict(xy=(.04, 1.0 - .125), text="{ybys[yb_label]}", transform='axes'),
            dict(xy=(.04, 1.0 - .075), text="{ybys[ys_label]}", transform='axes'),
        ],
    },
    'EventYield_allTriggers': {
        'filename' : "EventYield_allTriggers/{quantity[name]}/{ybys[name]}.png",
        'subplots' : [
            {
                'expression': '"ey:{ybys[name]}/all/h_{quantity[name]}"',
                'label': None,
                'color': 'k',
                'marker': 'o',
                'marker_style': 'full',
                'plot_method': 'errorbar',
                #'mask_zero_errors': True,
            }
        ],
        'pads' : [
            {
                'x_label' : '{quantity[label]}',
                'x_range' : ContextValue('quantity[range]'),
                'x_scale' : '{quantity[scale]}',
                'y_label' : 'Events',
                'y_range' : (0.1, 1e9),
                'y_scale' : 'log',
                'axhlines' : [1.0],
                'legend_kwargs': dict(loc='upper right'),
            },
        ],
        'pad_spec' : {
            'right': 0.95,
            'bottom': 0.15,
        },
        'texts' : [
            dict(xy=(.04, 1.0 - .125), text="{ybys[yb_label]}", transform='axes'),
            dict(xy=(.04, 1.0 - .075), text="{ybys[ys_label]}", transform='axes'),
        ],
    },

    'Occupancy': {
        'filename' : "Occupancy/{ybys[name]}/{occupancy[name]}.png",
        'subplots' : [
            dict(expression='"oc:{ybys[name]}/all/{occupancy[y_quantity]}/h2d_{occupancy[x_quantity]}"', label=r'inclusive', plot_method='pcolormesh', cmap='viridis'),
        ],
        'pads' : [
            {
                'x_label' : '{occupancy[x_label]}',
                'x_range' : ContextValue('occupancy[x_range]'),
                'x_scale' : '{occupancy[x_scale]}',
                'y_label' : '{occupancy[y_label]}',
                'y_range' : ContextValue('occupancy[y_range]'),
                'y_scale' : '{occupancy[x_scale]}',
                'z_scale' : 'log',
                'z_label' : 'Events',
                'z_labelpad' : 21.0,
            },
        ],
    },

    # -- MC

    'OccupancyMC': {
        'filename' : "OccupancyMC/{ybys[name]}/{occupancy[name]}.png",
        'subplots' : [
            dict(expression='"ocmc:{ybys[name]}/{occupancy[y_quantity]}/h2d_{occupancy[x_quantity]}"', label=r'inclusive', plot_method='pcolormesh', cmap='viridis'),
        ],
        'pads' : [
            {
                'x_label' : '{occupancy[x_label]}',
                'x_range' : ContextValue('occupancy[x_range]'),
                'x_scale' : '{occupancy[x_scale]}',
                'y_label' : '{occupancy[y_label]}',
                'y_range' : ContextValue('occupancy[y_range]'),
                'y_scale' : '{occupancy[x_scale]}',
                'z_scale' : 'log',
                'z_label' : 'Events',
                'z_labelpad' : 21.0,
            },
        ],
    },

    # Reco/Gen response matrix
    'JetResponseMatrix': {
        'filename' : "JetResponseMatrix/{ybys[name]}/{quantity[name]}_vs_{quantity[gen_name]}.png",
        'subplots' : [
            dict(expression='normalize_x("jr:{ybys[name]}/{quantity[name]}/h2d_{quantity[gen_name]}")', label=r'inclusive', plot_method='pcolormesh', cmap='viridis'),
        ],
        'pad_spec' : {
            'right': 0.95,
            'bottom': 0.15,
        },
        'pads' : [
            {
                'x_label' : '{quantity[gen_label]}',
                'x_range' : ContextValue('quantity[range]'),
                'x_scale' : '{quantity[scale]}',
                'y_label' : '{quantity[label]}',
                'y_range' : ContextValue('quantity[range]'),
                'y_scale' : '{quantity[scale]}',
                'z_range' : (0, 1),
                'z_scale' : 'linear',
                'z_label' : 'Event fraction',
                'z_labelpad' : 21.0,
            },
        ],
    },

    # RMS of jet quantity distribution (one subplot per YBYS splitting)
    'JetResolution_YBYS': {
        'filename' : "JetResolution_YBYS/{quantity[name]}.png",
        'subplots' : [
            {
                'expression': 'yerr("jr:' + _ybys['name'] + '/{quantity[name]}/p_{quantity[gen_name]}")',
                'label': _ybys['label'],
                'color': _ybys['color'],
                'marker': _ybys['marker'],
                'marker_style': _ybys['marker_style'],
                'plot_method': 'errorbar',
            }
            for _ybys in EXPANSIONS['ybys']
            if (_ybys['name'] != "inclusive")
        ],
        'pads' : [
            {
                'x_label' : '{quantity[gen_label]}',
                'x_range' : ContextValue('quantity[range]'),
                'x_scale' : '{quantity[scale]}',
                'y_label' : r'RMS({quantity[label]})',
                'y_range' : (1, 1e5),
                'y_scale' : 'log',
            },
        ],
        'request_params': {
            'profile_error_option': "S",  # take standard deviation instead of error on mean
        },
    },

    # RMS of jet quantity distribution, divided by bin width (one subplot per YBYS splitting)
    'JetResolutionOverBinWidth_YBYS': {
        'filename' : "JetResolutionOverBinWidth_YBYS/{quantity[name]}.png",
        'subplots' : [
            {
                'expression': 'yerr("jr:' + _ybys['name'] + '/{quantity[name]}/p_{quantity[gen_name]}") / bin_width("jr:' + _ybys['name'] + '/{quantity[name]}/p_{quantity[gen_name]}")',
                'label': _ybys['label'],
                'color': _ybys['color'],
                'marker': _ybys['marker'],
                'marker_style': _ybys['marker_style'],
                'plot_method': 'errorbar',
            }
            for _ybys in EXPANSIONS['ybys']
            if (_ybys['name'] != "inclusive")
        ],
        'pads' : [
            {
                'x_label' : '{quantity[gen_label]}',
                #'x_range' : ContextValue('quantity[range]'),
                'x_scale' : '{quantity[scale]}',
                'y_label' : r'RMS({quantity[label]}) / Bin width',
                'y_range' : (0.0, 2.0),
                'y_scale' : 'linear',
                'axhlines' : [1.0],
            },
        ],
        'request_params': {
            'profile_error_option': "S",  # take standard deviation instead of error on mean
        },
    },

    # RMS of jet quantity distribution (one subplot per YBYS splitting)
    'JetResolution_YBYS_Narrow': {
        'filename' : "JetResolution_YBYS_Narrow/{quantity[name]}.png",
        'subplots' : [
            {
                'expression': 'yerr("jr:' + _ybys['name'] + '/{quantity[name]}/p_{quantity[gen_name]}")',
                'label': _ybys['label'],
                'color': _ybys['color'],
                'marker': _ybys['marker'],
                'marker_style': _ybys['marker_style'],
                'plot_method': 'errorbar',
            }
            for _ybys in EXPANSIONS['ybys_narrow']
            if (_ybys['name'] != "inclusive")
        ],
        'pads' : [
            {
                'x_label' : '{quantity[gen_label]}',
                'x_range' : ContextValue('quantity[range]'),
                'x_scale' : '{quantity[scale]}',
                'y_label' : r'RMS({quantity[label]})',
                'y_range' : (1, 1e5),
                'y_scale' : 'log',
                'legend_kwargs': dict(ncol=2),
            },
        ],
        'request_params': {
            'profile_error_option': "S",  # take standard deviation instead of error on mean
        },
    },

    # RMS of jet quantity distribution, divided by bin width (one subplot per YBYS splitting)
    'JetResolutionOverBinWidth_YBYS_Narrow': {
        'filename' : "JetResolutionOverBinWidth_YBYS_Narrow/{quantity[name]}.png",
        'subplots' : [
            {
                'expression': 'yerr("jr:' + _ybys['name'] + '/{quantity[name]}/p_{quantity[gen_name]}") / bin_width("jr:' + _ybys['name'] + '/{quantity[name]}/p_{quantity[gen_name]}")',
                'label': _ybys['label'],
                'color': _ybys['color'],
                'marker': _ybys['marker'],
                'marker_style': _ybys['marker_style'],
                'plot_method': 'errorbar',
            }
            for _ybys in EXPANSIONS['ybys_narrow']
            if (_ybys['name'] != "inclusive")
        ],
        'pads' : [
            {
                'x_label' : '{quantity[gen_label]}',
                #'x_range' : ContextValue('quantity[range]'),
                'x_scale' : '{quantity[scale]}',
                'y_label' : r'RMS({quantity[label]}) / Bin width',
                'y_range' : (0.0, 2.0),
                'y_scale' : 'linear',
                'axhlines' : [1.0],
                'legend_kwargs': dict(ncol=2),
            },
        ],
        'request_params': {
            'profile_error_option': "S",  # take standard deviation instead of error on mean
        },
    },

    # RMS of jet quantity distribution (only one subplot showing inclusive sample)
    'JetResolution': {
        'filename' : "JetResolution/{quantity[name]}.png",
        'subplots' : [
            {
                'expression': 'yerr("jr:' + _ybys['name'] + '/{quantity[name]}/p_{quantity[gen_name]}")',
                'label': _ybys['label'],
                'color': _ybys['color'],
                'marker': _ybys['marker'],
                'marker_style': _ybys['marker_style'],
                'plot_method': 'errorbar',
            }
            for _ybys in EXPANSIONS['ybys_narrow']
            if (_ybys['name'] == "inclusive")
        ],
        'pads' : [
            {
                'x_label' : '{quantity[gen_label]}',
                'x_range' : ContextValue('quantity[range]'),
                'x_scale' : '{quantity[scale]}',
                'y_label' : r'RMS({quantity[label]})',
                'y_range' : (1, 1e5),
                'y_scale' : 'log',
            },
        ],
        'request_params': {
            'profile_error_option': "S",  # take standard deviation instead of error on mean
        },
    },

    # RMS of jet quantity distribution, divided by bin width (only one subplot showing inclusive sample)
    'JetResolutionOverBinWidth': {
        'filename' : "JetResolutionOverBinWidth/{quantity[name]}.png",
        'subplots' : [
            {
                'expression': 'yerr("jr:' + _ybys['name'] + '/{quantity[name]}/p_{quantity[gen_name]}") / bin_width("jr:' + _ybys['name'] + '/{quantity[name]}/p_{quantity[gen_name]}")',
                'label': _ybys['label'],
                'color': _ybys['color'],
                'marker': _ybys['marker'],
                'marker_style': _ybys['marker_style'],
                'plot_method': 'errorbar',
            }
            for _ybys in EXPANSIONS['ybys_narrow']
            if (_ybys['name'] == "inclusive")
        ],
        'pads' : [
            {
                'x_label' : '{quantity[gen_label]}',
                #'x_range' : ContextValue('quantity[range]'),
                'x_scale' : '{quantity[scale]}',
                'y_label' : r'RMS({quantity[label]}) / Bin width',
                'y_range' : (0.0, 2.0),
                'y_scale' : 'linear',
                'axhlines' : [1.0],
            },
        ],
        'request_params': {
            'profile_error_option': "S",  # take standard deviation instead of error on mean
        },
    },

    # Comparison of generator and reconstruction level
    'GenRecoCompare_EventYield': {
        'filename' : "GenRecoCompare_EventYield/{ybys[name]}/{quantity[name]}.png",
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
                'y_label' : 'Events',
                'x_ticklabels' : [],
                'y_scale' : 'log',
                'legend_kwargs': dict(loc='lower left'),
            },
            # ratio pad
            {
                'height_share' : 1,
                'x_label' : '{quantity[label]}',
                'x_range' : ContextValue('quantity[range]'),
                'x_scale' : '{quantity[scale]}',
                'y_label' : 'Reco/Gen',
                'y_range' : (0.4, 1.6),
                'axhlines' : [1.0],
                'y_scale' : 'linear',
                'legend_kwargs': dict(loc='lower left'),
            },
        ],
        'subplots' : [
            # Reco
            dict(expression='"eymc:{ybys[name]}/h_{quantity[name]}"',
                 label=r'reco.', plot_method='errorbar', color="royalblue", marker="{ybys[marker]}", marker_style="{ybys[marker_style]}", pad=0),
            # Gen
            dict(expression='"eymc:{ybys[name]}/h_{quantity[gen_name]}"',
                 label=r'gen.',  plot_method='errorbar', color="red", marker="{ybys[marker]}", marker_style="{ybys[marker_style]}", pad=0),
            # Ratio Reco/Gen
            dict(expression='"eymc:{ybys[name]}/h_{quantity[name]}" / discard_errors("eymc:{ybys[name]}/h_{quantity[gen_name]}")',
                 label=None, plot_method='errorbar', color="k", marker="{ybys[marker]}", marker_style="{ybys[marker_style]}", pad=1),
        ],
    },
    'GenRecoCompare_EventYield_StitchingWeighted': {
        'filename' : "GenRecoCompare_EventYield_StitchingWeighted/{ybys[name]}/{quantity[name]}.png",
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
                'y_label' : 'Events',
                'x_ticklabels' : [],
                'y_scale' : 'log',
                'legend_kwargs': dict(loc='lower left'),
            },
            # ratio pad
            {
                'height_share' : 1,
                'x_label' : '{quantity[label]}',
                'x_range' : ContextValue('quantity[range]'),
                'x_scale' : '{quantity[scale]}',
                'y_label' : 'Reco/Gen',
                'y_range' : (0.4, 1.6),
                'axhlines' : [1.0],
                'y_scale' : 'linear',
                'legend_kwargs': dict(loc='lower left'),
            },
        ],
        'subplots' : [
            # Reco
            dict(expression='"eymc:{ybys[name]}/h_{quantity[name]}_weightForStitching"',
                 label=r'reco.', plot_method='errorbar', color="royalblue", marker="{ybys[marker]}", marker_style="{ybys[marker_style]}", pad=0),
            # Gen
            dict(expression='"eymc:{ybys[name]}/h_{quantity[gen_name]}_weightForStitching"',
                 label=r'gen.',  plot_method='errorbar', color="red", marker="{ybys[marker]}", marker_style="{ybys[marker_style]}", pad=0),
            # Ratio Reco/Gen
            dict(expression='"eymc:{ybys[name]}/h_{quantity[name]}_weightForStitching" / discard_errors("eymc:{ybys[name]}/h_{quantity[gen_name]}_weightForStitching")',
                 label=None, plot_method='errorbar', color="k", marker="{ybys[marker]}", marker_style="{ybys[marker_style]}", pad=1),
        ],
    },

    'FlavorFractions' : {
        'filename' : "FlavorFractions/{ybys[name]}/{quantity[name]}.png",
        'pad_spec' : {
            'right': 0.95,
            'bottom': 0.15,
            'top': 0.925,
            'hspace': 0.075,
        },
        'subplots' : [
            dict(expression='discard_errors("fl:{ybys[name]}/'+_pf['name']+'/h_{quantity[name]}" / "fl:{ybys[name]}/Flavor_AllDefined/h_{quantity[name]}")',
                 label=LiteralString(_pf['label']), plot_method='bar', color=_pf['color'], show_yerr=False,
                 stack='all',
            )
            for _pf in EXPANSIONS['flavor_fraction']
            if not _pf['name'].startswith("Flavor_QQ_aa")
        ] + [
            dict(expression='discard_errors(("fl:{ybys[name]}/Flavor_QQ_aa_ii/h_{quantity[name]}" + "fl:{ybys[name]}/Flavor_QQ_aa_ij/h_{quantity[name]}") / "fl:{ybys[name]}/Flavor_AllDefined/h_{quantity[name]}")',
                 label=LiteralString(r"$\overline{{\mathrm{{q}}}}\overline{{\mathrm{{q}}}}$"), plot_method='bar', color=_pf['color'], show_yerr=False,
                 stack='all',
            )
            for _pf in EXPANSIONS['flavor_fraction']
            if _pf['name'].startswith("Flavor_QQ_aa_ii")
        ],
        'pads' : [
            {
                'x_label' : '{quantity[label]}',
                'x_range' : ContextValue('quantity[range]'),
                'x_scale' : '{quantity[scale]}',
                'y_label' : 'Event Fraction',
                'y_range' : (0, 1.2),
                'y_scale' : 'linear',
                'legend_kwargs': dict(loc='upper right', ncol=4),
            },
        ],
    },

    'QCDSubprocessFractions' : {
        'filename' : "QCDSubprocessFractions/{ybys[name]}/{quantity[name]}.png",
        'pad_spec' : {
            'right': 0.95,
            'bottom': 0.15,
            'top': 0.925,
            'hspace': 0.075,
        },
        'subplots' : [
            dict(expression='discard_errors("qcd:{ybys[name]}/'+_qsf['name']+'/h_{quantity[name]}_weightForStitching" / "qcd:{ybys[name]}/QCDSubprocess_AllDefined/h_{quantity[name]}_weightForStitching")',
                 label=LiteralString(_qsf['label']), plot_method='bar', color=_qsf['color'], show_yerr=False,
                 stack='all',
            )
            for _qsf in EXPANSIONS['qcd_subprocess_fraction']
            if not _qsf['name'].startswith("QCDSubprocess_QQ_aa")
        #] + [
        #    dict(expression='discard_errors(("qcd:{ybys[name]}/QCDSubprocess_QQ_aa_ii/h_{quantity[name]}" + "qcd:{ybys[name]}/QCDSubprocess_QQ_aa_ij/h_{quantity[name]}") / "qcd:{ybys[name]}/QCDSubprocess_AllDefined/h_{quantity[name]}")',
        #         label=LiteralString(r"$\overline{{\mathrm{{q}}}}\overline{{\mathrm{{q}}}}$"), plot_method='bar', color=_qsf['color'], show_yerr=False,
        #         stack='all',
        #    )
        #    for _qsf in EXPANSIONS['qcd_subprocess_fraction']
        #    if _qsf['name'].startswith("QCDSubprocess_QQ_aa_ii")
        ],
        'pads' : [
            {
                'x_label' : '{quantity[label]}',
                'x_range' : ContextValue('quantity[range]'),
                'x_scale' : '{quantity[scale]}',
                'y_label' : 'Event Fraction',
                'y_range' : (0, 1.2),
                'y_scale' : 'linear',
                'legend_kwargs': dict(loc='upper right', ncol=4),
            },
        ],
        'texts' : [
            dict(xy=(.04, .125), text="{ybys[yb_label]}", transform='axes'),
            dict(xy=(.04, .075), text="{ybys[ys_label]}", transform='axes'),
        ],
    },
}

ANALYZE_TASK_TEMPLATES = {

    "CrossSections" : {
        'filename' : "CrossSections.root",
        'subtasks' : [
            {
                'expression': (
                    # event yield
                    '"ey:{ybys[name]}/{trigger[name]}/h_{quantity[name]}"'
                    # but only if the corresponding trigger efficiency is >95%
                    '* threshold('
                        '"te:{ybys[name]}/{trigger[name]}/jet1HLTAssignedPathEfficiency/p_{quantity[name]}", '
                        '0.95'
                    ')' +
                    # divide by the trigger efficiency
                    ' / "te:{ybys[name]}/{trigger[name]}/jet1HLTAssignedPathEfficiency/p_{quantity[name]}"'
                    # divide by the luminosity
                    ' / {trigger[lumi_ub]} * 1e6'
                ),
                'output_path' : "{ybys[name]}/{trigger[name]}/h_xs_{quantity[name]}",
            },
            {
                'expression': '"te:{ybys[name]}/{trigger[name]}/jet1HLTAssignedPathEfficiency/p_{quantity[name]}"',
                'output_path' : "{ybys[name]}/{trigger[name]}/p_te_{quantity[name]}",
            },
            {
                'expression': '"ey:{ybys[name]}/{trigger[name]}/h_{quantity[name]}"',
                'output_path' : "{ybys[name]}/{trigger[name]}/h_ey_{quantity[name]}",
            },
        ]
    },

}
