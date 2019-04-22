#pragma once

#include "CollectionProducer.h"

#include "FWCore/Framework/interface/MakerMacros.h"

// -- output data formats
#include "Karma/SkimmingFormats/interface/Event.h"

// -- input data formats
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"

namespace karma {

    class VertexCollectionProducer :
        public karma::CollectionProducerBase<
            /* TInputType =*/ reco::VertexCollection,
            /* TOutputType =*/ karma::VertexCollection> {

      public:
        explicit VertexCollectionProducer(const edm::ParameterSet& config) :
            karma::CollectionProducerBase<reco::VertexCollection, karma::VertexCollection>(config) {

        };
        ~VertexCollectionProducer() {};


        /// // need to override produce function to update karmaRun handle
        /// virtual void produce(edm::Event& event, const edm::EventSetup& setup) {
        ///     // call "parent" produce function
        ///     karma::CollectionProducerBase<reco::VertexCollection, karma::VertexCollection>::produce(event, setup);
        /// };

        virtual void produceSingle(const reco::Vertex&, karma::Vertex&, const edm::Event&, const edm::EventSetup&);

        inline virtual bool acceptSingle(const reco::Vertex& in, const edm::Event& event, const edm::EventSetup& setup) override {
            return true;  // accept all
        };
    };

}  // end namespace
