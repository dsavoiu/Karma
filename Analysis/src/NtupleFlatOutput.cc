// system include files
#include <iostream>

#include <TROOT.h>
#include "TClass.h"
#include "TLeaf.h"

#include "DijetAnalysis/Analysis/interface/NtupleFlatOutput.h"

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
    m_tree->Branch("run",                                          &m_productForFill->run,                                           "run/L"                                          );
    m_tree->Branch("lumi",                                         &m_productForFill->lumi,                                          "lumi/I"                                         );
    m_tree->Branch("event",                                        &m_productForFill->event,                                         "event/L"                                        );
    m_tree->Branch("bx",                                           &m_productForFill->bx,                                            "bx/I"                                           );
    m_tree->Branch("rho",                                          &m_productForFill->rho,                                           "rho/D"                                          );
    m_tree->Branch("npv",                                          &m_productForFill->npv,                                           "npv/I"                                          );
    m_tree->Branch("npvGood",                                      &m_productForFill->npvGood,                                       "npvGood/I"                                      );
    m_tree->Branch("jet1pt",                                       &m_productForFill->jet1pt,                                        "jet1pt/D"                                       );
    m_tree->Branch("jet1phi",                                      &m_productForFill->jet1phi,                                       "jet1phi/D"                                      );
    m_tree->Branch("jet1eta",                                      &m_productForFill->jet1eta,                                       "jet1eta/D"                                      );
    m_tree->Branch("jet1y",                                        &m_productForFill->jet1y,                                         "jet1y/D"                                        );
    m_tree->Branch("jet1id",                                       &m_productForFill->jet1id,                                        "jet1id/I"                                       );
    m_tree->Branch("jet2pt",                                       &m_productForFill->jet2pt,                                        "jet2pt/D"                                       );
    m_tree->Branch("jet2phi",                                      &m_productForFill->jet2phi,                                       "jet2phi/D"                                      );
    m_tree->Branch("jet2eta",                                      &m_productForFill->jet2eta,                                       "jet2eta/D"                                      );
    m_tree->Branch("jet2y",                                        &m_productForFill->jet2y,                                         "jet2y/D"                                        );
    m_tree->Branch("jet2id",                                       &m_productForFill->jet2id,                                        "jet2id/I"                                       );
    m_tree->Branch("jet12mass",                                    &m_productForFill->jet12mass,                                     "jet12mass/D"                                    );
    m_tree->Branch("jet12ptave",                                   &m_productForFill->jet12ptave,                                    "jet12ptave/D"                                   );
    m_tree->Branch("jet12ystar",                                   &m_productForFill->jet12ystar,                                    "jet12ystar/D"                                   );
    m_tree->Branch("jet12yboost",                                  &m_productForFill->jet12yboost,                                   "jet12yboost/D"                                  );
    m_tree->Branch("met",                                          &m_productForFill->met,                                           "met/D"                                          );
    m_tree->Branch("sumEt",                                        &m_productForFill->sumEt,                                         "sumEt/D"                                        );
    m_tree->Branch("hltBits",                                      &m_productForFill->hltBits,                                       "hltBits/L"                                      );
    m_tree->Branch("hltJet1Match",                                 &m_productForFill->hltJet1Match,                                  "hltJet1Match/L"                                 );
    m_tree->Branch("hltJet2Match",                                 &m_productForFill->hltJet2Match,                                  "hltJet2Match/L"                                 );
    m_tree->Branch("hltJet1PtPassThresholds",                      &m_productForFill->hltJet1PtPassThresholds,                       "hltJet1PtPassThresholds/L"                      );
    m_tree->Branch("hltJet2PtPassThresholds",                      &m_productForFill->hltJet2PtPassThresholds,                       "hltJet2PtPassThresholds/L"                      );
    m_tree->Branch("hltJet12PtAvePassThresholds",                  &m_productForFill->hltJet12PtAvePassThresholds,                   "hltJet12PtAvePassThresholds/L"                  );
    // PF energy fractions
    m_tree->Branch("jet1NeutralHadronFraction",                    &m_productForFill->jet1NeutralHadronFraction,                     "jet1NeutralHadronFraction/D"                    );
    m_tree->Branch("jet1ChargedHadronFraction",                    &m_productForFill->jet1ChargedHadronFraction,                     "jet1ChargedHadronFraction/D"                    );
    m_tree->Branch("jet1MuonFraction",                             &m_productForFill->jet1MuonFraction,                              "jet1MuonFraction/D"                             );
    m_tree->Branch("jet1PhotonFraction",                           &m_productForFill->jet1PhotonFraction,                            "jet1PhotonFraction/D"                           );
    m_tree->Branch("jet1ElectronFraction",                         &m_productForFill->jet1ElectronFraction,                          "jet1ElectronFraction/D"                         );
    m_tree->Branch("jet1HFHadronFraction",                         &m_productForFill->jet1HFHadronFraction,                          "jet1HFHadronFraction/D"                         );
    m_tree->Branch("jet1HFEMFraction",                             &m_productForFill->jet1HFEMFraction,                              "jet1HFEMFraction/D"                             );
    m_tree->Branch("jet2NeutralHadronFraction",                    &m_productForFill->jet2NeutralHadronFraction,                     "jet2NeutralHadronFraction/D"                    );
    m_tree->Branch("jet2ChargedHadronFraction",                    &m_productForFill->jet2ChargedHadronFraction,                     "jet2ChargedHadronFraction/D"                    );
    m_tree->Branch("jet2MuonFraction",                             &m_productForFill->jet2MuonFraction,                              "jet2MuonFraction/D"                             );
    m_tree->Branch("jet2PhotonFraction",                           &m_productForFill->jet2PhotonFraction,                            "jet2PhotonFraction/D"                           );
    m_tree->Branch("jet2ElectronFraction",                         &m_productForFill->jet2ElectronFraction,                          "jet2ElectronFraction/D"                         );
    m_tree->Branch("jet2HFHadronFraction",                         &m_productForFill->jet2HFHadronFraction,                          "jet2HFHadronFraction/D"                         );
    m_tree->Branch("jet2HFEMFraction",                             &m_productForFill->jet2HFEMFraction,                              "jet2HFEMFraction/D"                             );

    // MC
    if (!m_isData) {
        m_tree->Branch("jet1MatchedGenJetPt",                          &m_productForFill->jet1MatchedGenJetPt,                           "jet1MatchedGenJetPt/D"                          );
        m_tree->Branch("jet1MatchedGenJetPhi",                         &m_productForFill->jet1MatchedGenJetPhi,                          "jet1MatchedGenJetPhi/D"                         );
        m_tree->Branch("jet1MatchedGenJetEta",                         &m_productForFill->jet1MatchedGenJetEta,                          "jet1MatchedGenJetEta/D"                         );
        m_tree->Branch("jet1MatchedGenJetY",                           &m_productForFill->jet1MatchedGenJetY,                            "jet1MatchedGenJetY/D"                           );
        m_tree->Branch("jet2MatchedGenJetPt",                          &m_productForFill->jet2MatchedGenJetPt,                           "jet2MatchedGenJetPt/D"                          );
        m_tree->Branch("jet2MatchedGenJetPhi",                         &m_productForFill->jet2MatchedGenJetPhi,                          "jet2MatchedGenJetPhi/D"                         );
        m_tree->Branch("jet2MatchedGenJetEta",                         &m_productForFill->jet2MatchedGenJetEta,                          "jet2MatchedGenJetEta/D"                         );
        m_tree->Branch("jet2MatchedGenJetY",                           &m_productForFill->jet2MatchedGenJetY,                            "jet2MatchedGenJetY/D"                           );
        m_tree->Branch("jet12MatchedGenJetPairMass",                   &m_productForFill->jet12MatchedGenJetPairMass,                    "jet12MatchedGenJetPairMass/D"                   );
        m_tree->Branch("jet12MatchedGenJetPairPtAve",                  &m_productForFill->jet12MatchedGenJetPairPtAve,                   "jet12MatchedGenJetPairPtAve/D"                  );
        m_tree->Branch("jet12MatchedGenJetPairYStar",                  &m_productForFill->jet12MatchedGenJetPairYStar,                   "jet12MatchedGenJetPairYStar/D"                  );
        m_tree->Branch("jet12MatchedGenJetPairYBoost",                 &m_productForFill->jet12MatchedGenJetPairYBoost,                  "jet12MatchedGenJetPairYBoost/D"                 );
        // QCD subprocess info
        m_tree->Branch("incomingParton1Flavor",                        &m_productForFill->incomingParton1Flavor,                         "incomingParton1Flavor/I"                        );
        m_tree->Branch("incomingParton2Flavor",                        &m_productForFill->incomingParton2Flavor,                         "incomingParton2Flavor/I"                        );
        m_tree->Branch("incomingParton1x",                             &m_productForFill->incomingParton1x,                              "incomingParton1x/D"                             );
        m_tree->Branch("incomingParton2x",                             &m_productForFill->incomingParton2x,                              "incomingParton2x/D"                             );
        m_tree->Branch("alphaQCD",                                     &m_productForFill->alphaQCD,                                      "alphaQCD/D"                                     );
        m_tree->Branch("scalePDF",                                     &m_productForFill->scalePDF,                                      "scalePDF/D"                                     );
        // flavor
        m_tree->Branch("jet1PartonFlavor",                             &m_productForFill->jet1PartonFlavor,                              "jet1PartonFlavor/I"                             );
        m_tree->Branch("jet2PartonFlavor",                             &m_productForFill->jet2PartonFlavor,                              "jet2PartonFlavor/I"                             );
        m_tree->Branch("jet1HadronFlavor",                             &m_productForFill->jet1HadronFlavor,                              "jet1HadronFlavor/I"                             );
        m_tree->Branch("jet2HadronFlavor",                             &m_productForFill->jet2HadronFlavor,                              "jet2HadronFlavor/I"                             );
        // weights
        m_tree->Branch("generatorWeight",                              &m_productForFill->generatorWeight,                               "generatorWeight/D"                              );
        m_tree->Branch("generatorWeightProduct",                       &m_productForFill->generatorWeightProduct,                        "generatorWeightProduct/D"                       );
        m_tree->Branch("weightForStitching",                           &m_productForFill->weightForStitching,                            "weightForStitching/D"                           );
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
