#pragma once

#include <stdexcept>

#include "CollectionProducer.h"

#include "FWCore/Utilities/interface/EDMException.h"
#include "FWCore/Framework/interface/MakerMacros.h"


// -- output data formats
#include "Karma/SkimmingFormats/interface/Event.h"

// -- input data formats
#include <DataFormats/PatCandidates/interface/Electron.h>


namespace karma {

    class ElectronCollectionProducer : public karma::CollectionProducerBase<edm::View<pat::Electron>, karma::ElectronCollection> {

      public:
        explicit ElectronCollectionProducer(const edm::ParameterSet& config) :
            karma::CollectionProducerBase<edm::View<pat::Electron>, karma::ElectronCollection>(config) {

            // -- set up electron Ids
            const auto& electronIdSpecs = this->m_configPSet.template getParameter<edm::VParameterSet>("electronIds");
            for (const auto& electronIdSpec : electronIdSpecs) {
                m_electronIdSpecs[electronIdSpec.getParameter<std::string>("name")] =
                    electronIdSpec.getParameter<std::vector<std::string>>("workingPoints");
            }
        };
        ~ElectronCollectionProducer() {};

        //virtual void produce(edm::Event& event, const edm::EventSetup& setup) override;
        virtual void produceSingle(const pat::Electron&, karma::Electron&, const edm::Event&, const edm::EventSetup&);

        inline virtual bool acceptSingle(const pat::Electron&, const edm::Event&, const edm::EventSetup&) override;

    protected:
        // store electron Id specification
        std::map<std::string, std::vector<std::string>> m_electronIdSpecs;

    };

}  // end namespace
