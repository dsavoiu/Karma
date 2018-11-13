#pragma once

#include <vector>

#define UNDEFINED_DOUBLE -999;

namespace dijet {
    class NtupleEntry {
      public:
        // -- ntuple branches
        long run = -1;
        int lumi = -1;
        long event = -1;
        int bx = -1;
        // pileup density
        double rho = UNDEFINED_DOUBLE;
        // number of primary vertices
        int npv = -1;
        int npvGood = -1;
        // leading jet kinematics
        double jet1pt = UNDEFINED_DOUBLE;
        double jet1phi = UNDEFINED_DOUBLE;
        double jet1eta = UNDEFINED_DOUBLE;
        double jet1y = UNDEFINED_DOUBLE;
        int    jet1id = -1;
        // second-leading jet kinematics
        double jet2pt = UNDEFINED_DOUBLE;
        double jet2phi = UNDEFINED_DOUBLE;
        double jet2eta = UNDEFINED_DOUBLE;
        double jet2y = UNDEFINED_DOUBLE;
        int    jet2id = -1;
        // leading jet pair kinematics
        double jet12mass = UNDEFINED_DOUBLE;
        double jet12ptave = UNDEFINED_DOUBLE;
        double jet12ystar = UNDEFINED_DOUBLE;
        double jet12yboost = UNDEFINED_DOUBLE;

        // jet PF energy fractions
        double jet1NeutralHadronFraction = UNDEFINED_DOUBLE;
        double jet1ChargedHadronFraction = UNDEFINED_DOUBLE;
        double jet1MuonFraction = UNDEFINED_DOUBLE;
        double jet1PhotonFraction = UNDEFINED_DOUBLE;
        double jet1ElectronFraction = UNDEFINED_DOUBLE;
        double jet1HFHadronFraction = UNDEFINED_DOUBLE;
        double jet1HFEMFraction = UNDEFINED_DOUBLE;

        double jet2NeutralHadronFraction = UNDEFINED_DOUBLE;
        double jet2ChargedHadronFraction = UNDEFINED_DOUBLE;
        double jet2MuonFraction = UNDEFINED_DOUBLE;
        double jet2PhotonFraction = UNDEFINED_DOUBLE;
        double jet2ElectronFraction = UNDEFINED_DOUBLE;
        double jet2HFHadronFraction = UNDEFINED_DOUBLE;
        double jet2HFEMFraction = UNDEFINED_DOUBLE;

        // MET
        double met = UNDEFINED_DOUBLE;
        double sumEt = UNDEFINED_DOUBLE;

        // trigger results
        unsigned long hltBits;

        // HLT objects
        double jet1HLTpt = UNDEFINED_DOUBLE;
        unsigned int jet1HLTNumMatchedTriggerObjects = 0;
        int jet1HLTAssignedPathIndex = -1;
        double jet1HLTAssignedPathEfficiency = UNDEFINED_DOUBLE;

        double jet2HLTpt = UNDEFINED_DOUBLE;
        unsigned int jet2HLTNumMatchedTriggerObjects = 0;
        int jet2HLTAssignedPathIndex = -1;
        double jet2HLTAssignedPathEfficiency = UNDEFINED_DOUBLE;

        // -- MC-specific

        // qcd subprocess
        int incomingParton1Flavor = -999;
        int incomingParton2Flavor = -999;
        double incomingParton1x = UNDEFINED_DOUBLE;
        double incomingParton2x = UNDEFINED_DOUBLE;
        double scalePDF = UNDEFINED_DOUBLE;
        double alphaQCD = UNDEFINED_DOUBLE;

        // jet flavor
        int jet1PartonFlavor = -999;
        int jet2PartonFlavor = -999;
        int jet1HadronFlavor = -999;
        int jet2HadronFlavor = -999;

        // weights
        double weightForStitching = 1.0;

        // GenJets
        double jet1MatchedGenJetPt = UNDEFINED_DOUBLE;
        double jet1MatchedGenJetEta = UNDEFINED_DOUBLE;
        double jet1MatchedGenJetY = UNDEFINED_DOUBLE;
        double jet1MatchedGenJetPhi = UNDEFINED_DOUBLE;

        double jet2MatchedGenJetPt = UNDEFINED_DOUBLE;
        double jet2MatchedGenJetEta = UNDEFINED_DOUBLE;
        double jet2MatchedGenJetY = UNDEFINED_DOUBLE;
        double jet2MatchedGenJetPhi = UNDEFINED_DOUBLE;

        // leading matched gen jet pair kinematics
        double jet12MatchedGenJetPairMass = UNDEFINED_DOUBLE;
        double jet12MatchedGenJetPairPtAve = UNDEFINED_DOUBLE;
        double jet12MatchedGenJetPairYStar = UNDEFINED_DOUBLE;
        double jet12MatchedGenJetPairYBoost = UNDEFINED_DOUBLE;

    };
    typedef std::vector<dijet::NtupleEntry> Ntuple;
}
