#pragma once

#include "CollectionProducer.h"

#include "FWCore/Framework/interface/MakerMacros.h"


// -- output data formats
#include "Karma/SkimmingFormats/interface/Event.h"

// -- input data formats
#include "DataFormats/PatCandidates/interface/Jet.h"


namespace karma {

    class JetCollectionProducer : public karma::CollectionProducerBase<edm::View<pat::Jet>, karma::JetCollection> {

      public:
        explicit JetCollectionProducer(const edm::ParameterSet& config) :
            karma::CollectionProducerBase<edm::View<pat::Jet>, karma::JetCollection>(config) {};
        ~JetCollectionProducer() {};

        virtual void produceSingle(const pat::Jet&, karma::Jet&, const edm::Event&, const edm::EventSetup&);

    };

}  // end namespace
