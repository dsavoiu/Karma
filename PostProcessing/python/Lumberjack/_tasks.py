import itertools


TASKS = {

    # -- DATA --

    "EventYield" : {
        "splittings": ["ybys_narrow"],
        "histograms" : (
            ["{}_{}".format(_qbasename, _qbinning) for (_qbasename, _qbinning) in itertools.product(['jet1pt', 'jet12ptave', 'jet12mass'], ['wide', 'narrow'])]
            + ["metOverSumET", "jet1phi", "count"]
        ),
    },

    # TODO: differentiate between AK4, AK8 and dijet triggers...
    #"TriggerEfficiencies" : {
    #    "splittings": ["ybys_narrow", "triggers_exclusive"],
    #    "profiles" : (
    #        ["{}_{}:jet1HLTAssignedPathEfficiency".format(_qbasename, _qbinning) for (_qbasename, _qbinning) in itertools.product(['jet1pt', 'jet12ptave', 'jet12mass'], ['wide', 'narrow'])]
    #        + ["metOverSumET:jet1HLTAssignedPathEfficiency"]
    #    ),
    #},

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

    "EventYieldMC" : {
        "splittings": ["ybys_narrow", "mc_subsamples"],
        "histograms" : (
            [
                "{}_{}{}".format(_qbasename, _qbinning, _qweight)
                for (_qbasename, _qbinning, _qweight) in itertools.product(
                    ['jet1pt', 'jet12ptave', 'jet12mass', 'jet1MatchedGenJetPt', 'jet12MatchedGenJetPairPtAve', 'jet12MatchedGenJetPairMass'],
                    ['wide', 'narrow'],
                    ["", "@weightForStitching"]
                )
            ] + [
                "{}{}".format(_qbasename, _qweight)
                for (_qbasename, _qweight) in itertools.product(
                    ['metOverSumET', 'jet1phi', 'count'],
                    ["", "@weightForStitching"]
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
                    ['jet1MatchedGenJetPt', 'jet12MatchedGenJetPairPtAve', 'jet12MatchedGenJetPairMass'],
                    ['jet1pt',              'jet12ptave',                  'jet12mass'                 ],
                ),
                zip(
                    ['wide', 'wide',   'narrow'],
                    ['wide', 'narrow', 'narrow'],
                )
            )
        ],
        "profiles" : [
            "{}_{}:{}_{}".format(_q1, _qbinning1, _q2, _qbinning2)
            for ((_q1, _q2), (_qbinning1, _qbinning2)) in itertools.product(
                zip(
                    ['jet1MatchedGenJetPt', 'jet12MatchedGenJetPairPtAve', 'jet12MatchedGenJetPairMass'],
                    ['jet1pt',              'jet12ptave',                  'jet12mass'                 ],
                ),
                zip(
                    ['wide', 'wide',   'narrow'],
                    ['wide', 'narrow', 'narrow'],
                )
            )
        ],
    },

    "Flavors" : {
        "splittings": ["ybys_narrow", "mc_subsamples", "flavors"],
        "histograms" : ([
            "{}_{}".format(_qbasename, _qbinning)
            for (_qbasename, _qbinning) in itertools.product(
                ['jet1pt', 'jet12ptave', 'jet12mass'],
                ['wide', 'narrow'],
            )
        ]),
    },
}

TASKS['OccupancyMC'] = dict(TASKS['Occupancy'], splittings=["ybys_narrow"])
TASKS['PFEnergyFractionsMC'] = dict(TASKS['PFEnergyFractions'], splittings=["ybys_narrow"])

TASKS['Occupancy_PFJetTriggers'] = dict(TASKS['Occupancy'], splittings=["ybys_narrow", "triggers_ak4"])
TASKS['Occupancy_DiPFJetAveTriggers'] = dict(TASKS['Occupancy'], splittings=["ybys_narrow", "triggers_dijet"])

TASKS['EventYield_PFJetTriggers'] = dict(TASKS['EventYield'], splittings=["ybys_narrow", "triggers_ak4"])
TASKS['EventYield_DiPFJetAveTriggers'] = dict(TASKS['EventYield'], splittings=["ybys_narrow", "triggers_dijet"])


