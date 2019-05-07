#pragma once

#include "CollectionProducer.h"

#include "FWCore/Framework/interface/MakerMacros.h"


// -- output data formats
#include "Karma/SkimmingFormats/interface/Event.h"

// -- input data formats
#include <DataFormats/PatCandidates/interface/Muon.h>


namespace karma {

    class MuonCollectionProducer : public karma::CollectionProducerBase<edm::View<pat::Muon>, karma::MuonCollection> {

      public:
        explicit MuonCollectionProducer(const edm::ParameterSet& config) :
            karma::CollectionProducerBase<edm::View<pat::Muon>, karma::MuonCollection>(config) {};
        ~MuonCollectionProducer() {};

        virtual void produceSingle(const pat::Muon&, karma::Muon&, const edm::Event&, const edm::EventSetup&);

        inline virtual bool acceptSingle(const pat::Muon&, const edm::Event&, const edm::EventSetup&) override;

    protected:

    };

}  // end namespace
