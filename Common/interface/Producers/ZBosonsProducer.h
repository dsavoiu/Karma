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
    class ZBosonsProducerGlobalCache : public karma::CacheBase {

      public:
        ZBosonsProducerGlobalCache(const edm::ParameterSet& pSet) :
            karma::CacheBase(pSet),
            maxDeltaInvariantMass_(pSet_.getParameter<double>("maxDeltaInvariantMass")) {

        };

        double maxDeltaInvariantMass_;

    };

    // -- main producer
    template<typename TLeptonCollection>
    class ZBosonsProducer : public edm::stream::EDProducer<
        edm::GlobalCache<karma::ZBosonsProducerGlobalCache>
    > {

      public:
        explicit ZBosonsProducer(const edm::ParameterSet& config, const karma::ZBosonsProducerGlobalCache* globalCache):
            m_configPSet(config) {

            // -- register products
            produces<karma::LVCollection>();
            produces<karma::LVCollection>("positiveLeptons");
            produces<karma::LVCollection>("negativeLeptons");

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
        virtual ~ZBosonsProducer() {};

        // -- global cache extension
        static std::unique_ptr<karma::ZBosonsProducerGlobalCache> initializeGlobalCache(const edm::ParameterSet& pSet) {
            // -- create the GlobalCache
            return std::unique_ptr<karma::ZBosonsProducerGlobalCache>(new karma::ZBosonsProducerGlobalCache(pSet));
        };
        static void globalEndJob(const karma::ZBosonsProducerGlobalCache*) {/* noop */};

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
            std::unique_ptr<karma::LVCollection> zBosonLVs(new karma::LVCollection());
            std::unique_ptr<karma::LVCollection> positiveLeptonLVs(new karma::LVCollection());
            std::unique_ptr<karma::LVCollection> negativeLeptonLVs(new karma::LVCollection());

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

            /// if (matchingIndexPairs.size() != 0) {
            ///     assert(matchingIndexPairs.size() == 1);  // should always have at most one matched lepton pair
            ///     positiveLeptonLV->p4 = positiveLeptons.at(matchingIndexPairs.at(0).first).p4;
            ///     negativeLeptonLV->p4 = negativeLeptons.at(matchingIndexPairs.at(0).second).p4;
            ///     zBosonLV->p4 = positiveLeptonLV->p4 + negativeLeptonLV->p4;
            /// }

            for (const auto& matchingIndexPair : matchingIndexPairs) {
              positiveLeptonLVs->emplace_back();
              positiveLeptonLVs->back().p4 = positiveLeptons.at(matchingIndexPair.first).p4;

              negativeLeptonLVs->emplace_back();
              negativeLeptonLVs->back().p4 = negativeLeptons.at(matchingIndexPair.second).p4;

              zBosonLVs->emplace_back();
              zBosonLVs->back().p4 = positiveLeptonLVs->back().p4 + negativeLeptonLVs->back().p4;
            }

            event.put(std::move(zBosonLVs));
            event.put(std::move(positiveLeptonLVs), "positiveLeptons");
            event.put(std::move(negativeLeptonLVs), "negativeLeptons");
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
