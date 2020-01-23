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

#include "Karma/Common/interface/EDMTools/Caches.h"
#include "Karma/Common/interface/EDMTools/Util.h"
#include "Karma/Common/interface/Tools/Matchers.h"

#include "Karma/SkimmingFormats/interface/Event.h"

#include "TH2F.h"


//
// class declaration
//
namespace karma {

    // helper enum

    enum PrefiringVariation { central = 0, up = 1, down = 2 };

    // -- main producer

    class PrefiringWeightProducer : public edm::stream::EDProducer<> {

      public:
        explicit PrefiringWeightProducer(const edm::ParameterSet&);
        ~PrefiringWeightProducer();

        // -- pSet descriptions for CMSSW help info
        static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

        // -- "regular" per-Event 'produce' method
        virtual void produce(edm::Event&, const edm::EventSetup&);


      private:

        // ----------helper methods ------------------------

        double getPrefiringRate(double eta, double pt, PrefiringVariation var);

        // ----------member data ---------------------------

        const edm::ParameterSet& m_configPSet;

        double m_prefiringRateSysUnc;
        double m_maxPt;
        TH2F* m_prefiringWeightHist;

        // -- handles and tokens
        typename edm::Handle<karma::JetCollection> karmaJetCollectionHandle;
        edm::EDGetTokenT<karma::JetCollection> karmaJetCollectionToken;

    };

}  // end namespace
