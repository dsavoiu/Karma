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
        double randomUniform = UNDEFINED_DOUBLE;
        // pileup-related
        double rho = UNDEFINED_DOUBLE;      // PU density
        double nPUMean = UNDEFINED_DOUBLE;  // true (MC) or estimated (DATA) mean of Poisson distribution of `nPU`

        // number of primary vertices
        int npv = -1;
        int npvGood = -1;

        // prefiring weights
        double prefiringWeight = 1.0;
        double prefiringWeightUp = 1.0;
        double prefiringWeightDown = 1.0;

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

        // global bin indices for reconstructed jet pair
        int binIndexJet12PtAve = -1;
        int binIndexJet12Mass = -1;

        // index of active trigger path
        int indexActiveTriggerPathJet12PtAve = -1;
        int indexActiveTriggerPathJet12Mass = -1;

        // prescale of active trigger path
        int prescaleActiveTriggerPathJet12PtAve = 0;
        int prescaleActiveTriggerPathJet12Mass = 0;

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
        double metRaw = UNDEFINED_DOUBLE;
        double sumEtRaw = UNDEFINED_DOUBLE;

        // trigger results
        unsigned long hltBits;
        unsigned long hltJet1Match;
        unsigned long hltJet2Match;
        unsigned long hltJet12Match;
        unsigned long hltJet1PtPassThresholdsL1;
        unsigned long hltJet1PtPassThresholdsHLT;
        unsigned long hltJet2PtPassThresholdsL1;
        unsigned long hltJet2PtPassThresholdsHLT;
        unsigned long hltJet12PtAvePassThresholdsL1;
        unsigned long hltJet12PtAvePassThresholdsHLT;

        // MET filter bits
        unsigned long metFilterBits;

        /// // HLT objects
        /// double jet1HLTpt = UNDEFINED_DOUBLE;
        /// unsigned int jet1HLTNumMatchedTriggerObjects = 0;
        /// double jet2HLTpt = UNDEFINED_DOUBLE;
        /// unsigned int jet2HLTNumMatchedTriggerObjects = 0;

        // -- MC-specific

        // pileup truth info
        int nPU = -1;

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
        double generatorWeight = 1.0;
        double generatorWeightProduct = 1.0;
        double weightForStitching = 1.0;
        double pileupWeight = 1.0;
        double pileupWeightSimulatedHLT = 1.0;
        double pileupWeightActiveHLTByJet12PtAve = 1.0;
        double pileupWeightActiveHLTByJet12Mass = 1.0;

        // binning values
        double binningValue = UNDEFINED_DOUBLE;

        // leading GenJets (unmatched to reco)
        double genJet1Pt = UNDEFINED_DOUBLE;
        double genJet1Eta = UNDEFINED_DOUBLE;
        double genJet1Y = UNDEFINED_DOUBLE;
        double genJet1Phi = UNDEFINED_DOUBLE;

        double genJet2Pt = UNDEFINED_DOUBLE;
        double genJet2Eta = UNDEFINED_DOUBLE;
        double genJet2Y = UNDEFINED_DOUBLE;
        double genJet2Phi = UNDEFINED_DOUBLE;

        // leading gen jet pair kinematics
        double genJet12Mass = UNDEFINED_DOUBLE;
        double genJet12PtAve = UNDEFINED_DOUBLE;
        double genJet12YStar = UNDEFINED_DOUBLE;
        double genJet12YBoost = UNDEFINED_DOUBLE;

        // global bin indices for reconstructed jet pair
        int binIndexGenJet12PtAve = -1;
        int binIndexGenJet12Mass = -1;

        // Matched Gen Jets
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

        // global bin indices for reconstructed jet pair
        int binIndexMatchedGenJet12PtAve = -1;
        int binIndexMatchedGenJet12Mass = -1;

    };
    typedef std::vector<dijet::NtupleEntry> Ntuple;
}
