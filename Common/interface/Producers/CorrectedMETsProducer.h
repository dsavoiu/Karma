#pragma once

// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/StreamID.h"

#include "Karma/Common/interface/EDMTools/Util.h"

// -- output data formats
#include "Karma/SkimmingFormats/interface/Event.h"

// -- input data formats
#include "Karma/SkimmingFormats/interface/Event.h"
#include "Karma/SkimmingFormats/interface/Lumi.h"
#include "Karma/SkimmingFormats/interface/Run.h"


//
// class declaration
//
namespace karma {
    // -- caches

    // -- main producer

    class CorrectedMETsProducer : public edm::stream::EDProducer<> {

      public:
        explicit CorrectedMETsProducer(const edm::ParameterSet&);
        ~CorrectedMETsProducer();

        // -- pSet descriptions for CMSSW help info
        static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

        // -- "regular" per-Event 'produce' method
        virtual void produce(edm::Event&, const edm::EventSetup&);


      private:

        // ----------member data ---------------------------

        const edm::ParameterSet& m_configPSet;
        const double typeICorrectionMinJetPt_;
        const double typeICorrectionMaxTotalEMFraction_;
        const std::string typeICorrectionJECReferenceLevel_;

        // -- handles and tokens
        typename edm::Handle<karma::Event> karmaEventHandle;
        edm::EDGetTokenT<karma::Event> karmaEventToken;

        typename edm::Handle<karma::METCollection> karmaMETCollectionHandle;
        edm::EDGetTokenT<karma::METCollection> karmaMETCollectionToken;

        typename edm::Handle<karma::JetCollection> karmaCorrectedJetCollectionHandle;
        edm::EDGetTokenT<karma::JetCollection> karmaCorrectedJetCollectionToken;

    };
}  // end namespace
