#pragma once

// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/stream/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/Framework/interface/makeRefToBaseProdFrom.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/Utilities/interface/StreamID.h"

#include "Karma/Common/interface/EDMTools/Util.h"

// -- output data formats
#include "DataFormats/Common/interface/Ref.h"
#include "DataFormats/Common/interface/AssociationMap.h"

//
// class declaration
//
namespace karma {

    // -- generic producer template

    template<typename TPrimaryCollection,
             typename TSecondaryCollection,
             typename Matcher,
             typename AssociationType = edm::OneToOne<TPrimaryCollection, TSecondaryCollection>,
             typename TProduct = edm::AssociationMap<AssociationType>>
    class GenericMatchingProducer : public edm::stream::EDProducer<> {

      public:
        template<typename... MatcherParameters>
        explicit GenericMatchingProducer(const edm::ParameterSet& config, MatcherParameters... matcherParams) :
            m_configPSet(config),
            m_matcher(new Matcher(matcherParams...)) {

            // -- register products
            produces<TProduct>();

            // -- process configuration

            // -- declare which collections are consumed and create tokens
            primaryCollectionToken = consumes<TPrimaryCollection>(m_configPSet.getParameter<edm::InputTag>("primaryCollectionSrc"));
            secondaryCollectionToken = consumes<TSecondaryCollection>(m_configPSet.getParameter<edm::InputTag>("secondaryCollectionSrc"));
        };
        virtual ~GenericMatchingProducer() {};

        // -- pSet descriptions for CMSSW help info
        static void fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
            // The following says we do not know what parameters are allowed so do no validation
            // Please change this to state exactly what you do use, even if it is no parameters
            edm::ParameterSetDescription desc;
            desc.setUnknown();
            descriptions.addDefault(desc);
        }

        // -- "regular" per-Event 'produce' method
        virtual void produce(edm::Event& event, const edm::EventSetup& setup) {

            // -- retrieve collections

            karma::util::getByTokenOrThrow(event, this->primaryCollectionToken, this->primaryCollectionHandle);
            karma::util::getByTokenOrThrow(event, this->secondaryCollectionToken, this->secondaryCollectionHandle);

            // create new TProduct (note: needs to provide constructor from RefProds)
            std::unique_ptr<TProduct> product(new TProduct(
                edm::RefProd<TPrimaryCollection>(this->primaryCollectionHandle),
                edm::RefProd<TSecondaryCollection>(this->secondaryCollectionHandle)
            ));

            // let the external matcher perform the matching
            const std::vector<std::pair<int, int>> matchResults(
                m_matcher->match(*this->primaryCollectionHandle, *this->secondaryCollectionHandle));

            // commit the match results to the product
            for (const auto& matchedIndexPair : matchResults) {
                product->insert(
                    edm::Ref<TPrimaryCollection>(this->primaryCollectionHandle, matchedIndexPair.first),
                    edm::Ref<TSecondaryCollection>(this->secondaryCollectionHandle, matchedIndexPair.second)
                );
            }

            // move outputs to event tree
            event.put(std::move(product));
        };


      private:

        // ----------member data ---------------------------

        const edm::ParameterSet& m_configPSet;

        std::unique_ptr<Matcher> m_matcher;

        // -- handles and tokens

        typename edm::Handle<TPrimaryCollection> primaryCollectionHandle;
        edm::EDGetTokenT<TPrimaryCollection> primaryCollectionToken;

        typename edm::Handle<TSecondaryCollection> secondaryCollectionHandle;
        edm::EDGetTokenT<TSecondaryCollection> secondaryCollectionToken;

    };
}  // end namespace
