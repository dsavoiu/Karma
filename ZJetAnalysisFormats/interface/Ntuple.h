#pragma once

#include <vector>

#define UNDEFINED_DOUBLE -999;

namespace zjet {
    class NtupleEntry {
      public:
        // -- ntuple branches
        long run = -1;
        int lumi = -1;
        long event = -1;
        int bx = -1;

        // pileup-related
        double rho = UNDEFINED_DOUBLE;      // PU density
        double nPUMean = UNDEFINED_DOUBLE;  // true (MC) or estimated (DATA) mean of Poisson distribution of `nPU`

        // number of primary vertices
        int npv = -1;
        int npvGood = -1;

        // Z boson kinematics
        double zPt = UNDEFINED_DOUBLE;
        double zPhi = UNDEFINED_DOUBLE;
        double zEta = UNDEFINED_DOUBLE;
        double zY = UNDEFINED_DOUBLE;
        double zMass = UNDEFINED_DOUBLE;

        // Z boson child lepton kinematics
        double zPositiveLeptonPt = UNDEFINED_DOUBLE;
        double zPositiveLeptonPhi = UNDEFINED_DOUBLE;
        double zPositiveLeptonEta = UNDEFINED_DOUBLE;

        double zNegativeLeptonPt = UNDEFINED_DOUBLE;
        double zNegativeLeptonPhi = UNDEFINED_DOUBLE;
        double zNegativeLeptonEta = UNDEFINED_DOUBLE;

        // lepton kinematics
        double lepton1Pt = UNDEFINED_DOUBLE;
        double lepton1Phi = UNDEFINED_DOUBLE;
        double lepton1Eta = UNDEFINED_DOUBLE;
        int lepton1PDGId = 0;
        double lepton2Pt = UNDEFINED_DOUBLE;
        double lepton2Phi = UNDEFINED_DOUBLE;
        double lepton2Eta = UNDEFINED_DOUBLE;
        int lepton2PDGId = 0;

        // leading jet kinematics
        double jet1Pt = UNDEFINED_DOUBLE;
        double jet1Phi = UNDEFINED_DOUBLE;
        double jet1Eta = UNDEFINED_DOUBLE;
        double jet1Y = UNDEFINED_DOUBLE;
        int    jet1Id = -1;
        // second-leading jet kinematics
        double jet2Pt = UNDEFINED_DOUBLE;
        double jet2Phi = UNDEFINED_DOUBLE;
        double jet2Eta = UNDEFINED_DOUBLE;
        double jet2Y = UNDEFINED_DOUBLE;
        int    jet2Id = -1;

        // MET
        double met = UNDEFINED_DOUBLE;
        double sumEt = UNDEFINED_DOUBLE;
        double metRaw = UNDEFINED_DOUBLE;
        double sumEtRaw = UNDEFINED_DOUBLE;

        // -- MC-specific

        // pileup truth info
        int nPU = -1;

        // weights
        double generatorWeight = 1.0;
        double generatorWeightProduct = 1.0;
        double weightForStitching = 1.0;
        double pileupWeight =  1.0;

        // binning values
        double binningValue = UNDEFINED_DOUBLE;

        // gen-Z boson kinematics
        double genZPt = UNDEFINED_DOUBLE;
        double genZEta = UNDEFINED_DOUBLE;
        double genZY = UNDEFINED_DOUBLE;
        double genZPhi = UNDEFINED_DOUBLE;

        // gen-genLepton kinematics
        double genLepton1Pt = UNDEFINED_DOUBLE;
        double genLepton1Phi = UNDEFINED_DOUBLE;
        double genLepton1Eta = UNDEFINED_DOUBLE;
        int genLepton1PDGId = 0;
        double genLepton2Pt = UNDEFINED_DOUBLE;
        double genLepton2Phi = UNDEFINED_DOUBLE;
        double genLepton2Eta = UNDEFINED_DOUBLE;
        int genLepton2PDGId = 0;

        // gen-jets (unmatched to reco)
        double genJet1Pt = UNDEFINED_DOUBLE;
        double genJet1Eta = UNDEFINED_DOUBLE;
        double genJet1Y = UNDEFINED_DOUBLE;
        double genJet1Phi = UNDEFINED_DOUBLE;

        double genJet2Pt = UNDEFINED_DOUBLE;
        double genJet2Eta = UNDEFINED_DOUBLE;
        double genJet2Y = UNDEFINED_DOUBLE;
        double genJet2Phi = UNDEFINED_DOUBLE;

        // gen-jets (matched to reco)
        double jet1MatchedGenJetPt = UNDEFINED_DOUBLE;
        double jet1MatchedGenJetEta = UNDEFINED_DOUBLE;
        double jet1MatchedGenJetY = UNDEFINED_DOUBLE;
        double jet1MatchedGenJetPhi = UNDEFINED_DOUBLE;

        double jet2MatchedGenJetPt = UNDEFINED_DOUBLE;
        double jet2MatchedGenJetEta = UNDEFINED_DOUBLE;
        double jet2MatchedGenJetY = UNDEFINED_DOUBLE;
        double jet2MatchedGenJetPhi = UNDEFINED_DOUBLE;

    };
    typedef std::vector<zjet::NtupleEntry> Ntuple;
}
