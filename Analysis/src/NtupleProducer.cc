// system include files
#include <iostream>
#include <bitset>

#include "DijetAnalysis/Analysis/interface/NtupleProducer.h"


// -- constructor
dijet::NtupleProducer::NtupleProducer(const edm::ParameterSet& config, const dijet::NtupleProducerGlobalCache* globalCache) : m_configPSet(config) {
    // -- register products
    produces<dijet::NtupleEntry>();

    /// // -- process configuration
    /// m_triggerEfficienciesProvider = std::unique_ptr<TriggerEfficienciesProvider>(
    ///     new TriggerEfficienciesProvider(m_configPSet.getParameter<std::string>("triggerEfficienciesFile"))
    /// );

    /// std::cout << "Read trigger efficiencies for paths:" << std::endl;
    /// for (const auto& mapIter : m_triggerEfficienciesProvider->triggerEfficiencies()) {
    ///     std::cout << "    " << mapIter.first << " -> " << &(*mapIter.second) << std::endl;
    /// }

    // set a flag if we are running on (real) data
    m_isData = m_configPSet.getParameter<bool>("isData");
    m_weightForStitching = m_configPSet.getParameter<double>("weightForStitching");

    // -- declare which collections are consumed and create tokens
    dijetEventToken = consumes<dijet::Event>(m_configPSet.getParameter<edm::InputTag>("dijetEventSrc"));
    dijetRunToken = consumes<dijet::Run, edm::InRun>(m_configPSet.getParameter<edm::InputTag>("dijetRunSrc"));
    dijetVertexCollectionToken = consumes<dijet::VertexCollection>(m_configPSet.getParameter<edm::InputTag>("dijetVertexCollectionSrc"));
    dijetJetCollectionToken = consumes<dijet::JetCollection>(m_configPSet.getParameter<edm::InputTag>("dijetJetCollectionSrc"));
    dijetMETCollectionToken = consumes<dijet::METCollection>(m_configPSet.getParameter<edm::InputTag>("dijetMETCollectionSrc"));
    dijetJetTriggerObjectsMapToken = consumes<dijet::JetTriggerObjectsMap>(m_configPSet.getParameter<edm::InputTag>("dijetJetTriggerObjectMapSrc"));
    if (!m_isData) {
        dijetGeneratorQCDInfoToken = consumes<dijet::GeneratorQCDInfo>(m_configPSet.getParameter<edm::InputTag>("dijetGeneratorQCDInfoSrc"));
        dijetJetGenJetMapToken = consumes<dijet::JetGenJetMap>(m_configPSet.getParameter<edm::InputTag>("dijetJetGenJetMapSrc"));
        dijetGenParticleCollectionToken = consumes<dijet::GenParticleCollection>(m_configPSet.getParameter<edm::InputTag>("dijetGenParticleCollectionSrc"));
    }

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

    runCache->triggerPathsUnversionedNames_.resize(runHandle->triggerPathInfos.size());
    runCache->triggerPathsIndicesInConfig_.resize(runHandle->triggerPathInfos.size(), -1);
    for (size_t iPath = 0; iPath < runHandle->triggerPathInfos.size(); ++iPath) {
        const std::string& pathName = runHandle->triggerPathInfos[iPath].name_;
        ///std::cout << "[Check iPath " << iPath << "] " << pathName << std::endl;

        boost::smatch matched_substrings;
        if (boost::regex_match(pathName, matched_substrings, globalCache->hltVersionPattern_) && matched_substrings.size() > 1) {
            // need matched_substrings[1] because matched_substrings[0] is always the entire string
            runCache->triggerPathsUnversionedNames_[iPath] = matched_substrings[1];
            ///std::cout << " -> unversioned name: " << matched_substrings[1] << std::endl;
        }

        for (size_t iRequestedPath = 0; iRequestedPath < globalCache->hltPaths_.size(); ++iRequestedPath) {
            ///std::cout << "[Check iRequestedPath " << iRequestedPath << "] " << globalCache->hltPaths_[iRequestedPath] << std::endl;
            if (runCache->triggerPathsUnversionedNames_[iPath] == globalCache->hltPaths_[iRequestedPath]) {
                std::cout << " -> matched! " << iPath << " = " << iRequestedPath << std::endl;
                runCache->triggerPathsIndicesInConfig_[iPath] = iRequestedPath;
                break;
            }
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
    if (!m_isData) {
        // QCD generator information
        obtained &= event.getByToken(this->dijetGeneratorQCDInfoToken, this->dijetGeneratorQCDInfoHandle);
        // genParticle collection
        obtained &= event.getByToken(this->dijetGenParticleCollectionToken, this->dijetGenParticleCollectionHandle);
        // jet genJet map
        obtained &= event.getByToken(this->dijetJetGenJetMapToken, this->dijetJetGenJetMapHandle);
    }

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

    // write information related to primary vertices

    // TEMPORARY: make PV collection will be standard in newer skims
    // obtain primary vertex collection (if available)
    bool hasPVCollection = event.getByToken(this->dijetVertexCollectionToken, this->dijetVertexCollectionHandle);
    if (hasPVCollection) {
        // fill from PV collection
        outputNtupleEntry->npv     = this->dijetVertexCollectionHandle->size();
        outputNtupleEntry->npvGood = std::count_if(
            this->dijetVertexCollectionHandle->begin(),
            this->dijetVertexCollectionHandle->end(),
            [](const dijet::Vertex& vtx) {return vtx.isGoodOfflineVertex();}
        );
    }
    else {
        // fill from dijet::Event
        outputNtupleEntry->npv     = this->dijetEventHandle->npv;
        outputNtupleEntry->npvGood = this->dijetEventHandle->npvGood;
    }

    // weights
    outputNtupleEntry->weightForStitching = m_weightForStitching;  // TODO: less wasteful way?

    // -- trigger results

    std::bitset<8*sizeof(unsigned long)> bitsetHLTBits;
    // go through all triggers in skim
    for (size_t iBit = 0; iBit < this->dijetEventHandle->hltBits.size(); ++iBit) {
        // if trigger fired
        if (this->dijetEventHandle->hltBits[iBit]) {
            // get the index of trigger in analysis config
            const int idxInConfig = runCache()->triggerPathsIndicesInConfig_[iBit];
            // if trigger present in config
            if (idxInConfig >= 0) {
                // set bit
                bitsetHLTBits[idxInConfig] = true;
            }
        }
    }

    // encode bitsets as 'unsigned long'
    outputNtupleEntry->hltBits = bitsetHLTBits.to_ulong();

    // -- generator data (MC-only)
    if (!m_isData) {
        outputNtupleEntry->generatorWeight = this->dijetGeneratorQCDInfoHandle->weight;
        outputNtupleEntry->generatorWeightProduct = this->dijetGeneratorQCDInfoHandle->weightProduct;
        //if (this->dijetGeneratorQCDInfoHandle->binningValues.size() > 0)
        //    outputNtupleEntry->binningValue1 = this->dijetGeneratorQCDInfoHandle->binningValues[0];
        //if (this->dijetGeneratorQCDInfoHandle->binningValues.size() > 1)
        //    outputNtupleEntry->binningValue2 = this->dijetGeneratorQCDInfoHandle->binningValues[1];
        outputNtupleEntry->incomingParton1Flavor = this->dijetGeneratorQCDInfoHandle->parton1PdgId;
        outputNtupleEntry->incomingParton2Flavor = this->dijetGeneratorQCDInfoHandle->parton2PdgId;
        outputNtupleEntry->incomingParton1x = this->dijetGeneratorQCDInfoHandle->parton1x;
        outputNtupleEntry->incomingParton2x = this->dijetGeneratorQCDInfoHandle->parton2x;
        outputNtupleEntry->scalePDF = this->dijetGeneratorQCDInfoHandle->scalePDF;
        outputNtupleEntry->alphaQCD = this->dijetGeneratorQCDInfoHandle->alphaQCD;
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

        // PF energy fractions (jet 1)
        outputNtupleEntry->jet1NeutralHadronFraction = jet1->neutralHadronFraction;
        outputNtupleEntry->jet1ChargedHadronFraction = jet1->chargedHadronFraction;
        outputNtupleEntry->jet1MuonFraction = jet1->muonFraction;
        outputNtupleEntry->jet1PhotonFraction = jet1->photonFraction;
        outputNtupleEntry->jet1ElectronFraction = jet1->electronFraction;
        outputNtupleEntry->jet1HFHadronFraction = jet1->hfHadronFraction;
        outputNtupleEntry->jet1HFEMFraction = jet1->hfEMFraction;

        // matched genJet (MC-only)
        const dijet::LV* jet1MatchedGenJet = nullptr;
        if (!m_isData) {
            jet1MatchedGenJet = getMatchedGenJet(0);
            if (jet1MatchedGenJet) {
                outputNtupleEntry->jet1MatchedGenJetPt = jet1MatchedGenJet->p4.pt();
                outputNtupleEntry->jet1MatchedGenJetPhi = jet1MatchedGenJet->p4.phi();
                outputNtupleEntry->jet1MatchedGenJetEta = jet1MatchedGenJet->p4.eta();
                outputNtupleEntry->jet1MatchedGenJetY = jet1MatchedGenJet->p4.Rapidity();
            }
            // flavor information (jet 1)
            outputNtupleEntry->jet1PartonFlavor = jet1->partonFlavor;
            outputNtupleEntry->jet1HadronFlavor = jet1->hadronFlavor;
        }

        // trigger bitsets
        dijet::TriggerBitsets jet1TriggerBitsets = getTriggerBitsetsForJet(0);
        outputNtupleEntry->hltJet1Match = (jet1TriggerBitsets.hltMatches & jet1TriggerBitsets.l1Matches).to_ulong();
        outputNtupleEntry->hltJet1PtPassThresholds = (jet1TriggerBitsets.hltPassThresholds & jet1TriggerBitsets.l1PassThresholds).to_ulong();

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

            // PF energy fractions (jet 2)
            outputNtupleEntry->jet2NeutralHadronFraction = jet2->neutralHadronFraction;
            outputNtupleEntry->jet2ChargedHadronFraction = jet2->chargedHadronFraction;
            outputNtupleEntry->jet2MuonFraction = jet2->muonFraction;
            outputNtupleEntry->jet2PhotonFraction = jet2->photonFraction;
            outputNtupleEntry->jet2ElectronFraction = jet2->electronFraction;
            outputNtupleEntry->jet2HFHadronFraction = jet2->hfHadronFraction;
            outputNtupleEntry->jet2HFEMFraction = jet2->hfEMFraction;

            // matched genJet (MC-only)
            const dijet::LV* jet2MatchedGenJet = nullptr;
            if (!m_isData) {
                jet2MatchedGenJet = getMatchedGenJet(1);
                if (jet2MatchedGenJet) {
                    outputNtupleEntry->jet2MatchedGenJetPt = jet2MatchedGenJet->p4.pt();
                    outputNtupleEntry->jet2MatchedGenJetPhi = jet2MatchedGenJet->p4.phi();
                    outputNtupleEntry->jet2MatchedGenJetEta = jet2MatchedGenJet->p4.eta();
                    outputNtupleEntry->jet2MatchedGenJetY = jet2MatchedGenJet->p4.Rapidity();
                }
                // flavor information (jet 2)
                outputNtupleEntry->jet2PartonFlavor = jet2->partonFlavor;
                outputNtupleEntry->jet2HadronFlavor = jet2->hadronFlavor;
            }

            // trigger bitsets
            dijet::TriggerBitsets jet2TriggerBitsets = getTriggerBitsetsForJet(1);
            outputNtupleEntry->hltJet2Match = (jet2TriggerBitsets.hltMatches & jet2TriggerBitsets.l1Matches).to_ulong();
            outputNtupleEntry->hltJet2PtPassThresholds = (jet2TriggerBitsets.hltPassThresholds & jet2TriggerBitsets.l1PassThresholds).to_ulong();

            // leading jet pair kinematics
            outputNtupleEntry->jet12mass = (jet1->p4 + jet2->p4).M();
            outputNtupleEntry->jet12ptave = 0.5 * (jet1->p4.pt() + jet2->p4.pt());
            outputNtupleEntry->jet12ystar = 0.5 * (jet1->p4.Rapidity() - jet2->p4.Rapidity());
            outputNtupleEntry->jet12yboost = 0.5 * (jet1->p4.Rapidity() + jet2->p4.Rapidity());

            // matched genJet pair kinematics (MC-only)
            if (jet1MatchedGenJet && jet2MatchedGenJet) {
                outputNtupleEntry->jet12MatchedGenJetPairMass = (jet1MatchedGenJet->p4 + jet2MatchedGenJet->p4).M();
                outputNtupleEntry->jet12MatchedGenJetPairPtAve = 0.5 * (jet1MatchedGenJet->p4.pt() + jet2MatchedGenJet->p4.pt());
                outputNtupleEntry->jet12MatchedGenJetPairYStar = 0.5 * (jet1MatchedGenJet->p4.Rapidity() - jet2MatchedGenJet->p4.Rapidity());
                outputNtupleEntry->jet12MatchedGenJetPairYBoost = 0.5 * (jet1MatchedGenJet->p4.Rapidity() + jet2MatchedGenJet->p4.Rapidity());
            }
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

    // if there is at least one trigger object match for the jet
    if (jetMatchedTriggerObjects != this->dijetJetTriggerObjectsMapHandle->end()) {

        std::set<int> seenPathIndices;
        std::set<double> seenObjectPts;
        unsigned int numValidMatchedTriggerObjects = 0;
        unsigned int numUniqueMatchedTriggerObjects = 0;

        // loop over all trigger objects matched to the jet
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

/**
 * Helper function to determine which HLT path (if any) can be assigned
 * to a reconstructed jet with a particular index.
 */
const dijet::LV* dijet::NtupleProducer::getMatchedGenJet(unsigned int jetIndex) {

    // -- obtain the collection of trigger objects matched to jet with index `jetIndex`
    const auto& jetMatchedJenJet = this->dijetJetGenJetMapHandle->find(
        edm::Ref<dijet::JetCollection>(this->dijetJetCollectionHandle, jetIndex)
    );

    // if there is a gen jet match, return it
    if (jetMatchedJenJet != this->dijetJetGenJetMapHandle->end()) {
        return &(*jetMatchedJenJet->val);
    }

    // if no match, a nullptr is returned
    return nullptr;
}

/**
 * Helper function to determine if a jet has L1 and/or HLT matches, and to check if those matches pass the configured thresholds.
 * This is typically needed for measuring the trigger efficiency.
 */
dijet::TriggerBitsets dijet::NtupleProducer::getTriggerBitsetsForJet(unsigned int jetIndex) {

    dijet::TriggerBitsets triggerBitsets;

    // -- obtain the collection of trigger objects matched to jet with index `jetIndex`
    const auto& jetMatchedTriggerObjects = this->dijetJetTriggerObjectsMapHandle->find(
        edm::Ref<dijet::JetCollection>(this->dijetJetCollectionHandle, jetIndex)
    );

    // if there is at least one trigger object match for the jet
    if (jetMatchedTriggerObjects != this->dijetJetTriggerObjectsMapHandle->end()) {

        // loop over all trigger objects matched to the jet
        for (const auto& jetMatchedTriggerObject : jetMatchedTriggerObjects->val) {

            // set L1 and HLT matching trigger bits if jet is assigned the corresponding HLT path
            for (const auto& assignedPathIdx : jetMatchedTriggerObject->assignedPathIndices) {
                // get the index of trigger in analysis config
                const int idxInConfig = runCache()->triggerPathsIndicesInConfig_[assignedPathIdx];

                // skip unrequested trigger paths
                if (idxInConfig < 0)
                    continue;

                if (jetMatchedTriggerObject->isHLT()) {
                    // HLT trigger object
                    triggerBitsets.hltMatches[idxInConfig] = true;
                }
                else {
                    // L1 trigger object
                    triggerBitsets.l1Matches[idxInConfig] = true;
                }
            }

            // set L1 and HLT emulation trigger bits if jet passes preset thresholds
            for (size_t idxInConfig = 0; idxInConfig < globalCache()->hltPaths_.size(); ++idxInConfig) {
                if (jetMatchedTriggerObject->isHLT() && (this->dijetJetCollectionHandle->at(jetIndex).p4.Pt() >= globalCache()->hltThresholds_[idxInConfig]))
                    triggerBitsets.hltPassThresholds[idxInConfig] = true;
                else if (!jetMatchedTriggerObject->isHLT() && (this->dijetJetCollectionHandle->at(jetIndex).p4.Pt() >= globalCache()->l1Thresholds_[idxInConfig]))
                    triggerBitsets.l1PassThresholds[idxInConfig] = true;
            }
        }
    }

    return triggerBitsets;
}



//define this as a plug-in
using dijet::NtupleProducer;
DEFINE_FWK_MODULE(NtupleProducer);
