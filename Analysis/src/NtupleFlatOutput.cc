// system include files
#include <iostream>

#include <TROOT.h>
#include "TClass.h"
#include "TLeaf.h"

#include "DijetAnalysis/Analysis/interface/NtupleFlatOutput.h"

/* helper macro for writing TTree branches
 *                                                           branch name               product member name/type
 *                                                                    pointer to product member */
#define ADD_BRANCH(tree, product, branch, type) tree->Branch(#branch, &product->branch, #branch"/"#type);

// Note: ADD_BRANCH(tree, product, branch, type) expands to:
//    tree->Branch("branch", &product->branch, "branch/type")

// -- constructor
dijet::NtupleFlatOutput::NtupleFlatOutput(const edm::ParameterSet& config) : m_configPSet(config) {

    // -- process configuration

    // set a flag if we are running on (real) data
    m_isData = m_configPSet.getParameter<bool>("isData");

    // -- declare which collections are consumed and create tokens
    // the only input here is the analysis ntuple
    dijetNtupleEntryToken = this->template consumes<dijet::NtupleEntry>(
        m_configPSet.template getParameter<edm::InputTag>("dijetNtupleSrc")
    );

    // declare use of shared resources -> all calls to analyze() will be serialized
    usesResource("TFileService");

    // access output ROOT file through TFileService
    edm::Service<TFileService> fileService;

    // create a TTree
    m_tree = fileService->make<TTree>(m_configPSet.getParameter<std::string>("treeName").c_str(),
                                      m_configPSet.getParameter<std::string>("treeName").c_str());

    // create a proxy product instance to use when filling
    m_productForFill = new dijet::NtupleEntry();

    // initialize a TTree branch for each of the product members
    std::cout << "Wiring TTree branches..." << std::endl;
    /*             branch name                                     pointer to product member                                         product member name/type                         */
    ADD_BRANCH(m_tree, m_productForFill, run, L);
    ADD_BRANCH(m_tree, m_productForFill, lumi, I);
    ADD_BRANCH(m_tree, m_productForFill, event, L);
    ADD_BRANCH(m_tree, m_productForFill, bx, I);
    ADD_BRANCH(m_tree, m_productForFill, rho, D);
    ADD_BRANCH(m_tree, m_productForFill, npv, I);
    ADD_BRANCH(m_tree, m_productForFill, npvGood, I);
    ADD_BRANCH(m_tree, m_productForFill, nPUMean, D);
    ADD_BRANCH(m_tree, m_productForFill, jet1pt, D);
    ADD_BRANCH(m_tree, m_productForFill, jet1phi, D);
    ADD_BRANCH(m_tree, m_productForFill, jet1eta, D);
    ADD_BRANCH(m_tree, m_productForFill, jet1y, D);
    ADD_BRANCH(m_tree, m_productForFill, jet1id, I);
    ADD_BRANCH(m_tree, m_productForFill, jet2pt, D);
    ADD_BRANCH(m_tree, m_productForFill, jet2phi, D);
    ADD_BRANCH(m_tree, m_productForFill, jet2eta, D);
    ADD_BRANCH(m_tree, m_productForFill, jet2y, D);
    ADD_BRANCH(m_tree, m_productForFill, jet2id, I);
    ADD_BRANCH(m_tree, m_productForFill, jet12mass, D);
    ADD_BRANCH(m_tree, m_productForFill, jet12ptave, D);
    ADD_BRANCH(m_tree, m_productForFill, jet12ystar, D);
    ADD_BRANCH(m_tree, m_productForFill, jet12yboost, D);
    ADD_BRANCH(m_tree, m_productForFill, binIndexJet12PtAve, I);
    ADD_BRANCH(m_tree, m_productForFill, binIndexJet12Mass, I);
    ADD_BRANCH(m_tree, m_productForFill, met, D);
    ADD_BRANCH(m_tree, m_productForFill, sumEt, D);
    ADD_BRANCH(m_tree, m_productForFill, hltBits, L);
    ADD_BRANCH(m_tree, m_productForFill, hltJet1Match, L);
    ADD_BRANCH(m_tree, m_productForFill, hltJet2Match, L);
    ADD_BRANCH(m_tree, m_productForFill, hltJet12Match, L);
    ADD_BRANCH(m_tree, m_productForFill, hltJet1PtPassThresholdsL1, L);
    ADD_BRANCH(m_tree, m_productForFill, hltJet1PtPassThresholdsHLT, L);
    ADD_BRANCH(m_tree, m_productForFill, hltJet2PtPassThresholdsL1, L);
    ADD_BRANCH(m_tree, m_productForFill, hltJet2PtPassThresholdsHLT, L);
    ADD_BRANCH(m_tree, m_productForFill, hltJet12PtAvePassThresholdsL1, L);
    ADD_BRANCH(m_tree, m_productForFill, hltJet12PtAvePassThresholdsHLT, L);
    // PF energy fractions
    ADD_BRANCH(m_tree, m_productForFill, jet1NeutralHadronFraction, D);
    ADD_BRANCH(m_tree, m_productForFill, jet1ChargedHadronFraction, D);
    ADD_BRANCH(m_tree, m_productForFill, jet1MuonFraction, D);
    ADD_BRANCH(m_tree, m_productForFill, jet1PhotonFraction, D);
    ADD_BRANCH(m_tree, m_productForFill, jet1ElectronFraction, D);
    ADD_BRANCH(m_tree, m_productForFill, jet1HFHadronFraction, D);
    ADD_BRANCH(m_tree, m_productForFill, jet1HFEMFraction, D);
    ADD_BRANCH(m_tree, m_productForFill, jet2NeutralHadronFraction, D);
    ADD_BRANCH(m_tree, m_productForFill, jet2ChargedHadronFraction, D);
    ADD_BRANCH(m_tree, m_productForFill, jet2MuonFraction, D);
    ADD_BRANCH(m_tree, m_productForFill, jet2PhotonFraction, D);
    ADD_BRANCH(m_tree, m_productForFill, jet2ElectronFraction, D);
    ADD_BRANCH(m_tree, m_productForFill, jet2HFHadronFraction, D);
    ADD_BRANCH(m_tree, m_productForFill, jet2HFEMFraction, D);

    // MC
    if (!m_isData) {
        // number of pile-up interactions
        ADD_BRANCH(m_tree, m_productForFill, nPU, I);
        // gen jets (not matched to reco)
        ADD_BRANCH(m_tree, m_productForFill, genJet1Pt, D);
        ADD_BRANCH(m_tree, m_productForFill, genJet1Phi, D);
        ADD_BRANCH(m_tree, m_productForFill, genJet1Eta, D);
        ADD_BRANCH(m_tree, m_productForFill, genJet1Y, D);
        ADD_BRANCH(m_tree, m_productForFill, genJet2Pt, D);
        ADD_BRANCH(m_tree, m_productForFill, genJet2Phi, D);
        ADD_BRANCH(m_tree, m_productForFill, genJet2Eta, D);
        ADD_BRANCH(m_tree, m_productForFill, genJet2Y, D);
        ADD_BRANCH(m_tree, m_productForFill, genJet12Mass, D);
        ADD_BRANCH(m_tree, m_productForFill, genJet12PtAve, D);
        ADD_BRANCH(m_tree, m_productForFill, genJet12YStar, D);
        ADD_BRANCH(m_tree, m_productForFill, genJet12YBoost, D);
        ADD_BRANCH(m_tree, m_productForFill, binIndexGenJet12PtAve, I);
        ADD_BRANCH(m_tree, m_productForFill, binIndexGenJet12Mass, I);
        // gen jets (matched to reco)
        ADD_BRANCH(m_tree, m_productForFill, jet1MatchedGenJetPt, D);
        ADD_BRANCH(m_tree, m_productForFill, jet1MatchedGenJetPhi, D);
        ADD_BRANCH(m_tree, m_productForFill, jet1MatchedGenJetEta, D);
        ADD_BRANCH(m_tree, m_productForFill, jet1MatchedGenJetY, D);
        ADD_BRANCH(m_tree, m_productForFill, jet2MatchedGenJetPt, D);
        ADD_BRANCH(m_tree, m_productForFill, jet2MatchedGenJetPhi, D);
        ADD_BRANCH(m_tree, m_productForFill, jet2MatchedGenJetEta, D);
        ADD_BRANCH(m_tree, m_productForFill, jet2MatchedGenJetY, D);
        ADD_BRANCH(m_tree, m_productForFill, jet12MatchedGenJetPairMass, D);
        ADD_BRANCH(m_tree, m_productForFill, jet12MatchedGenJetPairPtAve, D);
        ADD_BRANCH(m_tree, m_productForFill, jet12MatchedGenJetPairYStar, D);
        ADD_BRANCH(m_tree, m_productForFill, jet12MatchedGenJetPairYBoost, D);
        ADD_BRANCH(m_tree, m_productForFill, binIndexMatchedGenJet12PtAve, I);
        ADD_BRANCH(m_tree, m_productForFill, binIndexMatchedGenJet12Mass, I);
        // QCD subprocess info
        ADD_BRANCH(m_tree, m_productForFill, incomingParton1Flavor, I);
        ADD_BRANCH(m_tree, m_productForFill, incomingParton2Flavor, I);
        ADD_BRANCH(m_tree, m_productForFill, incomingParton1x, D);
        ADD_BRANCH(m_tree, m_productForFill, incomingParton2x, D);
        ADD_BRANCH(m_tree, m_productForFill, alphaQCD, D);
        ADD_BRANCH(m_tree, m_productForFill, scalePDF, D);
        // flavor
        ADD_BRANCH(m_tree, m_productForFill, jet1PartonFlavor, I);
        ADD_BRANCH(m_tree, m_productForFill, jet2PartonFlavor, I);
        ADD_BRANCH(m_tree, m_productForFill, jet1HadronFlavor, I);
        ADD_BRANCH(m_tree, m_productForFill, jet2HadronFlavor, I);
        // weights
        ADD_BRANCH(m_tree, m_productForFill, generatorWeight, D);
        ADD_BRANCH(m_tree, m_productForFill, generatorWeightProduct, D);
        ADD_BRANCH(m_tree, m_productForFill, weightForStitching, D);
        // binning values
        ADD_BRANCH(m_tree, m_productForFill, binningValue, D);
    }

    std::cout << "Done wiring TTree branches" << std::endl;

    // -- check added branches for completeness

    if (m_configPSet.getParameter<bool>("checkForCompleteness")) {

        // RTTI helper objects
        edm::TypeWithDict productTypeWithDict = edm::TypeWithDict::byName("dijet::NtupleEntry");
        edm::TypeDataMembers productTypeDataMembers(productTypeWithDict);

        // check for missing branches and branches with mismatched type sizes
        std::vector<std::string> missingBranches;
        std::map<std::string,std::pair<int,int>> mismatchedBranches;
        for (const auto& tdm : productTypeDataMembers) {
            // named local variables for readability
            const std::string& branchName = tdm->GetName();
            const std::string& branchTypeName = tdm->GetTypeName();
            TBranch* branchPtr = m_tree->GetBranch(branchName.c_str());
            if (!branchPtr) {
                missingBranches.push_back(branchName);
            }
            else {
                // check 1: number of leaves
                TObjArray* leafList = branchPtr->GetListOfLeaves();
                if (leafList->GetEntries() != 1) {
                    throw std::runtime_error("Unexpected leaf number (" + std::to_string(leafList->GetEntries()) + ") for branch '" + branchName + "'. Expected: 1");
                }
                // check 2: leaf data type size
                TLeaf* leaf = static_cast<TLeaf*>(leafList->At(0));
                if (!leaf) {
                    throw std::runtime_error("Could not get leaf for branch '" + branchName + "'");
                }
                int leafSize = gROOT->GetType(leaf->GetTypeName())->Size();
                int memberSize = gROOT->GetType(tdm->GetTypeName())->Size();
                if (leafSize != memberSize) {
                    mismatchedBranches[branchName] = std::make_pair(memberSize, leafSize);
                    //throw std::runtime_error("Size mismatch between TTree leaf and Ntuple data member '" + branchName + "': "
                    //                         "declared in Ntuple data format: " + std::to_string(memberSize) + ", "
                    //                         "declared in NtupleFlatOutput constructor (TTree leaf): " + std::to_string(leafSize) + "!");
                }
            }
        }

        if (missingBranches.size() > 0) {
            std::cout << "No branch created for the following Ntuple data members: " << std::endl;
            for (const auto& branchName : missingBranches) {
                std::cout << "    " << branchName << std::endl;
            }
            std::cout << "Please register these branches to the NtupleFlatOutput constructor!" << std::endl;
            throw std::runtime_error("Detected incomplete Ntuple writeout in NtupleFlatOutput!");
        }

        if (mismatchedBranches.size() > 0) {
            std::cout << "Declared branch type mismatch for the following Ntuple data members: " << std::endl;
            for (const auto branchNameSizePair : mismatchedBranches) {
                std::cout << "    " << branchNameSizePair.first << ":" << std::endl;
                std::cout << "        declared in Ntuple data format: " << branchNameSizePair.second.first << std::endl;
                std::cout << "        declared in NtupleFlatOutput constructor (TTree leaf): " << branchNameSizePair.second.second << std::endl;
            }
            std::cout << "Please correct the type of these branches in the NtupleFlatOutput constructor!" << std::endl;
            throw std::runtime_error("Detected mismatched branch types for Ntuple writeout in NtupleFlatOutput!");
        }

        /// // RTTI helper objects
        /// edm::TypeWithDict productTypeWithDict = edm::TypeWithDict::byName("dijet::NtupleEntry");
        /// edm::ObjectWithDict productObjectWithDict(productTypeWithDict, &m_productForFill);
        /// edm::TypeDataMembers productTypeDataMembers(productTypeWithDict);
        ///
        /// for (const auto& tdm : productTypeDataMembers) {
        ///     const edm::MemberWithDict member(tdm);  //
        ///     ////const edm::TypeWithDict memberTypeWithDict(member.typeOf())
        ///     // named local variables for readability
        ///     const std::string& branchName = tdm->GetName();
        ///     const std::string& branchTypeName = tdm->GetTypeName();
        ///     //std::cout << "m_productForFill." << branchName << " @ " << std::hex << productObjectWithDict.get(branchName).address() << std::dec << std::endl;
        ///     //m_tree->Bronch(branchName.c_str(), branchTypeName.c_str(), &(*dummy));
        ///     //m_tree->Bronch(branchName.c_str(), branchTypeName.c_str(), productObjectWithDict.get(branchName).address());
        ///     //short* objectPointerWithCorrectType = reinterpret_cast<short*>(productObjectWithDict.get(branchName).address());
        ///     m_tree->Branch(branchName.c_str(), branchTypeName.c_str(), productObjectWithDict.get(branchName).address());
        /// }
    }

}


void dijet::NtupleFlatOutput::endJob() {
    /* nothing to do: output written when TFile service closes output file */
}

// -- destructor
dijet::NtupleFlatOutput::~NtupleFlatOutput() {
    // do *not* delete TTree (ROOT does this on TFile::Close()!)
    delete m_productForFill;  // but *do* delete proxy product
}


// -- member functions

void dijet::NtupleFlatOutput::analyze(const edm::Event& event, const edm::EventSetup& setup) {

    // -- get object collections for event
    bool obtained = true;
    // ntuple entry
    obtained &= event.getByToken(this->dijetNtupleEntryToken, this->dijetNtupleEntryHandle);

    assert(obtained);  // raise if ntuple could not be obtained

    // copy event data
    *m_productForFill = *this->dijetNtupleEntryHandle;
    m_tree->Fill();

}


void dijet::NtupleFlatOutput::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    // The following says we do not know what parameters are allowed so do no validation
    // Please change this to state exactly what you do use, even if it is no parameters
    edm::ParameterSetDescription desc;
    desc.setUnknown();
    descriptions.addDefault(desc);
}


//define this as a plug-in
using dijet::NtupleFlatOutput;
DEFINE_FWK_MODULE(NtupleFlatOutput);
