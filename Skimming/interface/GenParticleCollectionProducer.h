#pragma once

#include "CollectionProducer.h"

#include "FWCore/Framework/interface/MakerMacros.h"


// -- output data formats
#include "Karma/SkimmingFormats/interface/Event.h"

// -- input data formats
#include <DataFormats/HepMCCandidate/interface/GenParticle.h>


namespace karma {

    class GenParticleCollectionProducer : public karma::CollectionProducerBase<edm::View<reco::GenParticle>, karma::GenParticleCollection> {

      public:
        explicit GenParticleCollectionProducer(const edm::ParameterSet& config) :
            karma::CollectionProducerBase<edm::View<reco::GenParticle>, karma::GenParticleCollection>(config) {
                const auto& paramAllowedPDGIds = config.getParameter<std::vector<int>>("allowedPDGIds");
                allowedPDGIds_ = std::set<int>(paramAllowedPDGIds.begin(), paramAllowedPDGIds.end());
        };
        ~GenParticleCollectionProducer() {};

        virtual void produceSingle(const reco::GenParticle&, karma::GenParticle&, const edm::Event&, const edm::EventSetup&);

        inline virtual bool acceptSingle(const reco::GenParticle&, const edm::Event&, const edm::EventSetup&) override;

    protected:
        std::set<int> allowedPDGIds_;

    };

}  // end namespace
