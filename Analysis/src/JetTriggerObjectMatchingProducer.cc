// system include files
#include <iostream>

#include "DijetAnalysis/Analysis/interface/JetTriggerObjectMatchingProducer.h"

// -- constructor
dijet::JetTriggerObjectMatchingProducer::JetTriggerObjectMatchingProducer(const edm::ParameterSet& config) : m_configPSet(config) {
    // -- register products
    produces<dijet::JetTriggerObjectsMap>();

    // -- process configuration

    // -- declare which collections are consumed and create tokens
    dijetEventToken = consumes<dijet::Event>(m_configPSet.getParameter<edm::InputTag>("dijetEventSrc"));
    dijetJetCollectionToken = consumes<dijet::JetCollection>(m_configPSet.getParameter<edm::InputTag>("dijetJetCollectionSrc"));
    dijetTriggerObjectCollectionToken = consumes<dijet::TriggerObjectCollection>(m_configPSet.getParameter<edm::InputTag>("dijetTriggerObjectCollectionSrc"));

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
    obtained &= event.getByToken(this->dijetEventToken, this->dijetEventHandle);
    // jet collection
    obtained &= event.getByToken(this->dijetJetCollectionToken, this->dijetJetCollectionHandle);
    // jet collection
    obtained &= event.getByToken(this->dijetTriggerObjectCollectionToken, this->dijetTriggerObjectCollectionHandle);

    assert(obtained);  // raise if one collection could not be obtained

    // create new AssociationMap (note: need to specify RefProds explicitly here!)
    std::unique_ptr<dijet::JetTriggerObjectsMap> jetTriggerObjectsMap(new dijet::JetTriggerObjectsMap(
        edm::RefProd<dijet::JetCollection>(this->dijetJetCollectionHandle),
        edm::RefProd<dijet::TriggerObjectCollection>(this->dijetTriggerObjectCollectionHandle)
    ));

    // -- do jet-to-trigger-object matching
    for (size_t iTO = 0; iTO < this->dijetTriggerObjectCollectionHandle->size(); ++iTO) {
        const auto& triggerObject = this->dijetTriggerObjectCollectionHandle->at(iTO);

        // match jets to objects
        for (size_t iJet = 0; iJet < this->dijetJetCollectionHandle->size(); ++iJet) {
            const auto& jet = this->dijetJetCollectionHandle->at(iJet);
            double deltaR = ROOT::Math::VectorUtil::DeltaR(triggerObject.p4, jet.p4);

            // match *every* object within configured max DeltaR
            if (deltaR <= maxDeltaR_) {
                jetTriggerObjectsMap->insert(
                    edm::Ref<dijet::JetCollection>(this->dijetJetCollectionHandle, iJet),
                    edm::Ref<dijet::TriggerObjectCollection>(this->dijetTriggerObjectCollectionHandle, iTO)
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
