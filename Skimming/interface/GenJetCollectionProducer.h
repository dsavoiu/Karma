#pragma once

#include "CollectionProducer.h"

#include "FWCore/Framework/interface/MakerMacros.h"


// -- output data formats
#include "Karma/SkimmingFormats/interface/Event.h"

// -- input data formats
#include "DataFormats/JetReco/interface/GenJet.h"


namespace dijet {

    class GenJetCollectionProducer : public dijet::CollectionProducerBase<edm::View<reco::GenJet>, dijet::LVCollection> {

      public:
        explicit GenJetCollectionProducer(const edm::ParameterSet& config) :
            dijet::CollectionProducerBase<edm::View<reco::GenJet>, dijet::LVCollection>(config) {};
        ~GenJetCollectionProducer() {};

        virtual void produceSingle(const reco::GenJet&, dijet::LV&, const edm::Event&, const edm::EventSetup&);

    };

}  // end namespace
