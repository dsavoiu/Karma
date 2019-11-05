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

// for random number generator service
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "FWCore/Utilities/interface/RandomNumberGenerator.h"
#include "CLHEP/Random/RandomEngine.h"
#include "CLHEP/Random/RandGaussT.h"

// for JER smearing
#include "JetMETCorrections/Modules/interface/JetResolution.h"

#include "Karma/Common/interface/EDMTools/Caches.h"
#include "Karma/Common/interface/EDMTools/Util.h"
#include "Karma/Common/interface/Providers/JetIDProvider.h"

// JEC and JER-related objects
#include "CondFormats/JetMETObjects/interface/FactorizedJetCorrector.h"
#include "CondFormats/JetMETObjects/interface/JetCorrectionUncertainty.h"
#include "CondFormats/JetMETObjects/interface/JetCorrectorParameters.h"

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

    class SmearedJetsProducer : public edm::stream::EDProducer<> {

      public:
        explicit SmearedJetsProducer(const edm::ParameterSet&);
        ~SmearedJetsProducer();

        // -- pSet descriptions for CMSSW help info
        static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

        // -- "regular" per-Event 'produce' method
        virtual void produce(edm::Event&, const edm::EventSetup&);


      private:

        // ----------member data ---------------------------

        const edm::ParameterSet& m_configPSet;

        const karma::LV* getMatchedGenJet(unsigned int jetIndex);

        // CMSSW value providers
        std::unique_ptr<JME::JetResolution> m_jetResolutionProvider;
        std::unique_ptr<JME::JetResolutionScaleFactor> m_jetResolutionScaleFactorProvider;
        Variation m_jerVariation = Variation::NOMINAL;
        bool m_stochasticOnly = true;

        // -- handles and tokens
        typename edm::Handle<karma::Event> karmaEventHandle;
        edm::EDGetTokenT<karma::Event> karmaEventToken;

        typename edm::Handle<karma::JetCollection> karmaJetCollectionHandle;
        edm::EDGetTokenT<karma::JetCollection> karmaJetCollectionToken;

        typename edm::Handle<karma::JetGenJetMap> karmaJetGenJetMapHandle;
        edm::EDGetTokenT<karma::JetGenJetMap> karmaJetGenJetMapToken;

    };
}  // end namespace
