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

#include "Karma/Common/interface/EDMTools/Util.h"

//
// class declaration
//
namespace karma {

    // -- filter template

    template<typename TNtupleEntry>
    class NtupleFilterBase : public edm::stream::EDFilter<> {

      public:
        explicit NtupleFilterBase(const edm::ParameterSet& config) : m_configPSet(config) {
            // -- this filter will run on the analysis ntuple
            ntupleEntryToken = this->template consumes<TNtupleEntry>(
                m_configPSet.template getParameter<edm::InputTag>("ntupleSrc")
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
            karma::util::getByTokenOrThrow(event, this->ntupleEntryToken, this->ntupleEntryHandle);

            return filterNtupleEntry(*ntupleEntryHandle);
        };

        // ntuple entry filter: to be overridden by user
        virtual bool filterNtupleEntry(const TNtupleEntry&) = 0;


      private:

        // ----------member data ---------------------------

        const edm::ParameterSet& m_configPSet;

        // -- handles and tokens
        typename edm::Handle<TNtupleEntry> ntupleEntryHandle;
        edm::EDGetTokenT<TNtupleEntry> ntupleEntryToken;

    };
}  // end namespace
