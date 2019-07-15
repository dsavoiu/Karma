#include "Karma/DijetAnalysis/interface/NtupleFlatOutput.h"

/* helper macro for writing TTree branches
 *                                                           branch name               product member name/type
 *                                                                    pointer to product member */
#define ADD_BRANCH(tree, product, branch, type) tree->Branch(#branch, &product->branch, #branch"/"#type);

// Note: ADD_BRANCH(tree, product, branch, type) expands to:
//    tree->Branch("branch", &product->branch, "branch/type")

// -- TTree wiring
void dijet::NtupleFlatOutput::setUpTTree(TTree* tree, dijet::NtupleEntry* productForFill) {

    ADD_BRANCH(tree, productForFill, run, L);
    ADD_BRANCH(tree, productForFill, lumi, I);
    ADD_BRANCH(tree, productForFill, event, L);
    ADD_BRANCH(tree, productForFill, bx, I);
    ADD_BRANCH(tree, productForFill, rho, D);
    ADD_BRANCH(tree, productForFill, npv, I);
    ADD_BRANCH(tree, productForFill, npvGood, I);
    ADD_BRANCH(tree, productForFill, nPUMean, D);
    ADD_BRANCH(tree, productForFill, jet1pt, D);
    ADD_BRANCH(tree, productForFill, jet1phi, D);
    ADD_BRANCH(tree, productForFill, jet1eta, D);
    ADD_BRANCH(tree, productForFill, jet1y, D);
    ADD_BRANCH(tree, productForFill, jet1id, I);
    ADD_BRANCH(tree, productForFill, jet2pt, D);
    ADD_BRANCH(tree, productForFill, jet2phi, D);
    ADD_BRANCH(tree, productForFill, jet2eta, D);
    ADD_BRANCH(tree, productForFill, jet2y, D);
    ADD_BRANCH(tree, productForFill, jet2id, I);
    ADD_BRANCH(tree, productForFill, jet12mass, D);
    ADD_BRANCH(tree, productForFill, jet12ptave, D);
    ADD_BRANCH(tree, productForFill, jet12ystar, D);
    ADD_BRANCH(tree, productForFill, jet12yboost, D);
    ADD_BRANCH(tree, productForFill, binIndexJet12PtAve, I);
    ADD_BRANCH(tree, productForFill, binIndexJet12Mass, I);
    ADD_BRANCH(tree, productForFill, met, D);
    ADD_BRANCH(tree, productForFill, sumEt, D);
    ADD_BRANCH(tree, productForFill, metRaw, D);
    ADD_BRANCH(tree, productForFill, sumEtRaw, D);
    ADD_BRANCH(tree, productForFill, hltBits, L);
    ADD_BRANCH(tree, productForFill, hltJet1Match, L);
    ADD_BRANCH(tree, productForFill, hltJet2Match, L);
    ADD_BRANCH(tree, productForFill, hltJet12Match, L);
    ADD_BRANCH(tree, productForFill, hltJet1PtPassThresholdsL1, L);
    ADD_BRANCH(tree, productForFill, hltJet1PtPassThresholdsHLT, L);
    ADD_BRANCH(tree, productForFill, hltJet2PtPassThresholdsL1, L);
    ADD_BRANCH(tree, productForFill, hltJet2PtPassThresholdsHLT, L);
    ADD_BRANCH(tree, productForFill, hltJet12PtAvePassThresholdsL1, L);
    ADD_BRANCH(tree, productForFill, hltJet12PtAvePassThresholdsHLT, L);
    // PF energy fractions
    ADD_BRANCH(tree, productForFill, jet1NeutralHadronFraction, D);
    ADD_BRANCH(tree, productForFill, jet1ChargedHadronFraction, D);
    ADD_BRANCH(tree, productForFill, jet1MuonFraction, D);
    ADD_BRANCH(tree, productForFill, jet1PhotonFraction, D);
    ADD_BRANCH(tree, productForFill, jet1ElectronFraction, D);
    ADD_BRANCH(tree, productForFill, jet1HFHadronFraction, D);
    ADD_BRANCH(tree, productForFill, jet1HFEMFraction, D);
    ADD_BRANCH(tree, productForFill, jet2NeutralHadronFraction, D);
    ADD_BRANCH(tree, productForFill, jet2ChargedHadronFraction, D);
    ADD_BRANCH(tree, productForFill, jet2MuonFraction, D);
    ADD_BRANCH(tree, productForFill, jet2PhotonFraction, D);
    ADD_BRANCH(tree, productForFill, jet2ElectronFraction, D);
    ADD_BRANCH(tree, productForFill, jet2HFHadronFraction, D);
    ADD_BRANCH(tree, productForFill, jet2HFEMFraction, D);

    // MC
    if (!m_isData) {
        // number of pile-up interactions
        ADD_BRANCH(tree, productForFill, nPU, I);
        // gen jets (not matched to reco)
        ADD_BRANCH(tree, productForFill, genJet1Pt, D);
        ADD_BRANCH(tree, productForFill, genJet1Phi, D);
        ADD_BRANCH(tree, productForFill, genJet1Eta, D);
        ADD_BRANCH(tree, productForFill, genJet1Y, D);
        ADD_BRANCH(tree, productForFill, genJet2Pt, D);
        ADD_BRANCH(tree, productForFill, genJet2Phi, D);
        ADD_BRANCH(tree, productForFill, genJet2Eta, D);
        ADD_BRANCH(tree, productForFill, genJet2Y, D);
        ADD_BRANCH(tree, productForFill, genJet12Mass, D);
        ADD_BRANCH(tree, productForFill, genJet12PtAve, D);
        ADD_BRANCH(tree, productForFill, genJet12YStar, D);
        ADD_BRANCH(tree, productForFill, genJet12YBoost, D);
        ADD_BRANCH(tree, productForFill, binIndexGenJet12PtAve, I);
        ADD_BRANCH(tree, productForFill, binIndexGenJet12Mass, I);
        // gen jets (matched to reco)
        ADD_BRANCH(tree, productForFill, jet1MatchedGenJetPt, D);
        ADD_BRANCH(tree, productForFill, jet1MatchedGenJetPhi, D);
        ADD_BRANCH(tree, productForFill, jet1MatchedGenJetEta, D);
        ADD_BRANCH(tree, productForFill, jet1MatchedGenJetY, D);
        ADD_BRANCH(tree, productForFill, jet2MatchedGenJetPt, D);
        ADD_BRANCH(tree, productForFill, jet2MatchedGenJetPhi, D);
        ADD_BRANCH(tree, productForFill, jet2MatchedGenJetEta, D);
        ADD_BRANCH(tree, productForFill, jet2MatchedGenJetY, D);
        ADD_BRANCH(tree, productForFill, jet12MatchedGenJetPairMass, D);
        ADD_BRANCH(tree, productForFill, jet12MatchedGenJetPairPtAve, D);
        ADD_BRANCH(tree, productForFill, jet12MatchedGenJetPairYStar, D);
        ADD_BRANCH(tree, productForFill, jet12MatchedGenJetPairYBoost, D);
        ADD_BRANCH(tree, productForFill, binIndexMatchedGenJet12PtAve, I);
        ADD_BRANCH(tree, productForFill, binIndexMatchedGenJet12Mass, I);
        // QCD subprocess info
        ADD_BRANCH(tree, productForFill, incomingParton1Flavor, I);
        ADD_BRANCH(tree, productForFill, incomingParton2Flavor, I);
        ADD_BRANCH(tree, productForFill, incomingParton1x, D);
        ADD_BRANCH(tree, productForFill, incomingParton2x, D);
        ADD_BRANCH(tree, productForFill, alphaQCD, D);
        ADD_BRANCH(tree, productForFill, scalePDF, D);
        // flavor
        ADD_BRANCH(tree, productForFill, jet1PartonFlavor, I);
        ADD_BRANCH(tree, productForFill, jet2PartonFlavor, I);
        ADD_BRANCH(tree, productForFill, jet1HadronFlavor, I);
        ADD_BRANCH(tree, productForFill, jet2HadronFlavor, I);
        // weights
        ADD_BRANCH(tree, productForFill, generatorWeight, D);
        ADD_BRANCH(tree, productForFill, generatorWeightProduct, D);
        ADD_BRANCH(tree, productForFill, weightForStitching, D);
        ADD_BRANCH(tree, productForFill, pileupWeight, D);
        ADD_BRANCH(tree, productForFill, pileupWeightAlt, D);
        // binning values
        ADD_BRANCH(tree, productForFill, binningValue, D);
    }

}


void dijet::NtupleFlatOutput::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    // call parent
    NtupleFlatOutputAnalyzerBase<dijet::NtupleEntry>::fillDescriptions(descriptions);

    // The following says we do not know what parameters are allowed so do no validation
    // Please change this to state exactly what you do use, even if it is no parameters
    edm::ParameterSetDescription desc;
    desc.setUnknown();
    descriptions.addDefault(desc);
}


// register type for RTTI / completeness check
REGISTER_NTUPLE_ENTRY_TYPE(dijet::NtupleEntry);

//define this as a plug-in
using DijetNtupleFlatOutput = dijet::NtupleFlatOutput;
DEFINE_FWK_MODULE(DijetNtupleFlatOutput);
