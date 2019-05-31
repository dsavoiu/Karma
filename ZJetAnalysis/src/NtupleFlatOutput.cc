#include "Karma/ZJetAnalysis/interface/NtupleFlatOutput.h"

/* helper macro for writing TTree branches
 *                                                           branch name               product member name/type
 *                                                                    pointer to product member */
#define ADD_BRANCH(tree, product, branch, type) tree->Branch(#branch, &product->branch, #branch"/"#type);

// Note: ADD_BRANCH(tree, product, branch, type) expands to:
//    tree->Branch("branch", &product->branch, "branch/type")

// -- TTree wiring
void zjet::NtupleFlatOutput::setUpTTree(TTree* tree, zjet::NtupleEntry* productForFill) {

    ADD_BRANCH(tree, productForFill, run, L);
    ADD_BRANCH(tree, productForFill, lumi, I);
    ADD_BRANCH(tree, productForFill, event, L);
    ADD_BRANCH(tree, productForFill, bx, I);
    ADD_BRANCH(tree, productForFill, rho, D);
    ADD_BRANCH(tree, productForFill, npv, I);
    ADD_BRANCH(tree, productForFill, npvGood, I);
    ADD_BRANCH(tree, productForFill, nPUMean, D);

    ADD_BRANCH(tree, productForFill, zPt, D);
    ADD_BRANCH(tree, productForFill, zPhi, D);
    ADD_BRANCH(tree, productForFill, zEta, D);
    ADD_BRANCH(tree, productForFill, zY, D);
    ADD_BRANCH(tree, productForFill, zMass, D);

    ADD_BRANCH(tree, productForFill, zPositiveLeptonPt, D);
    ADD_BRANCH(tree, productForFill, zPositiveLeptonPhi, D);
    ADD_BRANCH(tree, productForFill, zPositiveLeptonEta, D);

    ADD_BRANCH(tree, productForFill, zNegativeLeptonPt, D);
    ADD_BRANCH(tree, productForFill, zNegativeLeptonPhi, D);
    ADD_BRANCH(tree, productForFill, zNegativeLeptonEta, D);

    ADD_BRANCH(tree, productForFill, lepton1Pt, D);
    ADD_BRANCH(tree, productForFill, lepton1Phi, D);
    ADD_BRANCH(tree, productForFill, lepton1Eta, D);
    ADD_BRANCH(tree, productForFill, lepton1PDGId, I);

    ADD_BRANCH(tree, productForFill, lepton2Pt, D);
    ADD_BRANCH(tree, productForFill, lepton2Phi, D);
    ADD_BRANCH(tree, productForFill, lepton2Eta, D);
    ADD_BRANCH(tree, productForFill, lepton2PDGId, I);

    ADD_BRANCH(tree, productForFill, jet1Pt, D);
    ADD_BRANCH(tree, productForFill, jet1Phi, D);
    ADD_BRANCH(tree, productForFill, jet1Eta, D);
    ADD_BRANCH(tree, productForFill, jet1Y, D);
    ADD_BRANCH(tree, productForFill, jet1Id, I);

    ADD_BRANCH(tree, productForFill, jet2Pt, D);
    ADD_BRANCH(tree, productForFill, jet2Phi, D);
    ADD_BRANCH(tree, productForFill, jet2Eta, D);
    ADD_BRANCH(tree, productForFill, jet2Y, D);
    ADD_BRANCH(tree, productForFill, jet2Id, I);

    ADD_BRANCH(tree, productForFill, met, D);
    ADD_BRANCH(tree, productForFill, sumEt, D);
    ADD_BRANCH(tree, productForFill, metRaw, D);
    ADD_BRANCH(tree, productForFill, sumEtRaw, D);

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
        // gen jets (matched to reco)
        ADD_BRANCH(tree, productForFill, jet1MatchedGenJetPt, D);
        ADD_BRANCH(tree, productForFill, jet1MatchedGenJetPhi, D);
        ADD_BRANCH(tree, productForFill, jet1MatchedGenJetEta, D);
        ADD_BRANCH(tree, productForFill, jet1MatchedGenJetY, D);
        ADD_BRANCH(tree, productForFill, jet2MatchedGenJetPt, D);
        ADD_BRANCH(tree, productForFill, jet2MatchedGenJetPhi, D);
        ADD_BRANCH(tree, productForFill, jet2MatchedGenJetEta, D);
        ADD_BRANCH(tree, productForFill, jet2MatchedGenJetY, D);
        // weights
        ADD_BRANCH(tree, productForFill, generatorWeight, D);
        ADD_BRANCH(tree, productForFill, generatorWeightProduct, D);
        ADD_BRANCH(tree, productForFill, weightForStitching, D);
        ADD_BRANCH(tree, productForFill, pileupWeight, D);
        // binning values
        ADD_BRANCH(tree, productForFill, binningValue, D);
    }

}


void zjet::NtupleFlatOutput::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    // call parent
    NtupleFlatOutputAnalyzerBase<zjet::NtupleEntry>::fillDescriptions(descriptions);

    // The following says we do not know what parameters are allowed so do no validation
    // Please change this to state exactly what you do use, even if it is no parameters
    edm::ParameterSetDescription desc;
    desc.setUnknown();
    descriptions.addDefault(desc);
}


// register type for RTTI / completeness check
REGISTER_NTUPLE_ENTRY_TYPE(zjet::NtupleEntry);

//define this as a plug-in
using ZJetNtupleFlatOutput = zjet::NtupleFlatOutput;
DEFINE_FWK_MODULE(ZJetNtupleFlatOutput);
