#pragma once

#include <vector>

#define UNDEFINED_DOUBLE -999;

namespace dijet {
    struct NtupleV2Entry {
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

        // -- jets
        std::vector<double> Jet_pt;
        std::vector<double> Jet_phi;
        std::vector<double> Jet_eta;
        std::vector<double> Jet_mass;
        std::vector<double> Jet_area;
        std::vector<double> Jet_rawFactor;
        std::vector<int>    Jet_hadronFlavor;
        std::vector<int>    Jet_partonFlavor;
        // trigger object matches and pt threshold checks
        std::vector<unsigned long>   Jet_hltMatch;
        std::vector<unsigned long>   Jet_l1Match;
        std::vector<unsigned long>   Jet_hltPassPtAveThreshold; // index 0 refers to jet pair (0,1) etc.
        std::vector<unsigned long>   Jet_hltPassPtThreshold;
        std::vector<unsigned long>   Jet_l1PassPtThreshold;
        // precomputed jet ID
        std::vector<int>    Jet_jetId;
        // jet ID inputs (named as in https://twiki.cern.ch/twiki/bin/view/CMS/JetID13TeVRun2016)
        std::vector<double> Jet_NHF;
        std::vector<double> Jet_NEMF;
        std::vector<double> Jet_CHF;
        std::vector<double> Jet_MUF;
        std::vector<double> Jet_CEMF;
        std::vector<unsigned int> Jet_NumConst;
        std::vector<unsigned int> Jet_NumNeutralParticles;
        // split JES uncertainties
        std::vector<std::vector<double>> Jet_jesUncertaintyFactors;

        // jets (AK8)
        /*
        std::vector<double> FatJet_pt;
        std::vector<double> FatJet_phi;
        std::vector<double> FatJet_eta;
        std::vector<double> FatJet_mass;
        std::vector<double> FatJet_area;
        std::vector<double> FatJet_rawFactor;
        std::vector<int>    FatJet_hadronFlavor;
        std::vector<int>    FatJet_partonFlavor;
        // trigger object matches and pt threshold checks
        std::vector<unsigned long>   FatJet_hltMatch;
        std::vector<unsigned long>   FatJet_l1Match;
        std::vector<unsigned long>   FatJet_hltPassPtAveThreshold; // index 0 refers to jet pair (0,1) etc.
        std::vector<unsigned long>   FatJet_hltPassPtThreshold;
        std::vector<unsigned long>   FatJet_l1PassPtThreshold;
        // split JES uncertainties
        std::vector<std::vector<double>> FatJet_jesUncertaintyFactors;
        */

        // MET
        double MET_pt;
        double MET_sumEt;
        double MET_rawPt;
        double MET_rawSumEt;

        // trigger results
        unsigned long triggerResults = 0;

        // combined L1(min) + HLT prescales
        std::vector<int> triggerPrescales;

        // todo: refactor
        /*
        bool HLT_PFJet40;
        bool HLT_PFJet60;
        bool HLT_PFJet80;
        bool HLT_PFJet140;
        bool HLT_PFJet200;
        bool HLT_PFJet260;
        bool HLT_PFJet320;
        bool HLT_PFJet400;
        bool HLT_PFJet450;
        bool HLT_PFJet500;

        bool HLT_AK8PFJet40;
        bool HLT_AK8PFJet60;
        bool HLT_AK8PFJet80;
        bool HLT_AK8PFJet140;
        bool HLT_AK8PFJet200;
        bool HLT_AK8PFJet260;
        bool HLT_AK8PFJet320;
        bool HLT_AK8PFJet400;
        bool HLT_AK8PFJet450;
        bool HLT_AK8PFJet500;

        bool HLT_DiPFJetAve40;
        bool HLT_DiPFJetAve60;
        bool HLT_DiPFJetAve80;
        bool HLT_DiPFJetAve140;
        bool HLT_DiPFJetAve200;
        bool HLT_DiPFJetAve260;
        bool HLT_DiPFJetAve320;
        bool HLT_DiPFJetAve400;
        bool HLT_DiPFJetAve450;
        bool HLT_DiPFJetAve500;
        */

        // MET filter bits
        unsigned long metFilterBits;

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

        // weights
        double generatorWeight = 1.0;
        double stitchingWeight = 1.0;
        double pileupWeight = 1.0;
        double pileupWeightSimulatedHLT = 1.0;

        // binning values
        double binningValue = UNDEFINED_DOUBLE;

        // gen jet table (AK4)
        std::vector<double> GenJet_pt;
        std::vector<double> GenJet_phi;
        std::vector<double> GenJet_eta;
        std::vector<double> GenJet_mass;

        // gen jet table (AK8)
        /*
        std::vector<double> GenFatJet_pt;
        std::vector<double> GenFatJet_phi;
        std::vector<double> GenFatJet_eta;
        std::vector<double> GenFatJet_mass;
        */
    };
    typedef std::vector<dijet::NtupleV2Entry> NtupleV2;
}
