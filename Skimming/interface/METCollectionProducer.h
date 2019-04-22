#pragma once

#include "CollectionProducer.h"

#include "FWCore/Framework/interface/MakerMacros.h"


// -- output data formats
#include "Karma/SkimmingFormats/interface/Event.h"

// -- input data formats
#include "DataFormats/PatCandidates/interface/MET.h"


namespace karma {

    class METCollectionProducer : public karma::CollectionProducerBase<edm::View<pat::MET>, karma::METCollection> {

      public:
        explicit METCollectionProducer(const edm::ParameterSet& config) :
            karma::CollectionProducerBase<edm::View<pat::MET>, karma::METCollection>(config) {};
        ~METCollectionProducer() {};

        virtual void produceSingle(const pat::MET&, karma::MET&, const edm::Event&, const edm::EventSetup&);

    };

}  // end namespace
