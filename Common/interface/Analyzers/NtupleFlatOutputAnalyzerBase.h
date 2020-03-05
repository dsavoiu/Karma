#pragma once

// system include files
#include <memory>
#include <iostream>

#include <TROOT.h>
#include "TTree.h"
#include "TClass.h"
#include "TLeaf.h"

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/one/EDAnalyzer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/StreamID.h"

#if (CMSSW_MAJOR_VERSION >= 11)
#include "FWCore/Reflection/interface/TypeWithDict.h"
#include "FWCore/Reflection/interface/MemberWithDict.h"
#else
#include "FWCore/Utilities/interface/TypeWithDict.h"
#include "FWCore/Utilities/interface/MemberWithDict.h"
#endif

#include "CommonTools/Utils/interface/StringCutObjectSelector.h"

// -- base classes for caches
#include "Karma/Common/interface/EDMTools/Caches.h"
#include "Karma/Common/interface/EDMTools/Util.h"

#define REGISTER_NTUPLE_ENTRY_TYPE(TNtupleEntry) template<> const char* karma::NtupleFlatOutputAnalyzerBase<TNtupleEntry>::NTUPLE_ENTRY_TYPE = #TNtupleEntry;

//
// class declaration
//
namespace karma {

    // -- main producer

    template<typename TNtupleEntry>
    class NtupleFlatOutputAnalyzerBase : public edm::one::EDAnalyzer<
        edm::one::SharedResources  // enable serialization of all calls to this module
    > {

      public:
        explicit NtupleFlatOutputAnalyzerBase(const edm::ParameterSet& config) : m_configPSet(config) {

            // -- process configuration

            // -- declare which collections are consumed and create tokens
            // the only input here is the analysis ntuple
            ntupleEntryToken = this->template consumes<TNtupleEntry>(
                m_configPSet.template getParameter<edm::InputTag>("ntupleSrc")
            );

            // declare use of shared resources -> all calls to analyze() will be serialized
            usesResource("TFileService");

            // access output ROOT file through TFileService
            edm::Service<TFileService> fileService;

            // create a TTree
            m_tree = fileService->make<TTree>(m_configPSet.getParameter<std::string>("treeName").c_str(),
                                              m_configPSet.getParameter<std::string>("treeName").c_str());

            // create a proxy product instance to use when filling
            m_productForFill = new TNtupleEntry();
        }

        virtual ~NtupleFlatOutputAnalyzerBase() {
            // do *not* delete TTree (ROOT does this on TFile::Close()!)
            delete m_productForFill;  // but *do* delete proxy product
        };

        // -- method to run at job beginning
        virtual void beginJob() override {
            // NOTE: need to put TTree initialization in beginJob since virtual calls are not
            //       allowed in constructor

            // initialize a TTree branch for each of the product members
            std::cout << "[NtupleFlatOutputAnalyzerBase] Wiring TTree branches..." << std::endl;
            setUpTTree(m_tree, m_productForFill);  // call user setup code
            std::cout << "[NtupleFlatOutputAnalyzerBase] Done wiring TTree branches" << std::endl;

            // -- check added branches for completeness

            if (m_configPSet.getParameter<bool>("checkForCompleteness")) {

                //const auto& ntupleEntryTypeString = m_configPSet.getParameter<std::string>("ntupleEntryType");
                std::cout << "[NtupleFlatOutputAnalyzerBase] Checking wired TTree branches for completeness..." << std::endl;
                std::cout << "[NtupleFlatOutputAnalyzerBase] Ntuple entry type is: " << this->NTUPLE_ENTRY_TYPE << std::endl;
                //std::cout << "[NtupleFlatOutputAnalyzerBase] Ntuple entry type is: " << NTUPLE_ENTRY_TYPE << std::endl;

                // RTTI helper objects
                edm::TypeWithDict productTypeWithDict = edm::TypeWithDict::byName(this->NTUPLE_ENTRY_TYPE);
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

        };

        // -- pSet descriptions for CMSSW help info
        static void fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
            // The following says we do not know what parameters are allowed so do no validation
            // Please change this to state exactly what you do use, even if it is no parameters
            edm::ParameterSetDescription desc;
            desc.setUnknown();
            descriptions.addDefault(desc);
        };

        // -- main analyzer method
        virtual void analyze(const edm::Event& event, const edm::EventSetup& setup) override {
            // -- get object collections for event

            // obtain ntuple entry
            karma::util::getByTokenOrThrow(event, this->ntupleEntryToken, this->ntupleEntryHandle);

            // copy event data
            *m_productForFill = *this->ntupleEntryHandle;
            m_tree->Fill();
        };

        // -- method to run at job end
        virtual void endJob() override {
            /* nothing to do: output written when TFile service closes output file */
        };

        // -- pure virtual methods

        virtual void setUpTTree(TTree* tree, TNtupleEntry* productForFill) = 0;  // delegate TTree setup to user

        // NOTE: constexpr would be better, but it is impossible to override
        //       constexpr members in template specializations
        static const char* NTUPLE_ENTRY_TYPE;  // for RTTI / completeness check

      protected:

        // ----------member data ---------------------------

        const edm::ParameterSet& m_configPSet;

      private:

        // bare pointers (ROOT will manage this memory)
        TTree* m_tree;  // will be owened and destroyed by ROOT
        TNtupleEntry* m_productForFill;  // will clean up in destructor

        // -- handles and tokens
        typename edm::Handle<TNtupleEntry> ntupleEntryHandle;
        edm::EDGetTokenT<TNtupleEntry> ntupleEntryToken;

    };
}  // end namespace
