// system include files
#include <iostream>

#include "Karma/DijetAnalysis/interface/JetTriggerObjectMatchingProducer.h"

// -- constructor
dijet::JetTriggerObjectMatchingProducer::JetTriggerObjectMatchingProducer(const edm::ParameterSet& config) : m_configPSet(config) {
    // -- register products
    produces<karma::JetTriggerObjectsMap>();

    // -- process configuration

    // -- declare which collections are consumed and create tokens
    karmaEventToken = consumes<karma::Event>(m_configPSet.getParameter<edm::InputTag>("karmaEventSrc"));
    karmaJetCollectionToken = consumes<karma::JetCollection>(m_configPSet.getParameter<edm::InputTag>("karmaJetCollectionSrc"));
    karmaTriggerObjectCollectionToken = consumes<karma::TriggerObjectCollection>(m_configPSet.getParameter<edm::InputTag>("karmaTriggerObjectCollectionSrc"));

    maxDeltaR_ = m_configPSet.getParameter<double>("maxDeltaR");

}


// -- destructor
dijet::JetTriggerObjectMatchingProducer::~JetTriggerObjectMatchingProducer() {
}


// -- member functions

void dijet::JetTriggerObjectMatchingProducer::produce(edm::Event& event, const edm::EventSetup& setup) {

    // -- get object collections for event
    bool obtained = true;
    // pileup density
    obtained &= event.getByToken(this->karmaEventToken, this->karmaEventHandle);
    // jet collection
    obtained &= event.getByToken(this->karmaJetCollectionToken, this->karmaJetCollectionHandle);
    // trigger object collection
    obtained &= event.getByToken(this->karmaTriggerObjectCollectionToken, this->karmaTriggerObjectCollectionHandle);

    assert(obtained);  // raise if one collection could not be obtained

    // create new AssociationMap (note: need to specify RefProds explicitly here!)
    std::unique_ptr<karma::JetTriggerObjectsMap> jetTriggerObjectsMap(new karma::JetTriggerObjectsMap(
        edm::RefProd<karma::JetCollection>(this->karmaJetCollectionHandle),
        edm::RefProd<karma::TriggerObjectCollection>(this->karmaTriggerObjectCollectionHandle)
    ));

    // -- do jet-to-trigger-object matching
    for (size_t iTO = 0; iTO < this->karmaTriggerObjectCollectionHandle->size(); ++iTO) {
        const auto& triggerObject = this->karmaTriggerObjectCollectionHandle->at(iTO);

        // match jets to objects
        for (size_t iJet = 0; iJet < this->karmaJetCollectionHandle->size(); ++iJet) {
            const auto& jet = this->karmaJetCollectionHandle->at(iJet);
            double deltaR = ROOT::Math::VectorUtil::DeltaR(triggerObject.p4, jet.p4);

            // match *every* object within configured max DeltaR
            if (deltaR <= maxDeltaR_) {
                jetTriggerObjectsMap->insert(
                    edm::Ref<karma::JetCollection>(this->karmaJetCollectionHandle, iJet),
                    edm::Ref<karma::TriggerObjectCollection>(this->karmaTriggerObjectCollectionHandle, iTO)
                );
            }
        }
    }

    // move outputs to event tree
    event.put(std::move(jetTriggerObjectsMap));
}


void dijet::JetTriggerObjectMatchingProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    // The following says we do not know what parameters are allowed so do no validation
    // Please change this to state exactly what you do use, even if it is no parameters
    edm::ParameterSetDescription desc;
    desc.setUnknown();
    descriptions.addDefault(desc);
}


//define this as a plug-in
using dijet::JetTriggerObjectMatchingProducer;
DEFINE_FWK_MODULE(JetTriggerObjectMatchingProducer);
