#include "Karma/DijetAnalysis/interface/NtupleV2FlatOutput.h"

/* helper macro for writing TTree branches
 *                                                           branch name               product member name/type
 *                                                                    pointer to product member */
#define ADD_BRANCH(tree, product, branch, type) tree->Branch(#branch, &product->branch, #branch"/"#type);
#define ADD_ARRAY_BRANCH(tree, product, branch, size, type) tree->Branch(#branch, &product->branch, #branch"["#size"]/"#type);
// -- branches of simple STL types (vector, list, deque, etc.) can be added directly
#define ADD_STL_BRANCH(tree, product, branch) tree->Branch(#branch, &product->branch);

// Note: ADD_BRANCH(tree, product, branch, type) expands to:
//    tree->Branch("branch", &product->branch, "branch/type")

// -- TTree wiring
void dijet::NtupleV2FlatOutput::setUpTTree(TTree* tree, dijet::NtupleV2Entry* productForFill) {

    ADD_BRANCH(tree, productForFill, run, L);
    ADD_BRANCH(tree, productForFill, lumi, I);
    ADD_BRANCH(tree, productForFill, event, L);
    ADD_BRANCH(tree, productForFill, bx, I);
    ADD_BRANCH(tree, productForFill, randomUniform, D);

    ADD_BRANCH(tree, productForFill, rho, D);
    ADD_BRANCH(tree, productForFill, nPUMean, D);
    if (m_isData) {
        // shifts based on minBias XS uncertainty, only
        // relevant in DATA
        ADD_BRANCH(tree, productForFill, nPUMeanUp, D);
        ADD_BRANCH(tree, productForFill, nPUMeanDown, D);
    }

    ADD_BRANCH(tree, productForFill, npv, I);
    ADD_BRANCH(tree, productForFill, npvGood, I);

    ADD_BRANCH(tree, productForFill, prefiringWeight, D);
    ADD_BRANCH(tree, productForFill, prefiringWeightUp, D);
    ADD_BRANCH(tree, productForFill, prefiringWeightDown, D);

    ADD_STL_BRANCH(tree, productForFill, Jet_pt);
    ADD_STL_BRANCH(tree, productForFill, Jet_phi);
    ADD_STL_BRANCH(tree, productForFill, Jet_eta);
    ADD_STL_BRANCH(tree, productForFill, Jet_mass);
    ADD_STL_BRANCH(tree, productForFill, Jet_area);
    ADD_STL_BRANCH(tree, productForFill, Jet_rawFactor);
    ADD_STL_BRANCH(tree, productForFill, Jet_hadronFlavor);
    ADD_STL_BRANCH(tree, productForFill, Jet_partonFlavor);
    ADD_STL_BRANCH(tree, productForFill, Jet_jerScaleFactor);
    ADD_STL_BRANCH(tree, productForFill, Jet_jerSmearingFactor);
    if (!m_isData) {
        ADD_STL_BRANCH(tree, productForFill, Jet_genJetMatch);
    }
    ADD_STL_BRANCH(tree, productForFill, Jet_hltMatch);
    ADD_STL_BRANCH(tree, productForFill, Jet_l1Match);
    ADD_STL_BRANCH(tree, productForFill, Jet_hltPassPtAveThreshold);
    ADD_STL_BRANCH(tree, productForFill, Jet_hltPassPtThreshold);
    ADD_STL_BRANCH(tree, productForFill, Jet_l1PassPtThreshold);
    ADD_STL_BRANCH(tree, productForFill, Jet_jetId);
    // PF energy fractions & multiplicities
    ADD_STL_BRANCH(tree, productForFill, Jet_NHF);
    ADD_STL_BRANCH(tree, productForFill, Jet_NEMF);
    ADD_STL_BRANCH(tree, productForFill, Jet_CHF);
    ADD_STL_BRANCH(tree, productForFill, Jet_MUF);
    ADD_STL_BRANCH(tree, productForFill, Jet_CEMF);
    ADD_STL_BRANCH(tree, productForFill, Jet_NumConst);
    ADD_STL_BRANCH(tree, productForFill, Jet_NumNeutralParticles);
    ADD_STL_BRANCH(tree, productForFill, Jet_jesUncertaintyFactors);

    ADD_BRANCH(tree, productForFill, MET_pt, D);
    ADD_BRANCH(tree, productForFill, MET_sumEt, D);
    ADD_BRANCH(tree, productForFill, MET_rawPt, D);
    ADD_BRANCH(tree, productForFill, MET_rawSumEt, D);

    ADD_BRANCH(tree, productForFill, metFilterBits, L);
    ADD_BRANCH(tree, productForFill, triggerResults, L);
    ADD_STL_BRANCH(tree, productForFill, triggerPrescales);

    // MC
    if (!m_isData) {
        // per-trigger pileup weights
        ADD_STL_BRANCH(tree, productForFill, triggerPileupWeights);
        ADD_STL_BRANCH(tree, productForFill, triggerPileupWeightsUp);
        ADD_STL_BRANCH(tree, productForFill, triggerPileupWeightsDown);
        ADD_STL_BRANCH(tree, productForFill, triggerPileupWeightsAlt);
        ADD_STL_BRANCH(tree, productForFill, triggerPileupWeightsAltUp);
        ADD_STL_BRANCH(tree, productForFill, triggerPileupWeightsAltDown);

        // number of pile-up interactions
        ADD_BRANCH(tree, productForFill, nPU, I);

        // QCD subprocess info
        ADD_BRANCH(tree, productForFill, incomingParton1Flavor, I);
        ADD_BRANCH(tree, productForFill, incomingParton2Flavor, I);
        ADD_BRANCH(tree, productForFill, incomingParton1x, D);
        ADD_BRANCH(tree, productForFill, incomingParton2x, D);
        ADD_BRANCH(tree, productForFill, alphaQCD, D);
        ADD_BRANCH(tree, productForFill, scalePDF, D);
        // flavor
        /* -- not needed for now
        ADD_BRANCH(tree, productForFill, jet1PartonFlavor, I);
        ADD_BRANCH(tree, productForFill, jet2PartonFlavor, I);
        ADD_BRANCH(tree, productForFill, jet1HadronFlavor, I);
        ADD_BRANCH(tree, productForFill, jet2HadronFlavor, I);
        */

        // weights
        ADD_BRANCH(tree, productForFill, generatorWeight, D);
        ADD_BRANCH(tree, productForFill, stitchingWeight, D);
        ADD_BRANCH(tree, productForFill, pileupWeight, D);
        ADD_BRANCH(tree, productForFill, pileupWeightUp, D);
        ADD_BRANCH(tree, productForFill, pileupWeightDown, D);
        ADD_BRANCH(tree, productForFill, pileupWeightAlt, D);
        ADD_BRANCH(tree, productForFill, pileupWeightAltUp, D);
        ADD_BRANCH(tree, productForFill, pileupWeightAltDown, D);
        ADD_BRANCH(tree, productForFill, pileupWeightSimulatedHLT, D);
        ADD_BRANCH(tree, productForFill, pileupWeightSimulatedHLTUp, D);
        ADD_BRANCH(tree, productForFill, pileupWeightSimulatedHLTDown, D);

        // binning values
        ADD_BRANCH(tree, productForFill, binningValue, D);

        // gen jets (not matched to reco)
        ADD_STL_BRANCH(tree, productForFill, GenJet_pt);
        ADD_STL_BRANCH(tree, productForFill, GenJet_phi);
        ADD_STL_BRANCH(tree, productForFill, GenJet_eta);
        ADD_STL_BRANCH(tree, productForFill, GenJet_mass);
    }
}


void dijet::NtupleV2FlatOutput::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    // call parent
    NtupleFlatOutputAnalyzerBase<dijet::NtupleV2Entry>::fillDescriptions(descriptions);

    // The following says we do not know what parameters are allowed so do no validation
    // Please change this to state exactly what you do use, even if it is no parameters
    edm::ParameterSetDescription desc;
    desc.setUnknown();
    descriptions.addDefault(desc);
}


// register type for RTTI / completeness check
REGISTER_NTUPLE_ENTRY_TYPE(dijet::NtupleV2Entry);

//define this as a plug-in
using DijetNtupleV2FlatOutput = dijet::NtupleV2FlatOutput;
DEFINE_FWK_MODULE(DijetNtupleV2FlatOutput);
