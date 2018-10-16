// system include files
#include <iostream>

#include "DijetAnalysis/Analysis/interface/NtupleProducer.h"


// -- constructor
dijet::NtupleProducer::NtupleProducer(const edm::ParameterSet& config, const dijet::NtupleProducerGlobalCache* globalCache) : m_configPSet(config) {
    // -- register products
    produces<dijet::NtupleEntry>();

    // -- process configuration
    m_triggerEfficienciesProvider = std::unique_ptr<TriggerEfficienciesProvider>(
        new TriggerEfficienciesProvider(m_configPSet.getParameter<std::string>("triggerEfficienciesFile"))
    );

    std::cout << "Read trigger efficiencies for paths:" << std::endl;
    for (const auto& mapIter : m_triggerEfficienciesProvider->triggerEfficiencies()) {
        std::cout << "    " << mapIter.first << " -> " << &(*mapIter.second) << std::endl;
    }

    // set a flag if we are running on (real) data
    m_isData = m_configPSet.getParameter<bool>("isData");

    // -- declare which collections are consumed and create tokens
    dijetEventToken = consumes<dijet::Event>(m_configPSet.getParameter<edm::InputTag>("dijetEventSrc"));
    dijetRunToken = consumes<dijet::Run, edm::InRun>(m_configPSet.getParameter<edm::InputTag>("dijetRunSrc"));
    dijetJetCollectionToken = consumes<dijet::JetCollection>(m_configPSet.getParameter<edm::InputTag>("dijetJetCollectionSrc"));
    dijetMETCollectionToken = consumes<dijet::METCollection>(m_configPSet.getParameter<edm::InputTag>("dijetMETCollectionSrc"));
    dijetJetTriggerObjectsMapToken = consumes<dijet::JetTriggerObjectsMap>(m_configPSet.getParameter<edm::InputTag>("dijetJetTriggerObjectMapSrc"));

}


// -- destructor
dijet::NtupleProducer::~NtupleProducer() {
}

// -- static member functions

/*static*/ std::unique_ptr<dijet::NtupleProducerGlobalCache> dijet::NtupleProducer::initializeGlobalCache(const edm::ParameterSet& pSet) {
    // -- create the GlobalCache
    return std::unique_ptr<dijet::NtupleProducerGlobalCache>(new dijet::NtupleProducerGlobalCache(pSet));
}


/*static*/ std::shared_ptr<dijet::NtupleProducerRunCache> dijet::NtupleProducer::globalBeginRun(const edm::Run& run, const edm::EventSetup& setup, const dijet::NtupleProducer::GlobalCache* globalCache) {
    // -- create the RunCache
    auto runCache = std::make_shared<dijet::NtupleProducerRunCache>(globalCache->pSet_);

    typename edm::Handle<dijet::Run> runHandle;
    run.getByLabel(globalCache->pSet_.getParameter<edm::InputTag>("dijetRunSrc"), runHandle);

    // compute the unversioned HLT path names
    // (needed later to get the trigger efficiencies)
    boost::smatch matched_substrings;
    runCache->triggerPathsUnversionedNames_.resize(runHandle->triggerPathInfos.size());
    for (size_t iPath = 0; iPath < runHandle->triggerPathInfos.size(); ++iPath) {
        const std::string& pathName = runHandle->triggerPathInfos[iPath].name_;
        if (boost::regex_match(pathName, matched_substrings, globalCache->hltVersionPattern_) && matched_substrings.size() > 1) {
            // need matched_substrings[1] because matched_substrings[0] is always the entire string
            runCache->triggerPathsUnversionedNames_[iPath] = matched_substrings[1];
        }
    }

    return runCache;
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
    // MET collection
    obtained &= event.getByToken(this->dijetMETCollectionToken, this->dijetMETCollectionHandle);
    // jet trigger objects map
    obtained &= event.getByToken(this->dijetJetTriggerObjectsMapToken, this->dijetJetTriggerObjectsMapHandle);

    assert(obtained);  // raise if one collection could not be obtained
    assert(this->dijetMETCollectionHandle->size() == 1);  // only allow MET collections containing a single MET object

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
        // write out jetID (1 if pass, 0 if fail, -1 if not requested/not available)
        if (globalCache()->jetIDProvider_)
            outputNtupleEntry->jet1id = (globalCache()->jetIDProvider_->getJetID(*jet1));

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

        // retrieve the efficiency
        if (outputNtupleEntry->jet1HLTAssignedPathIndex >= 0) {
            const std::string unversionedPathName = runCache()->triggerPathsUnversionedNames_[
                outputNtupleEntry->jet1HLTAssignedPathIndex
            ];

            const TEfficiency* jet1HLTAssignedPathEfficiencyHisto = m_triggerEfficienciesProvider->getEfficiency(unversionedPathName);
            if (jet1HLTAssignedPathEfficiencyHisto) {
                int iBin = jet1HLTAssignedPathEfficiencyHisto->FindFixBin(outputNtupleEntry->jet1pt);
                outputNtupleEntry->jet1HLTAssignedPathEfficiency = jet1HLTAssignedPathEfficiencyHisto->GetEfficiency(iBin);
            }
        }

        outputNtupleEntry->jet1HLTpt = jet1HLTAssignment.assignedObjectPt;

        // second-leading jet kinematics
        if (jets->size() > 1) {
            const dijet::Jet* jet2 = &jets->at(1);
            // write out jetID (1 if pass, 0 if fail, -1 if not requested/not available)
            if (globalCache()->jetIDProvider_)
                outputNtupleEntry->jet2id = (globalCache()->jetIDProvider_->getJetID(*jet2));

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

    outputNtupleEntry->met = this->dijetMETCollectionHandle->at(0).p4.Pt();
    outputNtupleEntry->sumEt = this->dijetMETCollectionHandle->at(0).sumEt;

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
