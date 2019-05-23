#pragma once

// system include files
#include <memory>

// user include files
#include "Karma/Common/interface/EDMTools/Util.h"

#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/StreamID.h"
//#include "FWCore/Utilities/interface/Transition.h"  // CMSSW 9+


// -- output data formats
#include "Karma/SkimmingFormats/interface/Event.h"

// -- input data formats
#include "SimDataFormats/GeneratorProducts/interface/GenEventInfoProduct.h"



//
// class declaration
//
namespace karma {

    // -- main producer

    class GeneratorQCDInfoProducer : public edm::stream::EDProducer<> {

      public:
        explicit GeneratorQCDInfoProducer(const edm::ParameterSet&);
        ~GeneratorQCDInfoProducer();

        // -- pSet descriptions for CMSSW help info
        static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

        // -- "regular" per-Event 'produce' method
        virtual void produce(edm::Event&, const edm::EventSetup&);


      private:

        // ----------member data ---------------------------

        const edm::ParameterSet& m_configPSet;

        // -- handles and tokens
        typename edm::Handle<GenEventInfoProduct> genEventInfoProductHandle;
        edm::EDGetTokenT<GenEventInfoProduct> genEventInfoProductToken;


    };

    //
    // constants, enums and typedefs
    //


    //
    // static data member definitions
    //

}  // end namespace
