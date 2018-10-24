import numpy as np

from ._core import Quantity


# specification of quantities
# NOTE: a 'Define' will be applied to the data frame for every quantity whose name is different from its expression
QUANTITIES = {
    'run': Quantity(
        name='run',
        expression='run',
        binning=np.linspace(278820, 280385, 30)
    ),

    # for counting experiments
    'count': Quantity(
        name='count',
        expression='0.5',
        binning=(0, 1)
    ),

    'metOverSumET': Quantity(
        name='metOverSumET',
        expression='met/sumEt',
        binning=np.linspace(0, 1, 101)
    ),

    # "wide" binning with target resolution/bin_width of 0.5
    'jet1pt_wide': Quantity(
        name='jet1pt_wide',
        expression='jet1pt',
        binning=(60, 80, 106, 137, 174, 215, 264, 321, 384, 461, 539, 631, 731, 845, 966, 1099, 1245, 1407, 1582, 1782, 1977, 2192, 2443, 2681, 2944, 3218, 3518, 3874, 4170, 4827)
    ),
    'jet12mass_wide': Quantity(
        name='jet12mass_wide',
        expression='jet12mass',
        binning=(200, 249, 306, 372, 449, 539, 641, 756, 887, 1029, 1187, 1361, 1556, 1769, 2008, 2273, 2572, 2915, 3306, 3754, 4244, 4805, 5374, 5994, 6672, 7456, 8401, 9607)
    ),
    'jet12ptave_wide': Quantity(
        name='jet12ptave_wide',
        expression='jet12ptave',
        binning=(100, 122, 147, 175, 207, 243, 284, 329, 380, 437, 499, 569, 646, 732, 827, 931, 1046, 1171, 1307, 1458, 1621, 1806, 2003, 2217, 2453, 2702, 2977, 3249, 3557, 3816, 4045)
    ),

    # "narrow" binning with target resolution/bin_width of 1.0
    'jet1pt_narrow': Quantity(
        name='jet1pt_narrow',
        expression='jet1pt',
        binning=(60, 69, 79, 90, 102, 115, 129, 144, 160, 177, 194, 213, 233, 254, 277, 301, 326, 352, 380, 411, 443, 476, 510, 546, 584, 624, 665, 709, 755, 803, 852, 903, 956, 1012, 1070, 1130, 1193, 1258, 1326, 1398, 1472, 1549, 1629, 1712, 1799, 1884, 1971, 2062, 2156, 2256, 2361, 2461, 2562, 2669, 2778, 2893, 3019, 3143, 3267, 3402, 3569, 3715, 3805, 3930, 4084, 4413)
    ),
    'jet12mass_narrow': Quantity(
        name='jet12mass_narrow',
        expression='jet12mass',
        binning=(200, 220, 242, 265, 290, 317, 345, 375, 407, 441, 477, 516, 557, 600, 645, 693, 744, 797, 853, 912, 973, 1036, 1102, 1171, 1243, 1318, 1397, 1480, 1567, 1657, 1750, 1849, 1952, 2060, 2173, 2292, 2418, 2551, 2692, 2842, 3000, 3168, 3346, 3533, 3730, 3933, 4147, 4373, 4612, 4861, 5105, 5355, 5617, 5890, 6174, 6470, 6801, 7141, 7506, 7900, 8396, 8930, 9551, 9951)
    ),
    'jet12ptave_narrow': Quantity(
        name='jet12ptave_narrow',
        expression='jet12ptave',
        binning=(100, 110, 120, 131, 142, 154, 166, 179, 193, 207, 222, 238, 255, 273, 291, 310, 330, 351, 373, 397, 422, 448, 475, 503, 532, 563, 595, 628, 663, 700, 738, 778, 820, 863, 908, 955, 1004, 1055, 1108, 1163, 1220, 1280, 1342, 1406, 1473, 1543, 1615, 1690, 1768, 1850, 1935, 2023, 2114, 2209, 2307, 2410, 2515, 2624, 2738, 2857, 2979, 3104, 3233, 3372, 3517, 3580, 3709, 3810, 3914, 3973)
    ),

    # HLT
    'jet1HLTAssignedPathIndex': Quantity(
        name='jet1HLTAssignedPathIndex',
        expression='jet1HLTAssignedPathIndex',
        binning=np.arange(-1, 12) - 0.5
    ),
    'jet1HLTAssignedPathPrescale': Quantity(
        name='jet1HLTAssignedPathPrescale',
        expression='jet1HLTAssignedPathPrescale',
        binning=np.array([-1, 0, 1, 2, 11, 21, 41, 71, 121]) - 0.5
    ),
    'jet1HLTAssignedPathEfficiency': Quantity(
        name='jet1HLTAssignedPathEfficiency',
        expression='jet1HLTAssignedPathEfficiency',
        binning=np.linspace(0, 1, 25)
    ),

    # other jet quantities
    'jet1y': Quantity(
        name='jet1y',
        expression='jet1y',
        binning=[-5, -3.0, -2.853, -2.650, -2.500, -2.322, -2.172, -1.930, -1.653, -1.479, -1.305, -1.044, -0.783, -0.522, -0.261, 0.000, 0.261, 0.522, 0.783, 1.044, 1.305, 1.479, 1.653, 1.930, 2.172, 2.322, 2.500, 2.650, 2.853, 3.0, 5]
    ),
    'absjet1y': Quantity(
        name='absjet1y',
        expression='abs(jet1y)',
        binning=[0.000, 0.261, 0.522, 0.783, 1.044, 1.305, 1.479, 1.653, 1.930, 2.172, 2.322, 2.500, 2.650, 2.853, 3.0, 5]
    ),
    'jet1phi': Quantity(
        name='jet1phi',
        expression='jet1phi',
        binning=np.linspace(-np.pi, np.pi, 101),  #(-np.pi, np.pi)
    ),

    # fine binning in y*/yb
    'ystar': Quantity(
        name='ystar',
        expression='abs(jet12ystar)',
        binning=np.arange(0, 3.0 + 0.1, 0.1)
    ),
    'yboost': Quantity(
        name='yboost',
        expression='abs(jet12yboost)',
        binning=np.arange(0, 3.0 + 0.1, 0.1)
    ),
}
QUANTITIES.update({
    'jet1eta':          Quantity(name='jet1eta',       expression='jet1eta',       binning=QUANTITIES['jet1y'].binning),
    'absjet1eta':       Quantity(name='absjet1eta',    expression='abs(jet1eta)',  binning=QUANTITIES['absjet1y'].binning),
})
QUANTITIES.update({
    'absjet2y':         Quantity(name='absjet2y',      expression='abs(jet2y)',    binning=QUANTITIES['absjet1y'].binning),
    'absjet2eta':       Quantity(name='absjet2eta',    expression='abs(jet2eta)',  binning=QUANTITIES['absjet1eta'].binning),

    'jet2pt_narrow':    Quantity(name='jet2pt_narrow', expression='jet2pt',        binning=QUANTITIES['jet1pt_narrow'].binning),
    'jet2pt_wide':      Quantity(name='jet2pt_wide',   expression='jet2pt',        binning=QUANTITIES['jet1pt_wide'].binning),
    'jet2phi':          Quantity(name='jet2phi',       expression='jet2phi',       binning=QUANTITIES['jet1phi'].binning),
    'jet2y':            Quantity(name='jet2y',         expression='jet2y',         binning=QUANTITIES['jet1y'].binning),
    'jet2eta':          Quantity(name='jet2eta',       expression='jet2eta',       binning=QUANTITIES['jet1eta'].binning),

    'jet1MatchedGenJetPt_narrow':            Quantity(name='jet1MatchedGenJetPt_narrow',          expression='jet1MatchedGenJetPt',           binning=QUANTITIES['jet1pt_narrow'].binning),
    'jet12MatchedGenJetPairPtAve_narrow':    Quantity(name='jet12MatchedGenJetPairPtAve_narrow',  expression='jet12MatchedGenJetPairPtAve',   binning=QUANTITIES['jet12ptave_narrow'].binning),
    'jet12MatchedGenJetPairMass_narrow':     Quantity(name='jet12MatchedGenJetPairMass_narrow',   expression='jet12MatchedGenJetPairMass',    binning=QUANTITIES['jet12mass_narrow'].binning),

    'jet1MatchedGenJetPt_wide':              Quantity(name='jet1MatchedGenJetPt_wide',            expression='jet1MatchedGenJetPt',           binning=QUANTITIES['jet1pt_wide'].binning),
    'jet12MatchedGenJetPairPtAve_wide':      Quantity(name='jet12MatchedGenJetPairPtAve_wide',    expression='jet12MatchedGenJetPairPtAve',   binning=QUANTITIES['jet12ptave_wide'].binning),
    'jet12MatchedGenJetPairMass_wide':       Quantity(name='jet12MatchedGenJetPairMass_wide',     expression='jet12MatchedGenJetPairMass',    binning=QUANTITIES['jet12mass_wide'].binning),

    'jet2HLTAssignedPathIndex':         Quantity(name='jet2HLTAssignedPathIndex',       expression='jet2HLTAssignedPathIndex',      binning=QUANTITIES['jet1HLTAssignedPathIndex'].binning),
    'jet2HLTAssignedPathEfficiency':    Quantity(name='jet2HLTAssignedPathEfficiency',  expression='jet2HLTAssignedPathEfficiency', binning=QUANTITIES['jet1HLTAssignedPathEfficiency'].binning),
    'jet2HLTAssignedPathPrescale':      Quantity(name='jet2HLTAssignedPathPrescale',    expression='jet2HLTAssignedPathPrescale',   binning=QUANTITIES['jet1HLTAssignedPathPrescale'].binning),
})


# specification of defines to be applied to data frame
GLOBAL_DEFINES = {
    # extract HLT path bits
    "HLT_PFJet40":  "(hltBits&{})>0".format(2**0),
    "HLT_PFJet60":  "(hltBits&{})>0".format(2**1),
    "HLT_PFJet80":  "(hltBits&{})>0".format(2**2),
    "HLT_PFJet140": "(hltBits&{})>0".format(2**3),
    "HLT_PFJet200": "(hltBits&{})>0".format(2**4),
    "HLT_PFJet260": "(hltBits&{})>0".format(2**5),
    "HLT_PFJet320": "(hltBits&{})>0".format(2**6),
    "HLT_PFJet400": "(hltBits&{})>0".format(2**7),
    "HLT_PFJet450": "(hltBits&{})>0".format(2**8),
    "HLT_PFJet500": "(hltBits&{})>0".format(2**9),
    # event weights
    "totalWeight": "jet1HLTAssignedPathPrescale/jet1HLTAssignedPathEfficiency",
    "triggerEfficiencyWeight": "1.0/jet1HLTAssignedPathEfficiency",
    "triggerPrescaleWeight": "jet1HLTAssignedPathPrescale",
}


# specification of filters to be applied to data frame
BASIC_SELECTION = [
    # leading jet has matched trigger object
    "(jet1HLTAssignedPathEfficiency>0.0&&jet1HLTAssignedPathIndex>=0)",

    # kinematics of leading jets
    "abs(jet1pt) > 60",
    "abs(jet2pt) > 60",
    #"abs(jet1y) < 4.0",
    #"abs(jet2y) < 4.0",

    ##MET/sumEt filter
    #"metOverSumET < 0.3"
]


# specification of ways to split sample into subsamples
SPLITTINGS = {
    # in (y_boost, y_star) bins
    'ybys' : {
        'inclusive' : dict(),
        'YB01_YS01' : dict(yboost=(0, 1), ystar=(0, 1)),
        'YB01_YS12' : dict(yboost=(0, 1), ystar=(1, 2)),
        'YB01_YS23' : dict(yboost=(0, 1), ystar=(2, 3)),
        'YB12_YS01' : dict(yboost=(1, 2), ystar=(0, 1)),
        'YB12_YS12' : dict(yboost=(1, 2), ystar=(1, 2)),
        'YB23_YS01' : dict(yboost=(2, 3), ystar=(0, 1)),
    },
    # by trigger path (with overlap)
    'triggers' : {
        'all' : dict(),
        'HLT_PFJet40'  : dict(HLT_PFJet40=1),
        'HLT_PFJet60'  : dict(HLT_PFJet60=1),
        'HLT_PFJet80'  : dict(HLT_PFJet80=1),
        'HLT_PFJet140' : dict(HLT_PFJet140=1),
        'HLT_PFJet200' : dict(HLT_PFJet200=1),
        'HLT_PFJet260' : dict(HLT_PFJet260=1),
        'HLT_PFJet320' : dict(HLT_PFJet320=1),
        'HLT_PFJet400' : dict(HLT_PFJet400=1),
        'HLT_PFJet450' : dict(HLT_PFJet450=1),
        'HLT_PFJet500' : dict(HLT_PFJet500=1),
    },
    # by trigger path (mutually exclusive)
    'triggers_exclusive' : {
        'all' : dict(),
        'HLT_PFJet40' : dict(jet1HLTAssignedPathIndex=0),
        'HLT_PFJet60' : dict(jet1HLTAssignedPathIndex=1),
        'HLT_PFJet80' : dict(jet1HLTAssignedPathIndex=2),
        'HLT_PFJet140' : dict(jet1HLTAssignedPathIndex=3),
        'HLT_PFJet200' : dict(jet1HLTAssignedPathIndex=4),
        'HLT_PFJet260' : dict(jet1HLTAssignedPathIndex=5),
        'HLT_PFJet320' : dict(jet1HLTAssignedPathIndex=6),
        'HLT_PFJet400' : dict(jet1HLTAssignedPathIndex=7),
        'HLT_PFJet450' : dict(jet1HLTAssignedPathIndex=8),
        'HLT_PFJet500' : dict(jet1HLTAssignedPathIndex=9),
    }
}
