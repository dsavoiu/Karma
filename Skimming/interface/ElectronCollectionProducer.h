#pragma once

#include "CollectionProducer.h"

#include "FWCore/Framework/interface/MakerMacros.h"


// -- output data formats
#include "Karma/SkimmingFormats/interface/Event.h"

// -- input data formats
#include <DataFormats/PatCandidates/interface/Electron.h>


namespace karma {

    class ElectronCollectionProducer : public karma::CollectionProducerBase<edm::View<pat::Electron>, karma::ElectronCollection> {

      public:
        explicit ElectronCollectionProducer(const edm::ParameterSet& config) :
            karma::CollectionProducerBase<edm::View<pat::Electron>, karma::ElectronCollection>(config) {};
        ~ElectronCollectionProducer() {};

        virtual void produceSingle(const pat::Electron&, karma::Electron&, const edm::Event&, const edm::EventSetup&);

        inline virtual bool acceptSingle(const pat::Electron&, const edm::Event&, const edm::EventSetup&) override;

    protected:

    };

}  // end namespace
