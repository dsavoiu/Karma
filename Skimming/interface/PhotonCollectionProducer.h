#pragma once

#include "CollectionProducer.h"

#include "FWCore/Framework/interface/MakerMacros.h"


// -- output data formats
#include "Karma/SkimmingFormats/interface/Event.h"

// -- input data formats
#include "DataFormats/PatCandidates/interface/Photon.h"


namespace karma {

    class PhotonCollectionProducer : public karma::CollectionProducerBase<edm::View<pat::Photon>, karma::PhotonCollection> {

      public:
        explicit PhotonCollectionProducer(const edm::ParameterSet& config) :
            karma::CollectionProducerBase<edm::View<pat::Photon>, karma::PhotonCollection>(config) {
        };
        ~PhotonCollectionProducer() {};

        virtual void produceSingle(const pat::Photon&, karma::Photon&, const edm::Event&, const edm::EventSetup&);

      private:

    };

}  // end namespace
