import itertools


TASKS = {

    "Combination" : {
        "splittings": ["eta", "alpha_inclusive"],
        "histograms" : [
            "zpt"  # no weight
        ],
        "profiles" : [
            "zpt:{}@weight".format(_qname)
            for _qname in ("zpt", "zmass", "ptbalance", "mpf", "rawmpf", "npumean", "rho", "npv")
        ] + ["npumean:rho@weight", "npumean:npv@weight", "npumean:npumean@weight"]
    },

    "CombinationUnweighted" : {
        "splittings": ["eta", "alpha_inclusive"],
        "histograms" : [
            "zpt"
        ],
        "profiles" : [
            "zpt:{}".format(_qname)
            for _qname in ("zpt", "zmass", "ptbalance", "mpf", "rawmpf", "npumean", "rho", "npv")
        ] + ["npumean:rho", "npumean:npv", "npumean:npumean"]
    },

    "Shape" : {
        "splittings": ["eta_wide_barrel"],
        "histograms" : [
                "{}{}@weight".format(_prefix, _suffix)
                for _prefix in ("z", "jet1", "jet2", "jet3")
                for _suffix in ("pt", "eta", "phi")
            ] +
            ["{}@weight".format(_q) for _q in ("zmass", "met", "metphi", "mpf", "ptbalance", "rho", "npumean", "npv")] +
            [
                "zpt:{}{}@weight".format(_prefix, _suffix)
                for _prefix in ("z", "jet1", "jet2", "jet3")
                for _suffix in ("pt", "eta", "phi")
            ] +
            ["zpt:{}@weight".format(_q) for _q in ("zmass", "met", "metphi", "mpf", "ptbalance", "rho", "npumean", "npv")],
        "profiles" : [
            "zpt:{}{}@weight".format(_prefix, _suffix)
            for _prefix in ("z", "jet1", "jet2", "jet3")
            for _suffix in ("pt", "eta", "phi")
        ] + ["zpt:{}@weight".format(_q) for _q in ("zmass", "met", "metphi", "mpf", "ptbalance", "rho", "npumean", "npv")],
    },

    "ShapeUnweighted" : {
        "splittings": ["eta_wide_barrel"],
        "histograms" : [
                "{}{}".format(_prefix, _suffix)
                for _prefix in ("z", "jet1", "jet2", "jet3")
                for _suffix in ("pt", "eta", "phi")
            ] +
            ["zmass", "met", "metphi", "mpf", "ptbalance", "rho", "npumean", "npv"] +
            [
                "zpt:{}{}".format(_prefix, _suffix)
                for _prefix in ("z", "jet1", "jet2", "jet3")
                for _suffix in ("pt", "eta", "phi")
            ] +
            ["zpt:{}".format(_q) for _q in ("zmass", "met", "metphi", "mpf", "ptbalance", "rho", "npumean", "npv")],
        "profiles" : [
            "zpt:{}{}".format(_prefix, _suffix)
            for _prefix in ("z", "jet1", "jet2", "jet3")
            for _suffix in ("pt", "eta", "phi")
        ] + ["zpt:{}".format(_q) for _q in ("zmass", "met", "metphi", "mpf", "ptbalance", "rho", "npumean", "npv")],
    },

    "Extrapolation" : {
        "splittings": ["eta_wide_barrel", "zpt"],
        "histograms" :
            [
                "alpha:{}{}".format(_prefix, _suffix)
                for _prefix in ("z", "jet1", "jet2", "jet3")
                for _suffix in ("pt", "eta", "phi")
            ] +
            ["alpha:{}".format(_q) for _q in ("zmass", "met", "metphi", "mpf", "ptbalance", "rho", "npumean", "npv")],
        "profiles" : [
            "alpha:{}{}".format(_prefix, _suffix)
            for _prefix in ("z", "jet1", "jet2", "jet3")
            for _suffix in ("pt", "eta", "phi")
        ] + ["alpha:{}".format(_q) for _q in ("zmass", "met", "metphi", "mpf", "ptbalance", "rho", "npumean", "npv")],
    },

    "Occupancy" : {
        "splittings": ["zpt"],
        "histograms" : [
            "{0}eta:{0}phi".format(_prefix, _suffix)
            for _prefix in ("jet1", "jet2", "jet3", "z")
        ] + [
            "{0}pt:{0}eta".format(_prefix, _suffix)
            for _prefix in ("jet1", "jet2", "jet3", "z")
        ],
    },

    "TimeDependence_Run2018" : {
        "splittings": ["eta_wide_barrel"],
        "histograms" :
            [
                "run2018:{}{}".format(_prefix, _suffix)
                for _prefix in ("z", "jet1", "jet2", "jet3")
                for _suffix in ("pt", "eta", "phi")
            ] +
            ["run2018:{}".format(_q) for _q in ("zmass", "met", "metphi", "mpf", "ptbalance", "rho", "npumean", "npv")],
        "profiles" : [
            "run2018:{}{}".format(_prefix, _suffix)
            for _prefix in ("z", "jet1", "jet2", "jet3")
            for _suffix in ("pt", "eta", "phi")
        ] + ["run2018:{}".format(_q) for _q in ("zmass", "met", "metphi", "mpf", "ptbalance", "rho", "npumean", "npv")],
    },
}

# -- add run period-specific tasks
for _year in ("2016", "2017", "2018", "2018ABC", "2018D", "2018ABCD", "2017BCDEF", "2016BCDEFGH"):
    TASKS["CombinationData{}".format(_year)] = dict(
        TASKS["Combination"],
        splittings=["run{}".format(_year)] + TASKS["Combination"]["splittings"]
    )
    for _task in ("Extrapolation", "Shape", "Occupancy"):
        TASKS["{}_Run{}".format(_task, _year)] = dict(
            TASKS[_task],
            splittings=["run{}".format(_year)] + TASKS[_task]["splittings"]
        )
    if '2018' in _year and _year != '2018':
        TASKS["TimeDependence_Run{}".format(_year)] = dict(
            TASKS['TimeDependence_Run2018'],
            splittings=["run{}".format(_year)] + TASKS['TimeDependence_Run2018']["splittings"]
        )


# -- add MC-specific
TASKS["CombinationMC"] = dict(
    TASKS["Combination"],
    splittings=["runMC"] + TASKS["Combination"]["splittings"]
)
TASKS["CombinationUnweightedMC"] = dict(
    TASKS["CombinationUnweighted"],
    splittings=["runMC"] + TASKS["Combination"]["splittings"]
)
for _task in ("Extrapolation", "Shape", "Occupancy"):
    TASKS["{}_MC".format(_task)] = dict(
        TASKS[_task],
        splittings=["runMC"] + TASKS[_task]["splittings"]
    )
