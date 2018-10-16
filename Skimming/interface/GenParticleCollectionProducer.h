#pragma once

#include "CollectionProducer.h"

#include "FWCore/Framework/interface/MakerMacros.h"


// -- output data formats
#include "DijetAnalysis/DataFormats/interface/Event.h"

// -- input data formats
#include <DataFormats/HepMCCandidate/interface/GenParticle.h>


namespace dijet {

    class GenParticleCollectionProducer : public dijet::CollectionProducerBase<edm::View<reco::GenParticle>, dijet::GenParticleCollection> {

      public:
        explicit GenParticleCollectionProducer(const edm::ParameterSet& config) :
            dijet::CollectionProducerBase<edm::View<reco::GenParticle>, dijet::GenParticleCollection>(config) {
                const auto& paramAllowedPDGIds = config.getParameter<std::vector<int>>("allowedPDGIds");
                allowedPDGIds_ = std::set<int>(paramAllowedPDGIds.begin(), paramAllowedPDGIds.end());
        };
        ~GenParticleCollectionProducer() {};

        virtual void produceSingle(const reco::GenParticle&, dijet::GenParticle&, const edm::Event&, const edm::EventSetup&);

        inline virtual bool acceptSingle(const reco::GenParticle&, const edm::Event&, const edm::EventSetup&) override;

    protected:
        std::set<int> allowedPDGIds_;

    };

}  // end namespace
