// system include files
#include <iostream>

#include "DijetAnalysis/Analysis/interface/NtupleProducer.h"

// -- constructor
dijet::NtupleProducer::NtupleProducer(const edm::ParameterSet& config) : m_configPSet(config) {
    // -- register products
    produces<dijet::NtupleEntry>();

    // -- process configuration

    // -- declare which collections are consumed and create tokens
    dijetEventToken = consumes<dijet::Event>(m_configPSet.getParameter<edm::InputTag>("dijetEventSrc"));
    dijetRunToken = consumes<dijet::Run, edm::InRun>(m_configPSet.getParameter<edm::InputTag>("dijetRunSrc"));
    dijetJetCollectionToken = consumes<dijet::JetCollection>(m_configPSet.getParameter<edm::InputTag>("dijetJetCollectionSrc"));
    dijetJetTriggerObjectsMapToken = consumes<dijet::JetTriggerObjectsMap>(m_configPSet.getParameter<edm::InputTag>("dijetJetTriggerObjectMapSrc"));

}


// -- destructor
dijet::NtupleProducer::~NtupleProducer() {
}


// -- member functions

void dijet::NtupleProducer::produce(edm::Event& event, const edm::EventSetup& setup) {
    std::unique_ptr<dijet::NtupleEntry> outputNtupleEntry(new dijet::NtupleEntry());

    // -- get object collections for event
    bool obtained = true;
    // run data
    obtained &= event.getRun().getByToken(this->dijetRunToken, this->dijetRunHandle);
    // pileup density
    obtained &= event.getByToken(this->dijetEventToken, this->dijetEventHandle);
    // jet collection
    obtained &= event.getByToken(this->dijetJetCollectionToken, this->dijetJetCollectionHandle);
    // jet collection
    obtained &= event.getByToken(this->dijetJetTriggerObjectsMapToken, this->dijetJetTriggerObjectsMapHandle);

    assert(obtained);  // raise if one collection could not be obtained

    // -- populate outputs

    // event metadata
    outputNtupleEntry->run = event.id().run();
    outputNtupleEntry->lumi = event.id().luminosityBlock();
    outputNtupleEntry->event = event.id().event();
    outputNtupleEntry->bx = event.bunchCrossing();

    // -- copy event content to ntuple
    outputNtupleEntry->rho     = this->dijetEventHandle->rho;
    outputNtupleEntry->npv     = this->dijetEventHandle->npv;
    outputNtupleEntry->npvGood = this->dijetEventHandle->npvGood;

    // trigger result
    outputNtupleEntry->hltNumBits = std::accumulate(this->dijetEventHandle->hltBits.begin(), this->dijetEventHandle->hltBits.end(), 0);

    // assign highest-threshold trigger path (assume ordered)
    if (outputNtupleEntry->hltNumBits) {
        // higher paths take precedence -> iterate in reverse order
        for (int iBit = this->dijetEventHandle->hltBits.size() - 1; iBit >= 0; --iBit) {
            if (this->dijetEventHandle->hltBits[iBit]) {
                outputNtupleEntry->hltAssignedBit = iBit;
                break;
            }
        }
    }

    const auto& jets = this->dijetJetCollectionHandle;  // convenience
    // leading jet kinematics
    if (jets->size() > 0) {
        const dijet::Jet* jet1 = &jets->at(0);

        outputNtupleEntry->jet1pt = jet1->p4.pt();
        outputNtupleEntry->jet1phi = jet1->p4.phi();
        outputNtupleEntry->jet1eta = jet1->p4.eta();
        outputNtupleEntry->jet1y = jet1->p4.Rapidity();

        // get assigned HLT path(s) for leading jet
        dijet::HLTAssignment jet1HLTAssignment = getHLTAssignment(0);
        outputNtupleEntry->jet1HLTNumMatchedTriggerObjects = jet1HLTAssignment.numUniqueMatchedTriggerObjects;
        outputNtupleEntry->jet1HLTAssignedPathIndex = jet1HLTAssignment.assignedPathIndex;
        if (outputNtupleEntry->jet1HLTAssignedPathIndex >= 0) {
            outputNtupleEntry->jet1HLTAssignedPathPrescale = this->dijetEventHandle->triggerPathHLTPrescales[
                outputNtupleEntry->jet1HLTAssignedPathIndex
            ];
        }
        outputNtupleEntry->jet1HLTpt = jet1HLTAssignment.assignedObjectPt;

        // second-leading jet kinematics
        if (jets->size() > 1) {
            const dijet::Jet* jet2 = &jets->at(1);

            outputNtupleEntry->jet2pt = jet2->p4.pt();
            outputNtupleEntry->jet2phi = jet2->p4.phi();
            outputNtupleEntry->jet2eta = jet2->p4.eta();
            outputNtupleEntry->jet2y = jet2->p4.Rapidity();

            // get assigned HLT path(s) for second-leading jet
            dijet::HLTAssignment jet2HLTAssignment = getHLTAssignment(1);
            outputNtupleEntry->jet2HLTNumMatchedTriggerObjects = jet2HLTAssignment.numUniqueMatchedTriggerObjects;
            outputNtupleEntry->jet2HLTAssignedPathIndex = jet2HLTAssignment.assignedPathIndex;
            if (outputNtupleEntry->jet2HLTAssignedPathIndex >= 0) {
                outputNtupleEntry->jet2HLTAssignedPathPrescale = this->dijetEventHandle->triggerPathHLTPrescales[
                    outputNtupleEntry->jet2HLTAssignedPathIndex
                ];
            }
            outputNtupleEntry->jet2HLTpt = jet2HLTAssignment.assignedObjectPt;

            // leading jet pair kinematics
            outputNtupleEntry->jet12mass = (jet1->p4 + jet2->p4).M();
            outputNtupleEntry->jet12ptave = 0.5 * (jet1->p4.pt() + jet2->p4.pt());
            outputNtupleEntry->jet12ystar = 0.5 * (jet1->p4.Rapidity() - jet2->p4.Rapidity());
            outputNtupleEntry->jet12yboost = 0.5 * (jet1->p4.Rapidity() + jet2->p4.Rapidity());
        }
    }

    // move outputs to event tree
    event.put(std::move(outputNtupleEntry));
}


void dijet::NtupleProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    // The following says we do not know what parameters are allowed so do no validation
    // Please change this to state exactly what you do use, even if it is no parameters
    edm::ParameterSetDescription desc;
    desc.setUnknown();
    descriptions.addDefault(desc);
}

/**
 * Helper function to determine which HLT path (if any) can be assigned
 * to a reconstructed jet with a particular index.
 */
dijet::HLTAssignment dijet::NtupleProducer::getHLTAssignment(unsigned int jetIndex) {

    dijet::HLTAssignment hltAssignment;

    // -- obtain the collection of trigger objects matched to jet with index `jetIndex`
    const auto& jetMatchedTriggerObjects = this->dijetJetTriggerObjectsMapHandle->find(
        edm::Ref<dijet::JetCollection>(this->dijetJetCollectionHandle, jetIndex)
    );

    // if there is at least one trigger object match for the leading jet
    if (jetMatchedTriggerObjects != this->dijetJetTriggerObjectsMapHandle->end()) {

        std::set<int> seenPathIndices;
        std::set<double> seenObjectPts;
        unsigned int numValidMatchedTriggerObjects = 0;
        unsigned int numUniqueMatchedTriggerObjects = 0;

        // loop over all trigger objects matched to the leading jet
        for (const auto& jetMatchedTriggerObject : jetMatchedTriggerObjects->val) {

            // ignore L1 objects
            if (!jetMatchedTriggerObject->isHLT()) continue;

            // ignore objects that aren't assigned to a trigger path
            if (!jetMatchedTriggerObject->assignedPathIndices.size()) continue;

            // accumulate all path indices encountered
            seenPathIndices.insert(
                jetMatchedTriggerObject->assignedPathIndices.begin(),
                jetMatchedTriggerObject->assignedPathIndices.end()
            );

            // use insertion function to count "pT-unique" trigger objects
            const auto insertStatus = seenObjectPts.insert(jetMatchedTriggerObject->p4.pt());
            if (insertStatus.second) ++numUniqueMatchedTriggerObjects;

            // keep track of number of matched trigger objects
            ++numValidMatchedTriggerObjects;
        }

        // -- populate return struct
        if (numValidMatchedTriggerObjects) {
            hltAssignment.numMatchedTriggerObjects = numValidMatchedTriggerObjects;
            hltAssignment.numUniqueMatchedTriggerObjects = numUniqueMatchedTriggerObjects;

            // assign highest-threshold trigger path (assume ordered)
            hltAssignment.assignedPathIndex = *std::max_element(
                seenPathIndices.begin(),
                seenPathIndices.end()
            );

            // assign highest pt
            hltAssignment.assignedObjectPt = *std::max_element(
                seenObjectPts.begin(),
                seenObjectPts.end()
            );
        }
    }

    // if no matches, the default struct is returned
    return hltAssignment;
}


//define this as a plug-in
using dijet::NtupleProducer;
DEFINE_FWK_MODULE(NtupleProducer);
