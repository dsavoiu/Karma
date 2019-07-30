import itertools

_SHAPE_QUANTITIES = [
        "{}{}".format(_prefix, _suffix)
        for _prefix in ("z", "jet1", "jet2", "jet3")
        for _suffix in ("pt", "eta", "phi")
    ] + [
        "{}".format(_q)
        for _q in ("zmass", "met", "metphi", "mpf", "ptbalance", "rho", "npumean", "npv", "alpha",
                   "zJet1DeltaEta", "zJet1DeltaPhi", "zJet1DeltaR",
                   "jet12DeltaEta", "jet12DeltaPhi", "jet12DeltaR")
    ]

TASKS = {

    # -- assortment of objects specifically needed for creating combination files

    "Combination" : {
        "splittings": ["eta", "alpha_inclusive"],
        "histograms" : [
            "zpt"  # no weight here!
        ],
        "profiles" : [
            "zpt:{}@weight".format(_qname)
            for _qname in ("zpt", "zmass", "ptbalance", "mpf", "rawmpf", "npumean", "rho", "npv")
        ] + ["npumean:rho@weight", "npumean:npv@weight", "npumean:npumean@weight"]
    },

    # -- basic tasks

    # underlying histograms (1D)
    "Shape" : {
        "splittings": [],  # tasks for different splittings created below
        "histograms" : [
            "{}@weight".format(_q)
            for _q in _SHAPE_QUANTITIES
        ],
    },

    # means and standard deviations of quantities as a function of 'zpt'
    "ProfileZPt" : {
        "splittings": [],  # tasks for different splittings created below
        "profiles" : [
            "zpt:{}@weight".format(_q)
            for _q in _SHAPE_QUANTITIES
        ],
    },

    # means and standard deviations of quantities as a function of 'absjet1eta'
    "ProfileEta" : {
        "splittings": [],  # tasks for different splittings created below
        "profiles" : [
            "absjet1eta:{}@weight".format(_q)
            for _q in _SHAPE_QUANTITIES
        ],
    },

    # means and standard deviations of quantities as a function of 'alpha'
    "Extrapolation" : {
        "splittings": [],  # tasks for different splittings created below
        "histograms" : [
            "alpha:{}@weight".format(_q)
            for _q in ("mpf", "ptbalance", "jet12DeltaEta", "jet12DeltaPhi", "jet12DeltaR")
        ],
        "profiles" : [
            "alpha:{}@weight".format(_q)
            for _q in ("mpf", "ptbalance", "jet12DeltaEta", "jet12DeltaPhi", "jet12DeltaR", "alpha")
        ],
    },

    # means and standard deviations of quantities as a function of 'run_<year>'
    "TimeDependence" : {
        "splittings": [],  # tasks for different splittings created below
        "histograms" : [
            "run_year:{}".format(_q)  # no weight (always 1 in data anyway)
            for _q in _SHAPE_QUANTITIES
        ],
        "profiles" : [
            "run_year:{}".format(_q)  # no weight (always 1 in data anyway)
            for _q in _SHAPE_QUANTITIES
        ],
    },

    # 2D maps for Z boson and jets
    "Occupancy" : {
        "splittings": [],  # tasks for different splittings created below
        "histograms" : [
            "{0}eta:{0}phi@weight".format(_prefix, _suffix)
            for _prefix in ("jet1", "jet2", "jet3", "z")
        ] + [
            "{0}pt:{0}eta@weight".format(_prefix, _suffix)
            for _prefix in ("jet1", "jet2", "jet3", "z")
        ] + [
            "{0}DeltaEta:{0}DeltaPhi@weight".format(_pair_spec)
            for _pair_spec in ("zJet1", "jet12")
        ],
    },

}

# -- add unweighted versions for some tasks
for _task in list(TASKS):
    if not any((_task.startswith(_prefix) for _prefix in ('Shape', 'Profile', 'Extrapolation', 'Occupancy'))):
        continue

    TASKS["{}Unweighted".format(_task)] = dict(
        splittings=TASKS[_task]["splittings"],
        histograms=[
            _h.replace('@weight', '')
            for _h in TASKS[_task].get("histograms", [])
        ],
        profiles=[
            _p.replace('@weight', '')
            for _p in TASKS[_task].get("profiles", [])
        ],
    )

# -- add tasks with explicit run period splitting
for _task in list(TASKS):
    for _period in ("MC", "2016", "2017", "2018", "2018ABCD", "2017BCDEF", "2016BCDEFGH"):
        # divide into individual run periods
        TASKS["{}_Run{}".format(_task, _period)] = dict(
            TASKS[_task],
            splittings=["run{}".format(_period)] + TASKS[_task]["splittings"],
        )
        # divide into year-specific Intervals of Validity (IOVs)
        if len(_period) == 4:
            TASKS["{}_IOV{}".format(_task, _period)] = dict(
                TASKS[_task],
                splittings=["iov{}".format(_period)] + TASKS[_task]["splittings"],
            )

# -- tasks with explicit splitting ('zpt', 'absjet1eta' or both)
for _task in list(TASKS):

    # 'Combination' tasks already contain the correct splitting
    if _task.startswith('Combination'):
        continue
    # 'Profile' tasks only make sense with the complementary splitting
    elif _task.startswith('ProfileZPt'):
        TASKS[_task+"_EtaBins"] = dict(
            TASKS[_task],
            splittings=TASKS[_task]["splittings"] + ["eta_wide_barrel"],
        )
    elif _task.startswith('ProfileEta'):
        TASKS[_task+"_ZPtBins"] = dict(
            TASKS[_task],
            splittings=TASKS[_task]["splittings"] + ["zpt"],
        )
    # all other tasks can be split in either variable (or both)
    else:
        TASKS[_task+"_ZPtBins"] = dict(
            TASKS[_task],
            splittings=TASKS[_task]["splittings"] + ["zpt"],
        )
        TASKS[_task+"_EtaBins"] = dict(
            TASKS[_task],
            splittings=TASKS[_task]["splittings"] + ["eta_wide_barrel"],
        )
        TASKS[_task+"_EtaBins_ZPtBins"] = dict(
            TASKS[_task],
            splittings=TASKS[_task]["splittings"] + ["eta_wide_barrel", "zpt"],
        )
