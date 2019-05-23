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
namespace dijet {
    // -- caches

    /** Cache containing resources which do not change
     *  for the entire duration of the analysis job.
     */
    class CorrectedValidJetsProducerGlobalCache : public karma::CacheBase {

      public:
        CorrectedValidJetsProducerGlobalCache(const edm::ParameterSet& pSet) : karma::CacheBase(pSet) {

            // if JetID set to 'None', leave jetIDProvider_ as nullptr
            if (pSet_.getParameter<std::string>("jetIDSpec") != "None") {
                jetIDProvider_ = std::unique_ptr<karma::JetIDProvider>(
                    new karma::JetIDProvider(
                        pSet_.getParameter<std::string>("jetIDSpec"),
                        pSet_.getParameter<std::string>("jetIDWorkingPoint")
                    )
                );
            }
        };

        std::unique_ptr<karma::JetIDProvider> jetIDProvider_;

    };

    // -- main producer

    class CorrectedValidJetsProducer : public edm::stream::EDProducer<
        edm::GlobalCache<dijet::CorrectedValidJetsProducerGlobalCache>
    > {

      public:
        explicit CorrectedValidJetsProducer(const edm::ParameterSet&, const dijet::CorrectedValidJetsProducerGlobalCache*);
        ~CorrectedValidJetsProducer();

        // -- global cache extension
        static std::unique_ptr<dijet::CorrectedValidJetsProducerGlobalCache> initializeGlobalCache(const edm::ParameterSet& pSet);
        static void globalEndJob(const dijet::CorrectedValidJetsProducerGlobalCache*) {/* noop */};

        // -- pSet descriptions for CMSSW help info
        static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

        // -- "regular" per-Event 'produce' method
        virtual void produce(edm::Event&, const edm::EventSetup&);


      private:

        // static method for setting up either a `FactorizedJetCorrector` or a `JetCorrectionUncertainty`
        template<typename TFactorProvider>
        static void setupFactorProvider(TFactorProvider& factorProvider, const karma::Jet& jet) {
            factorProvider.setJetEta(jet.uncorP4.eta());
            factorProvider.setJetPt(jet.uncorP4.pt());
            factorProvider.setJetE(jet.uncorP4.E());
            factorProvider.setJetPhi(jet.uncorP4.phi());
        };

        static void setupFactorizedJetCorrector(FactorizedJetCorrector& jetCorrector, const karma::Event& dijetEvent, const karma::Jet& jet) {
            setupFactorProvider(jetCorrector, jet);
            jetCorrector.setJetA(jet.area);
            jetCorrector.setRho(static_cast<float>(dijetEvent.rho));
            //jetCorrector.setNPV(dijetEvent.npvGood);  // TODO: npv?
            jetCorrector.setNPV(dijetEvent.npv);
        };

        // ----------member data ---------------------------

        const edm::ParameterSet& m_configPSet;

        std::unique_ptr<FactorizedJetCorrector> m_jetCorrector;
        std::unique_ptr<FactorizedJetCorrector> m_jetCorrector_L1;
        std::unique_ptr<FactorizedJetCorrector> m_jetCorrector_L1RC;
        std::unique_ptr<JetCorrectionUncertainty> m_jetCorrectionUncertainty;
        double m_jecUncertaintyShift = 0.0;

        // -- handles and tokens
        typename edm::Handle<karma::Event> karmaEventHandle;
        edm::EDGetTokenT<karma::Event> karmaEventToken;

        typename edm::Handle<karma::JetCollection> karmaJetCollectionHandle;
        edm::EDGetTokenT<karma::JetCollection> karmaJetCollectionToken;

    };
}  // end namespace
