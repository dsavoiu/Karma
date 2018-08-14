#pragma once

// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDFilter.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"


// -- input data formats
#include "DijetAnalysis/AnalysisFormats/interface/Ntuple.h"


//
// class declaration
//
namespace dijet {

    // -- main filter

    class NtupleFilterBase : public edm::stream::EDFilter<> {

      public:
        explicit NtupleFilterBase(const edm::ParameterSet& config) : m_configPSet(config) {
            // -- this filter will run on the analysis ntuple
            dijetNtupleEntryToken = this->template consumes<dijet::NtupleEntry>(
                m_configPSet.template getParameter<edm::InputTag>("dijetNtupleSrc")
            );
        }
        ~NtupleFilterBase() {};

        // -- pSet descriptions for CMSSW help info
        static void fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
            // The following says we do not know what parameters are allowed so do no validation
            // Please change this to state exactly what you do use, even if it is no parameters
            edm::ParameterSetDescription desc;
            desc.setUnknown();
            descriptions.addDefault(desc);
        }

        // -- 'filter' method, called once per-Event
        virtual bool filter(edm::Event& event, const edm::EventSetup& setup) {
            // -- get object collections for event
            bool obtained = true;
            obtained &= event.getByToken(this->dijetNtupleEntryToken, this->dijetNtupleEntryHandle);
            assert(obtained);  // throw if one collection could not be obtained

            return filterNtupleEntry(*dijetNtupleEntryHandle);
        };

        // ntuple entry filter: to be overridden by user
        virtual bool filterNtupleEntry(const dijet::NtupleEntry&) = 0;


      private:

        // ----------member data ---------------------------

        const edm::ParameterSet& m_configPSet;

        // -- handles and tokens
        typename edm::Handle<dijet::NtupleEntry> dijetNtupleEntryHandle;
        edm::EDGetTokenT<dijet::NtupleEntry> dijetNtupleEntryToken;

    };
}  // end namespace
