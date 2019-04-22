#pragma once

// system include files
#include <memory>
#include <numeric>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDFilter.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"


// -- input data formats
#include "Karma/SkimmingFormats/interface/Event.h"


//
// class declaration
//
namespace karma {

    // -- main producer

    class EventHLTFilter : public edm::stream::EDFilter<> {

      public:
        explicit EventHLTFilter(const edm::ParameterSet&);
        ~EventHLTFilter() {};

        // -- pSet descriptions for CMSSW help info
        static void fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
            // The following says we do not know what parameters are allowed so do no validation
            // Please change this to state exactly what you do use, even if it is no parameters
            edm::ParameterSetDescription desc;
            desc.setUnknown();
            descriptions.addDefault(desc);
        }

        // -- 'filter' method
        virtual bool filter(edm::Event&, const edm::EventSetup&);


      private:

        // ----------member data ---------------------------

        const edm::ParameterSet& m_configPSet;

        // -- handles and tokens
        typename edm::Handle<karma::Event> karmaEventHandle;
        edm::EDGetTokenT<karma::Event> karmaEventToken;

    };

}  // end namespace
