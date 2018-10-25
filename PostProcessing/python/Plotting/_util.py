"""
module fragment containing some useful functions
"""

from ._definitions import EXPANSIONS
from ._plot import ContextValue, LiteralString

from matplotlib.colors import SymLogNorm


__all__ = ['xs_expression', 'xs_expression_mc', 'FIGURE_TEMPLATES']


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


def xs_expression(ey_nick, tep_nick, ybys_dict, tp_dict, trigger_expansions):
    """Return expression for cross section with phase space partitioning choosing trigger path with maximal event yield."""
    # let outer expansion determine ybys slice
    if ybys_dict is None:
        ybys_dict = dict(name='{ybys[name]}')

    # get yield for trigger path which maximizes yield
    _max_yield_string = ('max(' +
        ', '.join([
            (
                '"{ey}:'+ybys_dict['name']+'/'+_tpi['name']+'/h_{{quantity[name]}}" * threshold('
                    '"{tep}:'+ybys_dict['name']+'/'+_tpi['name']+'/jet1HLTAssignedPathEfficiency/p_{{quantity[name]}}", '
                    '0.99'
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
                '"{tep}:{ybys[name]}/{tp[name]}/jet1HLTAssignedPathEfficiency/p_{{quantity[name]}}", '
                '0.99'
            '),' +
            # reference is the maximum of all clipped event yields
            _max_yield_string +
        ')'
        # divide by the trigger efficiency
        ' / discard_errors("{tep}:{ybys[name]}/{tp[name]}/jet1HLTAssignedPathEfficiency/p_{{quantity[name]}}")'
        # divide by the luminosity
        ' / ' + str(tp_dict['lumi_ub']/1e6)
    ).format(ey=ey_nick, tep=tep_nick, ybys=ybys_dict, tp=tp_dict)


def xs_expression_mc(ey_nick, ybys_dict):
    """Return expression for MC cross section."""

    # let outer expansion determine ybys slice
    if ybys_dict is None:
        ybys_dict = dict(name='{ybys[name]}')

    return (
        '"{ey}:{ybys[name]}/h_{{quantity[name]}}_weightForStitching"'
    ).format(ey=ey_nick, ybys=ybys_dict)


FIGURE_TEMPLATES = {
    # -- DATA and MC

    # cross section in data and MC, colored by YBYS splitting
    'CrossSection': {
        'filename' : "CrossSection/{quantity[name]}.png",
        'subplots' : [
            {
                'expression': '{quantity[stagger_factors]['+_ybys['name']+']} * ' + xs_expression('ey', 'te', ybys_dict=_ybys, tp_dict=_tp, trigger_expansions=EXPANSIONS['trigger']),
                'label': LiteralString(r"{} ($\times$10$^{{?}}$)".format(_ybys['label'])) if _tp['name'] == "HLT_PFJet500" else None,
                'color': _ybys['color'],
                'marker': _ybys['marker'],
                'marker_style': _ybys['marker_style'],
                'plot_method': 'errorbar',
                'mask_zero_errors': True,
                'normalize_to_width': True,
            }
            for _tp in EXPANSIONS['trigger']
            for _ybys in EXPANSIONS['ybys']
            if (_tp['name'] != "all") and (_ybys['name'] != "inclusive")
        ] + [
            {
                'expression': '{quantity[stagger_factors]['+_ybys['name']+']} * ' + xs_expression_mc("eymc", _ybys),
                'label': LiteralString("MC") if _ybys['name'] == "YB01_YS01" else None,
                'color': 'k',
                'marker': ',',
                'marker_style': 'empty',
                'plot_method': 'errorbar',
                'mask_zero_errors': True,
                'normalize_to_width': True,
            }
            for _ybys in EXPANSIONS['ybys']
            if (_ybys['name'] != "inclusive")
        ],
        'pads' : [
            {
                'x_label' : '{quantity[label]}',
                'x_range' : ContextValue('quantity[range]'),
                'x_scale' : '{quantity[scale]}',
                'y_label' : '{quantity[xs_label]}', #LiteralString('Diff. cross section / pb GeV$^{-1}$'),
                'y_range' : ContextValue('quantity[xs_range]'),
                'y_scale' : 'log',
                'legend_kwargs': dict(loc='upper right'),
            },
        ],
    },

    # cross section in data and MC, colored by HLT path
    'CrossSection_HLTColor' : {
        'filename' : "CrossSection_HLTColor/{quantity[name]}.png",
        'subplots' : [
            {
                'expression': '{quantity[stagger_factors]['+_ybys['name']+']} * ' + xs_expression('ey', 'te', ybys_dict=_ybys, tp_dict=_tp, trigger_expansions=EXPANSIONS['trigger']),
                'label': LiteralString(r"{}".format(_tp['label'])) if _ybys['name'] == "YB01_YS01" else None,
                'color': _tp['color'],
                'marker': _tp['marker'],
                'marker_style': _tp['marker_style'],
                'plot_method': 'errorbar',
                'mask_zero_errors': True,
                'normalize_to_width': True,
            }
            for _tp in EXPANSIONS['trigger']
            for _ybys in EXPANSIONS['ybys']
            if (_tp['name'] != "all") and (_ybys['name'] != "inclusive")
        ] + [
            {
                'expression': '{quantity[stagger_factors]['+_ybys['name']+']} * ' + xs_expression_mc("eymc", _ybys),
                'label': LiteralString("MC") if _tp['name'] == "YB01_YS01" else None,
                'color': 'k',
                'marker': ',',
                'marker_style': 'empty',
                'plot_method': 'errorbar',
                'mask_zero_errors': True,
                'normalize_to_width': True,
            }
            for _ybys in EXPANSIONS['ybys']
            if (_ybys['name'] != "inclusive")
        ],
        'pads' : [
            {
                'x_label' : '{quantity[label]}',
                'x_range' : ContextValue('quantity[range]'),
                'x_scale' : '{quantity[scale]}',
                'y_label' : '{quantity[xs_label]}', #LiteralString('Diff. cross section / pb GeV$^{-1}$'),
                'y_range' : ContextValue('quantity[xs_range]'),
                'y_scale' : 'log',
                'legend_kwargs': dict(loc='upper right', ncol=2),
            },
        ],
    },
    'CrossSectionRatio': {
        'filename' : "CrossSectionRatio/{quantity[name]}/{ybys[name]}.png",
        'figsize' : (8, 2.5),
        'subplots' : [
            {
                'expression': '(' + xs_expression('ey', 'te', ybys_dict=None, tp_dict=_tp, trigger_expansions=EXPANSIONS['trigger']) + ')/(' + xs_expression_mc("eymc", None) + ')',
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
                'expression': '(' + xs_expression('ey', 'te', ybys_dict=None, tp_dict=_tp, trigger_expansions=EXPANSIONS['trigger']) + ')/(' + xs_expression_mc("eymc", None) + ')',
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
                'expression': 'yerr("jr_wide:' + _ybys['name'] + '/{quantity[name]}/p_{quantity[gen_name]}")',
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
                'expression': 'yerr("jr_wide:' + _ybys['name'] + '/{quantity[name]}/p_{quantity[gen_name]}") / bin_width("jr_wide:' + _ybys['name'] + '/{quantity[name]}/p_{quantity[gen_name]}")',
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

    # RMS of jet quantity distribution (only one subplot showing inclusive sample)
    'JetResolution': {
        'filename' : "JetResolution/{quantity[name]}.png",
        'subplots' : [
            {
                'expression': 'yerr("jr_wide:' + _ybys['name'] + '/{quantity[name]}/p_{quantity[gen_name]}")',
                'label': _ybys['label'],
                'color': _ybys['color'],
                'marker': _ybys['marker'],
                'marker_style': _ybys['marker_style'],
                'plot_method': 'errorbar',
            }
            for _ybys in EXPANSIONS['ybys']
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
                'expression': 'yerr("jr_wide:' + _ybys['name'] + '/{quantity[name]}/p_{quantity[gen_name]}") / bin_width("jr_wide:' + _ybys['name'] + '/{quantity[name]}/p_{quantity[gen_name]}")',
                'label': _ybys['label'],
                'color': _ybys['color'],
                'marker': _ybys['marker'],
                'marker_style': _ybys['marker_style'],
                'plot_method': 'errorbar',
            }
            for _ybys in EXPANSIONS['ybys']
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
}
