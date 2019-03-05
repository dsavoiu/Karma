import itertools

from .definitions import QUANTITIES


__all__ = ["TASKS"]


TASKS = {

    # -- DATA --

    "Count" : {
        "splittings": ["ybys_narrow"],
        "histograms" : ["count"],
    },

    "EventYield" : {
        "splittings": ["ybys_narrow"],
        "histograms" : (
            ["{}_{}".format(_qbasename, _qbinning) for (_qbasename, _qbinning) in itertools.product(['jet1pt', 'jet12ptave', 'jet12mass'], ['wide', 'narrow'])]
            + ["metOverSumET", "jet1phi", "count"]
        ),
    },

    "TriggerEfficienciesAK4" : {
        "splittings": ["ybys_narrow", "trigger_efficiencies_ak4"],
        "histograms" : (
            ["{}_{}".format(_qbasename, _qbinning) for (_qbasename, _qbinning) in itertools.product(['jet1pt', 'jet12ptave', 'jet12mass'], ['wide', 'narrow'])]
        ),
    },

    "TriggerEfficienciesAK8" : {
        "splittings": ["ybys_narrow", "trigger_efficiencies_ak8"],
        "histograms" : (
            ["{}_{}".format(_qbasename, _qbinning) for (_qbasename, _qbinning) in itertools.product(['jet1pt', 'jet12ptave', 'jet12mass'], ['wide', 'narrow'])]
        ),
    },

    "TriggerEfficienciesDijet" : {
        "splittings": ["ybys_narrow", "trigger_efficiencies_dijet"],
        "histograms" : (
            ["{}_{}".format(_qbasename, _qbinning) for (_qbasename, _qbinning) in itertools.product(['jet1pt', 'jet12ptave', 'jet12mass'], ['wide', 'narrow'])]
        ),
    },

    "Occupancy" : {
        "splittings": ["ybys_narrow"],
        "histograms" : ([
            "{}:{}_{}".format(_q2, _qbasename, _qbinning)
            for (_qbasename, _qbinning) in itertools.product(['jet1pt', 'jet12ptave', 'jet12mass'], ['wide', 'narrow'])
            for _q2 in ['jet1eta', 'jet2eta', 'yboost', 'ystar']
        ] + [
            "{}_{}:{}".format(_qbasename, _qbinning, _q2)
            for (_qbasename, _qbinning) in itertools.product(['jet1pt', 'jet12ptave', 'jet12mass'], ['wide', 'narrow'])
            for _q2 in ['jet1eta', 'jet2eta', 'yboost', 'ystar']
        ] + [
            "{}:{}".format(_qx, _qy)
            for (_qx, _qy) in zip(
                ['jet1eta', 'jet2eta', 'jet1eta', 'jet2eta', 'jet1y', 'absjet1y', 'ystar',  "jet1pt_wide", "jet1pt_narrow"],
                ['jet1phi', 'jet2phi', 'jet1y',   'jet2y'  , 'jet2y', 'absjet2y', 'yboost', "jet2pt_wide", "jet2pt_narrow"]
            )
        ] + [
            "{}:{}".format(_qx, _qy)
            for (_qx, _qy) in zip(
                ['jet1phi', 'jet2phi', 'jet1y',   'jet2y'  , 'jet2y', 'absjet2y', 'yboost', "jet2pt_wide", "jet2pt_narrow"],
                ['jet1eta', 'jet2eta', 'jet1eta', 'jet2eta', 'jet1y', 'absjet1y', 'ystar',  "jet1pt_wide", "jet1pt_narrow"]
            )
        ]),
    },

    "MainShapes" : {
        "splittings": ["ybys_narrow",],
        "histograms" : [
            "{}{}".format(_qn, _ws)
            for (_qn, _ws) in itertools.product(
                ["jet12ptave_wide", "jet12mass_wide"],
                ["", "@assignedTriggerLuminosityWeight"]
            )
        ],
    },

    "AllShapes" : {
        "splittings": ["ybys_narrow",],
        "histograms" : [
            "{}{}".format(_qn, _ws)
            for (_qn, _ws) in itertools.product(
                QUANTITIES['global'].keys() + QUANTITIES['data'].keys(),  # all quantities
                ["", "@assignedTriggerLuminosityWeight"]
            )
        ],
    },

    "PileupShapes" : {
        "splittings": ["ybys_narrow"],
        "histograms" : ['npv', 'nPUMean']
    },

    "PFEnergyFractions" : {
        "splittings": ["ybys_narrow"],
        "profiles" : ([
            "{}_{}:jet1{}Fraction".format(_qbasename, _qbinning, _q_pf_frac)
            for (_qbasename, _qbinning, _q_pf_frac) in itertools.product(
                ['jet1pt', 'jet12ptave', 'jet12mass'],
                ['wide', 'narrow'],
                ['NeutralHadron', 'ChargedHadron', 'Muon', 'Photon', 'Electron', 'HFHadron', 'HFEM']
            )
        ]),
        "histograms" : ([
            "{}_{}:jet1{}Fraction".format(_qbasename, _qbinning, _q_pf_frac)
            for (_qbasename, _qbinning, _q_pf_frac) in itertools.product(
                ['jet1pt', 'jet12ptave', 'jet12mass'],
                ['wide', 'narrow'],
                ['NeutralHadron', 'ChargedHadron', 'Muon', 'Photon', 'Electron', 'HFHadron', 'HFEM']
            )
        ] + [
            "jet1{}Fraction".format(_q_pf_frac)
            for _q_pf_frac in ['NeutralHadron', 'ChargedHadron', 'Muon', 'Photon', 'Electron', 'HFHadron', 'HFEM']
        ]),
    },

    # -- MC --

    "AllShapesMC" : {
        "splittings": ["ybys_narrow"],
        "histograms" : ["{}{}".format(_qn, _qweight)
            for _qn, _qweight in itertools.product(
              QUANTITIES['global'].keys() + QUANTITIES['mc'].keys(),
              ["", "@generatorWeight"],
            )
        ],
    },
    "AllShapesMCBinned" : {
        "splittings": ["ybys_narrow"],
        "histograms" : ["{}{}".format(_qn, _qweight)
            for _qn, _qweight in itertools.product(
              QUANTITIES['global'].keys() + QUANTITIES['mc'].keys(),
              ["", "@computedWeightForStitching"],
            )
        ],
    },

    "MainShapesMCBinned" : {
        "splittings": ["ybys_narrow",],
        "histograms" : [
            "{}{}".format(_qn, _ws)
            for (_qn, _ws) in itertools.product(
                ["jet12ptave_wide", "jet12mass_wide"],
                ["", "@computedWeightForStitching"],
            )
        ],
    },

    "PileupShapesMC" : {
        "splittings": ["ybys_narrow"],
        "histograms" : ['npv@generatorWeight', 'nPUMean@generatorWeight', 'nPU@generatorWeight']
    },

    "EventYieldMC" : {
        "splittings": ["ybys_narrow"],
        "histograms" : (
            [
                "{}_{}{}".format(_qbasename, _qbinning, _qweight)
                for (_qbasename, _qbinning, _qweight) in itertools.product(
                    ['jet1pt', 'jet12ptave', 'jet12mass', 'jet1MatchedGenJetPt', 'jet12MatchedGenJetPairPtAve', 'jet12MatchedGenJetPairMass'],
                    ['wide', 'narrow'],
                    ["", "@generatorWeight"]
                )
            ] + [
                "{}{}".format(_qbasename, _qweight)
                for (_qbasename, _qweight) in itertools.product(
                    ['metOverSumET', 'jet1phi', 'count'],
                    ["", "@generatorWeight"]
                )
            ]
        ),
    },

    "JetResponse" : {
        "splittings": ["ybys_narrow"],
        "histograms" : [
            "{}_{}".format(_qbasename, _qbinning) for (_qbasename, _qbinning) in itertools.product(
                ['jet1MatchedGenJetPt', 'jet12MatchedGenJetPairPtAve', 'jet12MatchedGenJetPairMass'],
                ['wide', 'narrow']
            )
        ] + [
            "{}_{}:{}_{}".format(_q1, _qbinning1, _q2, _qbinning2)
            for ((_q1, _q2), (_qbinning1, _qbinning2)) in itertools.product(
                zip(
                    ['jet12MatchedGenJetPairPtAve', 'jet12MatchedGenJetPairMass'],
                    ['jet12ptave',                  'jet12mass'                 ],
                ),
                zip(
                    ['wide'],
                    ['wide'],
                )
            )
        ],
        "profiles" : [
            "{}_{}:{}_{}".format(_q1, _qbinning1, _q2, _qbinning2)
            for ((_q1, _q2), (_qbinning1, _qbinning2)) in itertools.product(
                zip(
                    ['jet12MatchedGenJetPairPtAve', 'jet12MatchedGenJetPairMass'],
                    ['jet12ptave',                  'jet12mass'                 ],
                ),
                zip(
                    ['wide'],
                    ['wide'],
                )
            )
        ],
    },

    "Flavors" : {
        "splittings": ["ybys_narrow", "flavors"],
        "histograms" : ([
            "{}_{}".format(_qbasename, _qbinning)
            for (_qbasename, _qbinning) in itertools.product(
                ['jet1pt', 'jet12ptave', 'jet12mass'],
                ['wide', 'narrow'],
            )
        ]),
    },

    "QCDSubprocesses" : {
        "splittings": ["ybys_narrow", "qcd_subprocesses"],
        "histograms" : ([
            "{}_{}".format(_qbasename, _qbinning)
            for (_qbasename, _qbinning) in itertools.product(
                #['jet12ptave'],
                #['narrow'],
                ['jet1pt', 'jet12ptave', 'jet12mass',
                 'jet1MatchedGenJetPt', 'jet12MatchedGenJetPairPtAve', 'jet12MatchedGenJetPairMass'],
                ['wide', 'narrow'],
            )
        ]),
    },

    "QCDSubprocesses_SubsampleWeighted" : {
        "splittings": ["ybys_narrow", "qcd_subprocesses"],
        "histograms" : ([
            "{}_{}@weightForStitching".format(_qbasename, _qbinning)
            for (_qbasename, _qbinning) in itertools.product(
                ['jet1pt', 'jet12ptave', 'jet12mass',
                 'jet1MatchedGenJetPt', 'jet12MatchedGenJetPairPtAve', 'jet12MatchedGenJetPairMass'],
                ['wide', 'narrow'],
            )
        ]),
    },
}

TASKS['OccupancyMC'] = dict(TASKS['Occupancy'], splittings=["ybys_narrow"])
TASKS['PFEnergyFractionsMC'] = dict(TASKS['PFEnergyFractions'], splittings=["ybys_narrow"])

TASKS['Occupancy_AK4PFJetTriggers'] = dict(TASKS['Occupancy'], splittings=["ybys_narrow", "triggers_ak4"])
TASKS['Occupancy_AK8PFJetTriggers'] = dict(TASKS['Occupancy'], splittings=["ybys_narrow", "triggers_ak8"])
TASKS['Occupancy_DiPFJetAveTriggers'] = dict(TASKS['Occupancy'], splittings=["ybys_narrow", "triggers_dijet"])

TASKS['EventYield_AK4PFJetTriggers'] = dict(TASKS['EventYield'], splittings=["ybys_narrow", "triggers_ak4"])
TASKS['EventYield_AK8PFJetTriggers'] = dict(TASKS['EventYield'], splittings=["ybys_narrow", "triggers_ak8"])
TASKS['EventYield_DiPFJetAveTriggers'] = dict(TASKS['EventYield'], splittings=["ybys_narrow", "triggers_dijet"])

TASKS['EventYieldMC_Subsamples'] = dict(TASKS['EventYieldMC'], splittings=["ybys_narrow", "mc_subsamples"])

TASKS['Flavors_Subsamples'] = dict(TASKS['Flavors'], splittings=["ybys_narrow", "mc_subsamples", "flavors"])
TASKS['QCDSubprocesses_Subsamples'] = dict(TASKS['QCDSubprocesses'], splittings=["ybys_narrow@4", "mc_subsamples", "qcd_subprocesses"])
