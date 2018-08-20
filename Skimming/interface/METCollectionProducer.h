#pragma once

#include "CollectionProducer.h"

#include "FWCore/Framework/interface/MakerMacros.h"


// -- output data formats
#include "DijetAnalysis/DataFormats/interface/Event.h"

// -- input data formats
#include "DataFormats/PatCandidates/interface/MET.h"


namespace dijet {

    class METCollectionProducer : public dijet::CollectionProducerBase<edm::View<pat::MET>, dijet::METCollection> {

      public:
        explicit METCollectionProducer(const edm::ParameterSet& config) :
            dijet::CollectionProducerBase<edm::View<pat::MET>, dijet::METCollection>(config) {};
        ~METCollectionProducer() {};

        virtual void produceSingle(const pat::MET&, dijet::MET&, const edm::Event&, const edm::EventSetup&);

    };

}  // end namespace
