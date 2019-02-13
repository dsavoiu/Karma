#pragma once

#include "CollectionProducer.h"

#include "FWCore/Framework/interface/MakerMacros.h"

// -- output data formats
#include "DijetAnalysis/DataFormats/interface/Event.h"

// -- input data formats
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"

namespace dijet {

    class VertexCollectionProducer :
        public dijet::CollectionProducerBase<
            /* TInputType =*/ reco::VertexCollection,
            /* TOutputType =*/ dijet::VertexCollection> {

      public:
        explicit VertexCollectionProducer(const edm::ParameterSet& config) :
            dijet::CollectionProducerBase<reco::VertexCollection, dijet::VertexCollection>(config) {

        };
        ~VertexCollectionProducer() {};


        /// // need to override produce function to update dijetRun handle
        /// virtual void produce(edm::Event& event, const edm::EventSetup& setup) {
        ///     // call "parent" produce function
        ///     dijet::CollectionProducerBase<reco::VertexCollection, dijet::VertexCollection>::produce(event, setup);
        /// };

        virtual void produceSingle(const reco::Vertex&, dijet::Vertex&, const edm::Event&, const edm::EventSetup&);

        inline virtual bool acceptSingle(const reco::Vertex& in, const edm::Event& event, const edm::EventSetup& setup) override {
            return true;  // accept all
        };
    };

}  // end namespace
