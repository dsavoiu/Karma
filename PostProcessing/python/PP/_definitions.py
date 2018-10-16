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
    #'jet12mass' : np.linspace(0, 8000, 101),
    'metOverSumET' : np.linspace(0, 1, 101),
    'jet12mass' : (60, 74, 84, 97, 114, 133, 153, 174, 196, 220, 245, 272, 300, 330, 362, 395, 430, 468, 507, 548, 592, 638, 686, 737, 790, 846, 905, 967, 1032, 1101, 1172, 1248, 1327, 1410, 1497, 1588, 1784, 2116, 5000),
    'jet1pt' : (60, 74, 84, 97, 114, 133, 153, 174, 196, 220, 245, 272, 300, 330, 362, 395, 430, 468, 507, 548, 592, 638, 686, 737, 790, 846, 905, 967, 1032, 1101, 1172, 1248, 1327, 1410, 1497, 1588, 1784, 2116, 5000),
    'jet12ptave' : (60, 74, 84, 97, 114, 133, 153, 174, 196, 220, 245, 272, 300, 330, 362, 395, 430, 468, 507, 548, 592, 638, 686, 737, 790, 846, 905, 967, 1032, 1101, 1172, 1248, 1327, 1410, 1497, 1588, 1784, 2116, 5000),
    'jet1HLTAssignedPathIndex': np.arange(-1, 12) - 0.5,
    'jet2HLTAssignedPathIndex': np.arange(-1, 12) - 0.5,
    'jet1HLTAssignedPathPrescale': np.array([-1, 0, 1, 2, 11, 21, 41, 71, 121]) - 0.5,
    'jet2HLTAssignedPathPrescale': np.array([-1, 0, 1, 2, 11, 21, 41, 71, 121]) - 0.5,
    'jet1HLTAssignedPathEfficiency': np.linspace(0, 1, 25),
    'jet2HLTAssignedPathEfficiency': np.linspace(0, 1, 25),
}
QUANTITY_BINNINGS['jet1MatchedGenJetPt'] = QUANTITY_BINNINGS['jet1pt']
QUANTITY_BINNINGS['jet12MatchedGenJetPairPtAve'] = QUANTITY_BINNINGS['jet12ptave']
QUANTITY_BINNINGS['jet12MatchedGenJetPairMass'] = QUANTITY_BINNINGS['jet12mass']

def basic_selection(data_frame):
    return (data_frame
        .Define("isValid", "(jet1HLTAssignedPathEfficiency>0.0&&jet1HLTAssignedPathIndex>=0)")
        .Define("metOverSumET", "met/sumEt")
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
