import numpy as np

SPLITTINGS = {
    'ybys' : {
        'inclusive' : dict(),
        'YB01_YS01' : dict(jet12yboost=(0, 1), jet12ystar=(0, 1)),
        'YB01_YS12' : dict(jet12yboost=(0, 1), jet12ystar=(1, 2)),
        'YB01_YS23' : dict(jet12yboost=(0, 1), jet12ystar=(2, 3)),
        'YB12_YS01' : dict(jet12yboost=(1, 2), jet12ystar=(0, 1)),
        'YB12_YS12' : dict(jet12yboost=(1, 2), jet12ystar=(1, 2)),
        'YB23_YS01' : dict(jet12yboost=(2, 3), jet12ystar=(0, 1)),
    },
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

QUANTITY_BINNINGS = {
    'metOverSumET' : np.linspace(0, 1, 101),

    # original (arbitrary) binning
    #'jet1pt' : (60, 74, 84, 97, 114, 133, 153, 174, 196, 220, 245, 272, 300, 330, 362, 395, 430, 468, 507, 548, 592, 638, 686, 737, 790, 846, 905, 967, 1032, 1101, 1172, 1248, 1327, 1410, 1497, 1588, 1784, 2116, 5000),
    #'jet12mass' : (60, 74, 84, 97, 114, 133, 153, 174, 196, 220, 245, 272, 300, 330, 362, 395, 430, 468, 507, 548, 592, 638, 686, 737, 790, 846, 905, 967, 1032, 1101, 1172, 1248, 1327, 1410, 1497, 1588, 1784, 2116, 5000),
    #'jet12ptave' : (60, 74, 84, 97, 114, 133, 153, 174, 196, 220, 245, 272, 300, 330, 362, 395, 430, 468, 507, 548, 592, 638, 686, 737, 790, 846, 905, 967, 1032, 1101, 1172, 1248, 1327, 1410, 1497, 1588, 1784, 2116, 5000),

    ## "wide" binning with targer resolution/bin_width of 0.5
    #'jet1pt' : (60, 80, 106, 137, 174, 215, 264, 321, 384, 461, 539, 631, 731, 845, 966, 1099, 1245, 1407, 1582, 1782, 1977, 2192, 2443, 2681, 2944, 3218, 3518, 3874, 4170, 4827),
    #'jet12mass' : (200, 249, 306, 372, 449, 539, 641, 756, 887, 1029, 1187, 1361, 1556, 1769, 2008, 2273, 2572, 2915, 3306, 3754, 4244, 4805, 5374, 5994, 6672, 7456, 8401, 9607),
    #'jet12ptave' : (100, 122, 147, 175, 207, 243, 284, 329, 380, 437, 499, 569, 646, 732, 827, 931, 1046, 1171, 1307, 1458, 1621, 1806, 2003, 2217, 2453, 2702, 2977, 3249, 3557, 3816, 4045),

    # "narrow" binning with target resolution/bin_width of 1.0
    'jet1pt' : (60, 69, 79, 90, 102, 115, 129, 144, 160, 177, 194, 213, 233, 254, 277, 301, 326, 352, 380, 411, 443, 476, 510, 546, 584, 624, 665, 709, 755, 803, 852, 903, 956, 1012, 1070, 1130, 1193, 1258, 1326, 1398, 1472, 1549, 1629, 1712, 1799, 1884, 1971, 2062, 2156, 2256, 2361, 2461, 2562, 2669, 2778, 2893, 3019, 3143, 3267, 3402, 3569, 3715, 3805, 3930, 4084, 4413),
    'jet12mass' : (200, 220, 242, 265, 290, 317, 345, 375, 407, 441, 477, 516, 557, 600, 645, 693, 744, 797, 853, 912, 973, 1036, 1102, 1171, 1243, 1318, 1397, 1480, 1567, 1657, 1750, 1849, 1952, 2060, 2173, 2292, 2418, 2551, 2692, 2842, 3000, 3168, 3346, 3533, 3730, 3933, 4147, 4373, 4612, 4861, 5105, 5355, 5617, 5890, 6174, 6470, 6801, 7141, 7506, 7900, 8396, 8930, 9551, 9951),
    'jet12ptave' : (100, 110, 120, 131, 142, 154, 166, 179, 193, 207, 222, 238, 255, 273, 291, 310, 330, 351, 373, 397, 422, 448, 475, 503, 532, 563, 595, 628, 663, 700, 738, 778, 820, 863, 908, 955, 1004, 1055, 1108, 1163, 1220, 1280, 1342, 1406, 1473, 1543, 1615, 1690, 1768, 1850, 1935, 2023, 2114, 2209, 2307, 2410, 2515, 2624, 2738, 2857, 2979, 3104, 3233, 3372, 3517, 3580, 3709, 3810, 3914, 3973),


    'jet1HLTAssignedPathIndex': np.arange(-1, 12) - 0.5,
    'jet2HLTAssignedPathIndex': np.arange(-1, 12) - 0.5,
    'jet1HLTAssignedPathPrescale': np.array([-1, 0, 1, 2, 11, 21, 41, 71, 121]) - 0.5,
    'jet2HLTAssignedPathPrescale': np.array([-1, 0, 1, 2, 11, 21, 41, 71, 121]) - 0.5,
    'jet1HLTAssignedPathEfficiency': np.linspace(0, 1, 25),
    'jet2HLTAssignedPathEfficiency': np.linspace(0, 1, 25),
    'jet1phi': (-3.2, 3.2),  # one big bin for counting experiments
    'run': np.linspace(278820, 280385, 30),
}
QUANTITY_BINNINGS['jet1MatchedGenJetPt'] = QUANTITY_BINNINGS['jet1pt']
QUANTITY_BINNINGS['jet12MatchedGenJetPairPtAve'] = QUANTITY_BINNINGS['jet12ptave']
QUANTITY_BINNINGS['jet12MatchedGenJetPairMass'] = QUANTITY_BINNINGS['jet12mass']

def basic_selection(data_frame):
    return (data_frame
        .Define("isValid", "(jet1HLTAssignedPathEfficiency>0.0&&jet1HLTAssignedPathIndex>=0)")
        .Define("metOverSumET", "met/sumEt")
        .Define("HLT_PFJet40",  "(hltBits&{})>0".format(2**0))
        .Define("HLT_PFJet60",  "(hltBits&{})>0".format(2**1))
        .Define("HLT_PFJet80",  "(hltBits&{})>0".format(2**2))
        .Define("HLT_PFJet140", "(hltBits&{})>0".format(2**3))
        .Define("HLT_PFJet200", "(hltBits&{})>0".format(2**4))
        .Define("HLT_PFJet260", "(hltBits&{})>0".format(2**5))
        .Define("HLT_PFJet320", "(hltBits&{})>0".format(2**6))
        .Define("HLT_PFJet400", "(hltBits&{})>0".format(2**7))
        .Define("HLT_PFJet450", "(hltBits&{})>0".format(2**8))
        .Define("HLT_PFJet500", "(hltBits&{})>0".format(2**9))
        .Filter("isValid")
        .Filter("abs(jet1pt) > 60")
        .Filter("abs(jet2pt) > 60")
        .Filter("abs(jet1y) < 3.0")
        .Filter("abs(jet2y) < 3.0")
        #.Filter("metOverSumET < 0.3")
        .Define("totalWeight", "jet1HLTAssignedPathPrescale/jet1HLTAssignedPathEfficiency")
        .Define("triggerEfficiencyWeight", "1.0/jet1HLTAssignedPathEfficiency")
        .Define("triggerPrescaleWeight", "jet1HLTAssignedPathPrescale")
    )
