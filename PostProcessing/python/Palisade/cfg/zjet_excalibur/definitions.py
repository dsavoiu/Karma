import numpy as np

from copy import deepcopy

from Karma.PostProcessing.Lumberjack.cfg.zjet_excalibur import QUANTITIES


def _uniform_range(quantity, n_standard_deviations=1.5):
    "symmetric confidence interval based on uniform distribution over defined quantity range"
    _a, _b = quantity.range
    _uniform_mean = 0.5 * (_a + _b)
    _uniform_error = float(_b - _a) / np.sqrt(12)
    return (
        _uniform_mean - n_standard_deviations*_uniform_error,
        _uniform_mean + n_standard_deviations*_uniform_error
    )


# mean ranges for quantities with non-uniform distributions
_LOOKUP_MEAN_RANGE = {
    'zpt' :     (50, 150),
    'jet1pt' :  (40, 140),
    'jet2pt' :  (15, 30),
    'jet3pt' :  (10, 25),
}
_LOOKUP_EXPECTED_VALUE = {
    "ptbalance" : 1.0,
    "mpf" : 1.0,
    "zphi" : 0.0,
    "zmass" : 91.1876,
    "jet1phi" : 0.0,
    "jet2phi" : 0.0,
    "jet3phi" : 0.0,
}
# display ranges for profiles of quantities with non-uniform distributions
_LOOKUP_PROFILE_RANGE = {
    'zpt' :         (5, 1000),
    'zmass' :       (90, 96),
    'mpf' :         (0.6, 1.4),
    'ptbalance' :   (0.6, 1.4),
    'jet1pt' :      (5, 1000),
    'jet2pt' :      (5, 200),
    'jet3pt' :      (5, 100),
}

EXPANSIONS = {
    # year
    "year" : [
        {
            "year": "2016",
            "year_short": "16",
            'color': "darkgoldenrod",
        },
        {
            "year": "2017",
            "year_short": "17",
            'color': "forestgreen",
        },
        {
            "year": "2018",
            "year_short": "18",
            'color': "darkorchid",
        },
    ],

    # run periods
    'run2016' : [
        {
            "name": "Run2016{}".format(_letter),
            "year": "2016",
            "year_short": "16",
            'color': _color,
        }
        for _letter, _color in zip(('B',       'C',       'D',       'E',       'F',       'G',       'H', 'BCDEFGH'),
                                   ('#ffc0cb', '#e11e1e', '#7c1010', '#1e9ce1', '#10447c', '#8cc90d', '#f0b117', 'k'))
    ],
    'run2017' : [
        {
            "name": "Run2017{}".format(_letter),
            "year": "2017",
            "year_short": "17",
            'color': _color,
        }
        for _letter, _color in zip(('B',       'C',       'D',       'E',       'F',   'BCDEF'),
                                   ('#ff8499', '#e90000', '#3760de', '#3da95d', '#36eac1', 'k'))
    ],

    'run2018' : [
        {
            "name": "Run2018{}".format(_letter),
            "year": "2018",
            "year_short": "18",
            'color': _color,
        }
        for _letter, _color in zip(('A',       'B',       'C',       'D',    'ABCD'),
                                   ('#cd5c5c', '#cd853f', '#008b8b', '#6a5acd', 'k'))
    ],

    # JEC IOVs
    'iov2016' : [
        {
            "name": "Run2016{}".format(_letter),
            "year": "2016",
            "year_short": "16",
            'color': _color,
        }
        for _letter, _color in zip(('BCD',     'EFearly', 'FlateGH', 'BCDEFGH'),
                                   ('#d92626', '#4169e1', '#b0861e', 'k'))
    ],
    'iov2017' : [
        {
            "name": "Run2017{}".format(_letter),
            "year": "2017",
            "year_short": "17",
            'color': _color,
        }
        for _letter, _color in zip(('B',       'C',       'DE',       'F',   'BCDEF'),
                                   ('#ff8499', '#e90000', '#4686ed',  '#36eac1', 'k'))
    ],

    'iov2018' : [
        {
            "name": "Run2018{}".format(_letter),
            "year": "2018",
            "year_short": "18",
            'color': _color,
        }
        for _letter, _color in zip(('A',       'B',       'C',       'D',    'ABCD'),
                                   ('#cd5c5c', '#cd853f', '#008b8b', '#6a5acd', 'k'))
    ],

    # event yields (2D binnings)
    'occupancy': [
        {
            "name": "{0}phi_vs_{0}eta".format(_q),
            #
            "x_quantity": "{}eta".format(_q),
            "x_label": r"$\eta^{\mathrm{" + (_q if len(_q) > 1 else _q.upper()) + "}}$",
            "x_scale": "linear",
            #
            "y_quantity": "{}phi".format(_q),
            "y_label": r"$\phi^{\mathrm{" + (_q if len(_q) > 1 else _q.upper()) + "}}$",
            "y_scale": "linear",
        }
        for _q in ('z', 'jet1', 'jet2', 'jet3')
    ]
    + [
        {
            "name": "{0}eta_vs_{0}pt".format(_q),
            #
            "x_quantity": "{}pt".format(_q),
            "x_label": r"$p_{\mathrm{T}}^{\mathrm{" + (_q if len(_q) > 1 else _q.upper()) + "}}$ /  GeV",
            "x_scale": "log",
            "x_range": (5, 5000),
            #
            "y_quantity": "{}eta".format(_q),
            "y_label": r"$\eta^{\mathrm{" + (_q if len(_q) > 1 else _q.upper()) + "}}$",
            "y_scale": "linear",
        }
        for _q in ('z', 'jet1', 'jet2', 'jet3')
    ],

    # -----

    # Particle Flow (PF) energy fractions
    'pf_fraction': [
        {
            "name": "ChargedHadronFraction",
            "label": r"PF charged hadron fraction",
            "scale": "log",
            "color": "red",
            "marker": "o",
            "marker_style": "full",
        },
        {
            "name": "PhotonFraction",
            "label": r"PF photon fraction",
            "scale": "log",
            "color": "royalblue",
            "marker": "s",
            "marker_style": "full",
        },
        {
            "name": "NeutralHadronFraction",
            "label": r"PF neutral hadron fraction",
            "scale": "log",
            "color": "green",
            "marker": "D",
            "marker_style": "full",
        },
        {
            "name": "MuonFraction",
            "label": r"PF muon fraction",
            "scale": "log",
            "color": "teal",
            "marker": "v",
            "marker_style": "full",
        },
        {
            "name": "ElectronFraction",
            "label": r"PF electron fraction",
            "scale": "log",
            "color": "orange",
            "marker": "^",
            "marker_style": "full",
        },
        # HF fractions
        {
            "name": "HFHadronFraction",
            "label": r"PF HF hadron fraction",
            "scale": "log",
            "color": "mediumorchid",
            "marker": "s",
            "marker_style": "empty",
        },
        {
            "name": "HFEMFraction",
            "label": r"PF HF electromagnetic fraction",
            "scale": "log",
            "color": "darkgoldenrod",
            "marker": "o",
            "marker_style": "empty",
        },
    ],
    # leading jet pair flavor fractions
    'flavor_fraction': [
        {
            "name": "Flavor_GG",
            "label": r"$\mathrm{g}\mathrm{g}$",
            "scale": "log",
            "color": "orange",
        },
        {
            "name": "Flavor_QG",
            "label": r"$\mathrm{q}\mathrm{g}$, $\mathrm{g}\mathrm{q}$",
            "scale": "log",
            "color": "#328DCA",
        },
        {
            "name": "Flavor_QQ_pp_ii",
            "label": r"$\mathrm{q}_\mathrm{i} \mathrm{q}_\mathrm{i}$",
            "scale": "log",
            "color": "lightgreen",
        },
        {
            "name": "Flavor_QQ_pp_ij",
            "label": r"$\mathrm{q}_\mathrm{i} \mathrm{q}_\mathrm{j}$",
            "scale": "log",
            "color": "forestgreen",
        },
        {
            "name": "Flavor_QQ_ap_ii",
            "label": r"$\mathrm{q}_\mathrm{i} \overline{\mathrm{q}}_\mathrm{i}$",
            "scale": "log",
            "color": "salmon",
        },
        {
            "name": "Flavor_QQ_ap_ij",
            "label": r"$\mathrm{q}_\mathrm{i} \overline{\mathrm{q}}_\mathrm{j}$",
            "scale": "log",
            "color": "firebrick",
        },
        {
            "name": "Flavor_QQ_aa_ii",
            "label": r"$\overline{\mathrm{q}}_\mathrm{i} \overline{\mathrm{q}}_\mathrm{i}$",
            "scale": "log",
            "color": "plum",
        },
        {
            "name": "Flavor_QQ_aa_ij",
            "label": r"$\overline{\mathrm{q}}_\mathrm{i} \overline{\mathrm{q}}_\mathrm{j}$",
            "scale": "log",
            "color": "mediumorchid",
        },
    ],
}


# define LaTeX labels for some quantities
_QUANTITY_LABELS = {
    'mpf' : 'MPF',
    'ptbalance' : '$p_{\\mathrm{T}}$ balance',
    'met' : '$E_{\\mathrm{T}}^{\\mathrm{miss.}}}$ / GeV',
    'metphi' : '$\\phi (E_{\\mathrm{T}}^{\\mathrm{miss.}})$',
    #'npumean' : '$\\langle n_{\\mathrm{PU}} \\rangle$',
    'npumean' : 'Expected pile-up $\\mu$',
    'npv' : '$n_{\\mathrm{PV}}$',
    'zmass' : '$m^{\\mathrm{Z}}$ / GeV',
    'rho' : 'Pile-up density $\\rho$ / GeV',
    'run2016' : 'Run number (2016)',
    'run2017' : 'Run number (2017)',
    'run2018' : 'Run number (2018)',
}
_QUANTITY_SCALES = {}
# construct labels for some quantities programatically
for _o in ('Z', 'jet1', 'jet2', 'jet3'):
    for _p, _pl, _pu in zip(
        ['pt', 'eta', 'phi'],
        ['p_{\\mathrm{T}}', '\\eta', '\\phi'],
        ['GeV', None, None]):

        _QUANTITY_LABELS[_o.lower()+_p] = "${prop}^{{\\mathrm{{{obj}}}}}${unit}".format(
            obj=_o,
            prop=_pl,
            unit=' / {}'.format(_pu) if _pu is not None else '',
        )

        # log scale x axis on all pt plots
        if _p == 'pt':
            _QUANTITY_SCALES[_o.lower()+_p] = 'log'

# build basic `quantity` expansion from Lumberjack config
EXPANSIONS['quantity'] = [
    {
        'name' : _qn,
        'label' : _QUANTITY_LABELS.get(_qn, _qn),
        'scale' : _QUANTITY_SCALES.get(_qn, 'linear'),
        'range' : _q.range,
        'mean_range' : _LOOKUP_MEAN_RANGE.get(_qn, _uniform_range(_q)),
        'profile_range' : _LOOKUP_PROFILE_RANGE.get(_qn, _uniform_range(_q)),
        'expected_values' : [_LOOKUP_EXPECTED_VALUE[_qn]] if _qn in _LOOKUP_EXPECTED_VALUE else [],
    }
    for _qn, _q in QUANTITIES['global'].iteritems()  # TODO: data/mc-specific quantities
]


# programatically fill in the defined quantity ranges for 'occupancy' axes
for _expansion in EXPANSIONS['occupancy']:
    _expansion.setdefault('x_range', QUANTITIES['global'][_expansion['x_quantity']].range)
    _expansion.setdefault('y_range', QUANTITIES['global'][_expansion['y_quantity']].range)


# merge 'run' expansion for all years (for lookup purposes)
EXPANSIONS['run'] = EXPANSIONS['run2016'] + EXPANSIONS['run2017'] + EXPANSIONS['run2018']
