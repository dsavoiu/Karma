#pragma once

#include <iostream>
#include "CollectionProducer.h"
 
#include "FWCore/Framework/interface/MakerMacros.h"


// -- output data formats
#include "DijetAnalysis/DataFormats/interface/Event.h"

// -- input data formats
#include "DataFormats/PatCandidates/interface/TriggerObjectStandAlone.h"


namespace dijet {

    class TriggerObjectCollectionProducer : public dijet::CollectionProducerBase<pat::TriggerObjectStandAloneCollection, dijet::TriggerObjectCollection> {

      public:
        explicit TriggerObjectCollectionProducer(const edm::ParameterSet& config) : 
            dijet::CollectionProducerBase<pat::TriggerObjectStandAloneCollection, dijet::TriggerObjectCollection>(config) {};
        ~TriggerObjectCollectionProducer() {};

        virtual void produceSingle(const pat::TriggerObjectStandAlone&, dijet::TriggerObject&);
        
        inline virtual bool acceptSingle(const pat::TriggerObjectStandAlone& in) {
            for (const auto& objType : in.triggerObjectTypes()) {
                for (const auto& allowedObjType : m_configPSet.getParameter<std::vector<int>>("allowedTriggerObjectTypes")) {
                    if (objType == allowedObjType) {
                        return true;  // accept objects with allowed types
                    }
                }
            }
            return false;  // reject all the rest
        };

    };

}  // end namespace
