#pragma once

#include "CollectionProducer.h"

#include "FWCore/Framework/interface/MakerMacros.h"


// -- output data formats
#include "Karma/SkimmingFormats/interface/Event.h"

// -- input data formats
#include "DataFormats/PatCandidates/interface/Jet.h"


namespace dijet {

    class JetCollectionProducer : public dijet::CollectionProducerBase<edm::View<pat::Jet>, dijet::JetCollection> {

      public:
        explicit JetCollectionProducer(const edm::ParameterSet& config) :
            dijet::CollectionProducerBase<edm::View<pat::Jet>, dijet::JetCollection>(config) {};
        ~JetCollectionProducer() {};

        virtual void produceSingle(const pat::Jet&, dijet::Jet&, const edm::Event&, const edm::EventSetup&);

    };

}  // end namespace
