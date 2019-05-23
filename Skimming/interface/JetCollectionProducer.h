#pragma once

#include "CollectionProducer.h"

#include "FWCore/Framework/interface/MakerMacros.h"


// -- output data formats
#include "Karma/SkimmingFormats/interface/Event.h"

// -- input data formats
#include "DataFormats/PatCandidates/interface/Jet.h"


namespace karma {

    class JetCollectionProducer : public karma::CollectionProducerBase<edm::View<pat::Jet>, karma::JetCollection> {

      public:
        explicit JetCollectionProducer(const edm::ParameterSet& config) :
            karma::CollectionProducerBase<edm::View<pat::Jet>, karma::JetCollection>(config) {

            // -- declare which collections are consumed and create tokens
            const auto& transientInfoSpec =
                this->m_configPSet.getParameter<edm::ParameterSet>("transientInformationSpec");

            const auto& fromUserIntSpec = transientInfoSpec.getParameter<edm::ParameterSet>("fromUserInt");
            for(const auto& transientKeyName : fromUserIntSpec.getParameterNames()) {
                m_transientIntKeyForUserInt[fromUserIntSpec.getParameter<std::string>(transientKeyName)] = transientKeyName;
            };
            const auto& fromUserIntAsBoolSpec = transientInfoSpec.getParameter<edm::ParameterSet>("fromUserIntAsBool");
            for(const auto& transientKeyName : fromUserIntAsBoolSpec.getParameterNames()) {
                m_transientBoolKeyForUserInt[fromUserIntAsBoolSpec.getParameter<std::string>(transientKeyName)] = transientKeyName;
            };
            const auto& fromUserFloatSpec = transientInfoSpec.getParameter<edm::ParameterSet>("fromUserFloat");
            for(const auto& transientKeyName : fromUserFloatSpec.getParameterNames()) {
                m_transientDoubleKeyForUserFloat[fromUserFloatSpec.getParameter<std::string>(transientKeyName)] = transientKeyName;
            };

        };
        ~JetCollectionProducer() {};

        virtual void produceSingle(const pat::Jet&, karma::Jet&, const edm::Event&, const edm::EventSetup&);

      private:
        std::map<std::string,std::string> m_transientBoolKeyForUserInt;
        std::map<std::string,std::string> m_transientIntKeyForUserInt;
        std::map<std::string,std::string> m_transientDoubleKeyForUserFloat;

    };

}  // end namespace
