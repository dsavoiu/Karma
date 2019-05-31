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


//
// class declaration
//
namespace karma {
    // -- caches

    /** Cache containing resources which do not change
     *  for the entire duration of the analysis job.
     */
    class ZBosonProducerGlobalCache : public karma::CacheBase {

      public:
        ZBosonProducerGlobalCache(const edm::ParameterSet& pSet) :
            karma::CacheBase(pSet),
            maxDeltaInvariantMass_(pSet_.getParameter<double>("maxDeltaInvariantMass")) {

        };

        double maxDeltaInvariantMass_;

    };

    // -- main producer
    template<typename TLeptonCollection>
    class ZBosonProducer : public edm::stream::EDProducer<
        edm::GlobalCache<karma::ZBosonProducerGlobalCache>
    > {

      public:
        explicit ZBosonProducer(const edm::ParameterSet& config, const karma::ZBosonProducerGlobalCache* globalCache):
            m_configPSet(config) {

            // -- register products
            produces<karma::LV>();
            produces<karma::LV>("positiveLepton");
            produces<karma::LV>("negativeLepton");

            m_matcher = std::unique_ptr<LowestAbsDeltaInvariantMassMatcher<TLeptonCollection>>(
                new LowestAbsDeltaInvariantMassMatcher<TLeptonCollection>(
                 /* targetInvariantMass = */ Z_BOSON_MASS_GEV,
                 /* maxDeltaInvariantMass = */ globalCache->maxDeltaInvariantMass_,
                 /* maxMatches = */ 1,
                 /* allowIdenticalIndices = */ true
                )
            );

            // -- declare which collections are consumed and create tokens
            karmaLeptonCollectionToken = consumes<TLeptonCollection>(m_configPSet.getParameter<edm::InputTag>("karmaLeptonCollectionSrc"));
        };
        virtual ~ZBosonProducer() {};

        // -- global cache extension
        static std::unique_ptr<karma::ZBosonProducerGlobalCache> initializeGlobalCache(const edm::ParameterSet& pSet) {
            // -- create the GlobalCache
            return std::unique_ptr<karma::ZBosonProducerGlobalCache>(new karma::ZBosonProducerGlobalCache(pSet));
        };
        static void globalEndJob(const karma::ZBosonProducerGlobalCache*) {/* noop */};

        // -- pSet descriptions for CMSSW help info
        static void fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
            // The following says we do not know what parameters are allowed so do no validation
            // Please change this to state exactly what you do use, even if it is no parameters
            edm::ParameterSetDescription desc;
            desc.setUnknown();
            descriptions.addDefault(desc);
        };

        // -- "regular" per-Event 'produce' method
        virtual void produce(edm::Event& event, const edm::EventSetup& setup) {
            karma::util::getByTokenOrThrow(event, this->karmaLeptonCollectionToken, this->karmaLeptonCollectionHandle);
            std::unique_ptr<karma::LV> zBosonLV(new karma::LV());
            std::unique_ptr<karma::LV> positiveLeptonLV(new karma::LV());
            std::unique_ptr<karma::LV> negativeLeptonLV(new karma::LV());

            // separate leptons into two collections by charge
            TLeptonCollection positiveLeptons;
            std::copy_if(
                (*this->karmaLeptonCollectionHandle).begin(),
                (*this->karmaLeptonCollectionHandle).end(),
                std::back_inserter(positiveLeptons),
                [](const typename TLeptonCollection::value_type& lepton) {
                    return (lepton.charge > 0);
                }
            );
            TLeptonCollection negativeLeptons;
            std::copy_if(
                (*this->karmaLeptonCollectionHandle).begin(),
                (*this->karmaLeptonCollectionHandle).end(),
                std::back_inserter(negativeLeptons),
                [](const typename TLeptonCollection::value_type& lepton) {
                    return (lepton.charge < 0);
                }
            );

            // apply matcher between opposite-charge collections
            const auto& matchingIndexPairs = this->m_matcher->match(
                positiveLeptons, negativeLeptons
            );

            if (matchingIndexPairs.size() != 0) {
                assert(matchingIndexPairs.size() == 1);  // should always have at most one matched lepton pair
                positiveLeptonLV->p4 = positiveLeptons.at(matchingIndexPairs.at(0).first).p4;
                negativeLeptonLV->p4 = negativeLeptons.at(matchingIndexPairs.at(0).second).p4;
                zBosonLV->p4 = positiveLeptonLV->p4 + negativeLeptonLV->p4;
            }
            event.put(std::move(zBosonLV));
            event.put(std::move(positiveLeptonLV), "positiveLepton");
            event.put(std::move(negativeLeptonLV), "negativeLepton");
        };


      private:

        // ----------member data ---------------------------

        const edm::ParameterSet& m_configPSet;

        std::unique_ptr<LowestAbsDeltaInvariantMassMatcher<TLeptonCollection>> m_matcher;

        static constexpr const double Z_BOSON_MASS_GEV = 91.1876;

        typename edm::Handle<TLeptonCollection> karmaLeptonCollectionHandle;
        edm::EDGetTokenT<TLeptonCollection> karmaLeptonCollectionToken;

    };

}  // end namespace
