import numpy as np

from Karma.PostProcessing.Lumberjack import Quantity

ROOT_MACROS = ""

_N_BINS_DEFAULT = 50

# specification of quantities
# NOTE: a 'Define' will be applied to the data frame for every quantity whose name is different from its expression
QUANTITIES = {
    'global': {
        'run2016': Quantity(
            name='run2016',
            expression='run',
            binning=np.linspace(272007, 284044, _N_BINS_DEFAULT)
        ),
        'run2017': Quantity(
            name='run2017',
            expression='run',
            binning=np.linspace(297020, 306462, _N_BINS_DEFAULT)
        ),
        'run2018': Quantity(
            name='run2018',
            expression='run',
            # bins with roughly equal integrated luminosity
            binning=[315257, 315642, 315770, 316082, 316202, 316472, 316717, 316994, #runA
                     317080, 317213, 317320, 317392, 317527, 317640, 317661, 319077, #runB
                     319337, 319456, 319528, 319639, 319756, 319950, 320023, 320065, #runC
                     320673, 321122, 321434, 321919, 322324, 323726, 324729, 325172] #runD
        ),

        # for counting experiments
        'count': Quantity(
            name='count',
            expression='0.5',
            binning=(0, 1)
        ),

        'zpt': Quantity(
            name='zpt',
            expression='zpt',
            binning=(30, 40, 50, 60, 85, 105, 130, 175, 230, 300, 400, 500, 700, 1000, 1500),
        ),
        'jet1pt': Quantity(
            name='jet1pt',
            expression='jet1pt',
            binning=(10, 20, 30, 40, 50, 60, 85, 105, 130, 175, 230, 300, 400, 500, 700, 1000, 1500, 2000, 5000),
        ),
        'jet2pt': Quantity(
            name='jet2pt',
            expression='jet2pt',
            binning=np.linspace(5, 200, _N_BINS_DEFAULT),
        ),
        'jet3pt': Quantity(
            name='jet3pt',
            expression='jet3pt',
            binning=np.linspace(5, 200, _N_BINS_DEFAULT),
        ),
        'zmass': Quantity(
            name='zmass',
            expression='zmass',
            binning=np.linspace(70, 110, _N_BINS_DEFAULT),
        ),
        'met': Quantity(
            name='met',
            expression='met',
            binning=np.linspace(0, 100, _N_BINS_DEFAULT),
        ),
        'metphi': Quantity(
            name='metphi',
            expression='metphi',
            binning=np.linspace(-np.pi, np.pi, 41),
        ),

        # responses
        'mpf': Quantity(
            name='mpf',
            expression='mpf',
            binning=np.linspace(0, 2, 50),
        ),
        'rawmpf': Quantity(
            name='rawmpf',
            expression='rawmpf',
            binning=np.linspace(0, 2, 50),
        ),
        'ptbalance': Quantity(
            name='ptbalance',
            expression='jet1pt/zpt',
            binning=np.linspace(0, 2, 50),
        ),
        'alpha': Quantity(
            name='alpha',
            expression='jet2pt/zpt',
            binning=np.linspace(0, 1.0, 50),
        ),

        # pileup quantities
        'rho': Quantity(
            name='rho',
            expression='rho',
            binning=np.linspace(0, 80, 81),
        ),
        'npv': Quantity(
            name='npv',
            expression='npv',
            binning=np.linspace(-0.5, 80.5, 82),
        ),
        'npu': Quantity(
            name='npu',
            expression='npu',
            binning=np.linspace(-0.5, 80.5, 82),
        ),
        'npumean': Quantity(
            name='npumean',
            expression='npumean',
            binning=np.linspace(-0.5, 80.5, 82),
        ),
    }
}

for _prefix in ("z", "jet1", "jet2", "jet3"):
    QUANTITIES['global'].update({
        '{}eta'.format(_prefix): Quantity(
            name='{}eta'.format(_prefix),
            expression='{}eta'.format(_prefix),
            binning=[-5.191, -3.839, -3.489, -3.139, -2.964, -2.853, -2.650, -2.500, -2.322, -2.172, -1.930, -1.653, -1.479, -1.305, -1.044, -0.783, -0.522, -0.261, 0.000, 0.261, 0.522, 0.783, 1.044, 1.305, 1.479, 1.653, 1.930, 2.172, 2.322, 2.500, 2.650, 2.853, 2.964, 3.139, 3.489, 3.839, 5.191],
        ),
        'abs{}eta'.format(_prefix): Quantity(
            name='abs{}eta'.format(_prefix),
            expression='abs({}eta)'.format(_prefix),
            binning=[0.000, 0.261, 0.522, 0.783, 1.044, 1.305, 1.479, 1.653, 1.930, 2.172, 2.322, 2.500, 2.650, 2.853, 2.964, 3.139, 3.489, 3.839, 5.191],
        ),
        '{}phi'.format(_prefix): Quantity(
            name='{}phi'.format(_prefix),
            expression='{}phi'.format(_prefix),
            binning=np.linspace(-np.pi, np.pi, 41),
        ),
    })

# specification of defines to be applied to data frame
DEFINES = {
    # defines to be applied globally
    'global': {
    },
    # defines to be applied for MC samples only
    'mc': {
    },
}


# specification of filters to be applied to data frame
SELECTIONS = {
    'global' : [
    ],
    'zpt' : [
        "zpt>30",
    ],
    'alpha' : [
        "alpha<0.3",
    ],
    'absjet1eta' : [
        "absjet1eta<1.3",
    ],
}

_ALPHA_BIN_EDGES = [0.0, 0.1, 0.15, 0.2, 0.3, 0.4]

_ETA_BIN_EDGES_BARREL = (0, 1.3)
_ETA_BIN_EDGES_WIDE = [0, 0.783, 1.305, 1.93,
                      2.5, 2.964, 3.2, 5.191]

_ETA_BIN_EDGES = QUANTITIES['global']['absjet1eta'].binning
_ZPT_BIN_EDGES = QUANTITIES['global']['zpt'].binning

# specification of ways to split sample into subsamples
SPLITTINGS = {
    'run2016' : {
        "Run2016B" : dict(run=(272007, 275376+1)),  # add one to upper bound to include last value
        "Run2016C" : dict(run=(275657, 276283+1)),
        "Run2016D" : dict(run=(276315, 276811+1)),
        "Run2016E" : dict(run=(276831, 277420+1)),
        "Run2016F" : dict(run=(277772, 278808+1)),
        "Run2016G" : dict(run=(278820, 280385+1)),
        "Run2016H" : dict(run=(280919, 284044+1)),
        "Run2016BCDEFGH" : dict(run=(272007, 284044+1)),
    },
    'run2017' : {
        "Run2017B" : dict(run=(297020, 299329+1)),
        "Run2017C" : dict(run=(299337, 302029+1)),
        "Run2017D" : dict(run=(302030, 303434+1)),
        "Run2017E" : dict(run=(303435, 304826+1)),
        "Run2017F" : dict(run=(304911, 306462+1)),
        "Run2017BCDEF" : dict(run=(297020, 306462+1)),
    },
    'run2018' : {
        "Run2018A" : dict(run=(315252, 316995+1)),
        "Run2018B" : dict(run=(316998, 319312+1)),
        "Run2018C" : dict(run=(319313, 320393+1)),
        "Run2018D" : dict(run=(320394, 325273+1)),
        "Run2018ABCD" : dict(run=(315252, 325273+1)),
    },
    'run2018ABC' : {
        "Run2018A" : dict(run=(315252, 316995+1)),
        "Run2018B" : dict(run=(316998, 319312+1)),
        "Run2018C" : dict(run=(319313, 320393+1)),
        "Run2018ABC" : dict(run=(315252, 320393+1)),
    },
    'run2018D' : {
        "Run2018D" : dict(run=(320394, 325273+1)),
    },
    # dummy splitting for MC
    'runMC' : {
        "MC" : dict(run=1),
    },
}
SPLITTINGS['run2018ABCD'] = SPLITTINGS['run2018']
SPLITTINGS['run2017BCDEF'] = SPLITTINGS['run2017']
SPLITTINGS['run2016BCDEFGH'] = SPLITTINGS['run2016']
SPLITTINGS['iov2018'] = SPLITTINGS['run2018']
SPLITTINGS['iov2017'] = {
    "Run2017B" : dict(run=(297020, 299329+1)),
    "Run2017C" : dict(run=(299337, 302029+1)),
    "Run2017DE" : dict(run=(302030, 304826+1)),
    "Run2017F" : dict(run=(304911, 306462+1)),
    "Run2017BCDEF" : dict(run=(297020, 306462+1)),

}
SPLITTINGS['iov2016'] = {
    "Run2016BCD" : dict(run=(272007, 276811+1)),
    "Run2016EFearly" : dict(run=(276831, 278801+1)),
    "Run2016FlateGH" : dict(run=(278802, 284044+1)),
    "Run2016BCDEFGH" : dict(run=(272007, 284044+1)),

}


# -- alpha binning
SPLITTINGS['alpha_exclusive'] = dict({
    "alpha_{:04d}_{:04d}".format(int(_lo*1e2), int(_hi*1e2)) : dict(alpha=(_lo, _hi))
    for _lo, _hi in zip(_ALPHA_BIN_EDGES[:-1], _ALPHA_BIN_EDGES[1:])
}, **{"alpha_all" : dict()})
SPLITTINGS['alpha_inclusive'] = dict({
    "alpha_0_{:04d}".format(int(_hi*1e2)) : dict(alpha=(0, _hi))
    for _hi in _ALPHA_BIN_EDGES[1:]
}, **{"alpha_all" : dict()})
SPLITTINGS['alpha'] = dict(SPLITTINGS['alpha_exclusive'], **SPLITTINGS['alpha_inclusive'])


# -- eta binning
SPLITTINGS['eta_wide'] = dict({
    "absEta_{:04d}_{:04d}".format(int(_lo*1e3), int(_hi*1e3)) : dict(absjet1eta=(_lo, _hi))
    for _lo, _hi in zip(_ETA_BIN_EDGES_WIDE[:-1], _ETA_BIN_EDGES_WIDE[1:])
}, **{"absEta_all" : dict(absjet1eta=(0, 5.191))})
SPLITTINGS['eta_narrow'] = dict({
    "absEta_{:04d}_{:04d}".format(int(_lo*1e3), int(_hi*1e3)) : dict(absjet1eta=(_lo, _hi))
    for _lo, _hi in zip(_ETA_BIN_EDGES[:-1], _ETA_BIN_EDGES[1:])
}, **{"absEta_all" : dict(absjet1eta=(0, 5.191))})

assert len(_ETA_BIN_EDGES_BARREL) == 2
SPLITTINGS['eta'] = {"absEta_{:04d}_{:04d}".format(int(_ETA_BIN_EDGES_BARREL[0]*1e3), int(_ETA_BIN_EDGES_BARREL[1]*1e3)) : dict(absjet1eta=_ETA_BIN_EDGES_BARREL)}
SPLITTINGS['eta'].update(SPLITTINGS['eta_narrow'])
SPLITTINGS['eta'].update(SPLITTINGS['eta_wide'])

SPLITTINGS['eta_wide_barrel'] = {"absEta_{:04d}_{:04d}".format(int(_ETA_BIN_EDGES_BARREL[0]*1e3), int(_ETA_BIN_EDGES_BARREL[1]*1e3)) : dict(absjet1eta=_ETA_BIN_EDGES_BARREL)}
SPLITTINGS['eta_wide_barrel'].update(SPLITTINGS['eta_wide'])


# -- zpt binning
SPLITTINGS['zpt'] = dict({
    "zpt_{:d}_{:d}".format(int(_lo), int(_hi)) : dict(zpt=(_lo, _hi))
    for _lo, _hi in zip(_ZPT_BIN_EDGES[:-1], _ZPT_BIN_EDGES[1:])
}, **{"zpt_gt_30" : dict(zpt=(30, 100000))})
