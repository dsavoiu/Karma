#pragma once

#include "CollectionProducer.h"

#include "FWCore/Framework/interface/MakerMacros.h"


// -- output data formats
#include "Karma/SkimmingFormats/interface/Event.h"

// -- input data formats
#include "DataFormats/JetReco/interface/GenJet.h"


namespace karma {

    class GenJetCollectionProducer : public karma::CollectionProducerBase<edm::View<reco::GenJet>, karma::LVCollection> {

      public:
        explicit GenJetCollectionProducer(const edm::ParameterSet& config) :
            karma::CollectionProducerBase<edm::View<reco::GenJet>, karma::LVCollection>(config) {};
        ~GenJetCollectionProducer() {};

        virtual void produceSingle(const reco::GenJet&, karma::LV&, const edm::Event&, const edm::EventSetup&);

    };

}  // end namespace
