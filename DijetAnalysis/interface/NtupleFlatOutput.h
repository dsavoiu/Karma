#pragma once

// system include files
#include <memory>

//#include "TClass.h"
#include "TTree.h"

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/one/EDAnalyzer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/StreamID.h"
#include "FWCore/Utilities/interface/TypeWithDict.h"
#include "FWCore/Utilities/interface/MemberWithDict.h"

#include "CommonTools/Utils/interface/StringCutObjectSelector.h"

// -- base classes for caches
#include "Karma/Common/interface/Caches.h"

// -- output data formats
#include "Karma/DijetAnalysisFormats/interface/Ntuple.h"

//
// class declaration
//
namespace dijet {

    // -- main producer

    class NtupleFlatOutput : public edm::one::EDAnalyzer<
        edm::one::SharedResources  // enable serialization of all calls to this module
    > {

      public:
        explicit NtupleFlatOutput(const edm::ParameterSet&);
        ~NtupleFlatOutput();

        // -- pSet descriptions for CMSSW help info
        static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

        // -- filter method
        virtual void analyze(const edm::Event&, const edm::EventSetup&) override;

        // -- method to run at job end
        virtual void endJob() override;


      private:

        // ----------member data ---------------------------

        const edm::ParameterSet& m_configPSet;
        bool m_isData;

        // bare pointers (ROOT will manage this memory)
        TTree* m_tree;  // will be owened and destroyed by ROOT
        dijet::NtupleEntry* m_productForFill;  // will clean up in destructor

        // -- handles and tokens
        typename edm::Handle<dijet::NtupleEntry> dijetNtupleEntryHandle;
        edm::EDGetTokenT<dijet::NtupleEntry> dijetNtupleEntryToken;

    };
}  // end namespace
