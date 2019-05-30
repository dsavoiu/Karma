// system include files
#include <iostream>
#include <bitset>

#include "Karma/ZJetAnalysis/interface/NtupleProducer.h"


// -- constructor
zjet::NtupleProducer::NtupleProducer(const edm::ParameterSet& config, const zjet::NtupleProducerGlobalCache* globalCache) : m_configPSet(config) {
    // -- register products
    produces<zjet::NtupleEntry>();

    // -- process configuration

    // set a flag if we are running on (real) data
    m_isData = m_configPSet.getParameter<bool>("isData");
    m_weightForStitching = m_configPSet.getParameter<double>("weightForStitching");

    // load external file to get `nPUMean` in data
    if (m_isData) {
        m_npuMeanProvider = std::unique_ptr<karma::NPUMeanProvider>(
            new karma::NPUMeanProvider(
                m_configPSet.getParameter<std::string>("npuMeanFile"),
                m_configPSet.getParameter<double>("minBiasCrossSection")
            )
        );
        std::cout << "Reading nPUMean information from file: " << m_configPSet.getParameter<std::string>("npuMeanFile") << std::endl;
    }

    if (!m_isData) {
        if (!m_configPSet.getParameter<std::string>("pileupWeightFile").empty()) {
            m_puWeightProvider = std::unique_ptr<karma::PileupWeightProvider>(
                new karma::PileupWeightProvider(
                    m_configPSet.getParameter<std::string>("pileupWeightFile"),
                    m_configPSet.getParameter<std::string>("pileupWeightHistogramName")
                )
            );
        }
    }

    // -- declare which collections are consumed and create tokens
    karmaEventToken = consumes<karma::Event>(m_configPSet.getParameter<edm::InputTag>("karmaEventSrc"));
    karmaRunToken = consumes<karma::Run, edm::InRun>(m_configPSet.getParameter<edm::InputTag>("karmaRunSrc"));
    karmaVertexCollectionToken = consumes<karma::VertexCollection>(m_configPSet.getParameter<edm::InputTag>("karmaVertexCollectionSrc"));
    karmaJetCollectionToken = consumes<karma::JetCollection>(m_configPSet.getParameter<edm::InputTag>("karmaJetCollectionSrc"));
    karmaMETCollectionToken = consumes<karma::METCollection>(m_configPSet.getParameter<edm::InputTag>("karmaMETCollectionSrc"));

    if (globalCache->channel_ == zjet::AnalysisChannel::EE) {
        karmaElectronCollectionToken = consumes<karma::ElectronCollection>(m_configPSet.getParameter<edm::InputTag>("karmaElectronCollectionSrc"));
    }
    else if (globalCache->channel_ == zjet::AnalysisChannel::MM) {
        karmaMuonCollectionToken = consumes<karma::MuonCollection>(m_configPSet.getParameter<edm::InputTag>("karmaMuonCollectionSrc"));
    }

    if (!m_isData) {
        karmaGenJetCollectionToken = consumes<karma::LVCollection>(m_configPSet.getParameter<edm::InputTag>("karmaGenJetCollectionSrc"));
        karmaGeneratorQCDInfoToken = consumes<karma::GeneratorQCDInfo>(m_configPSet.getParameter<edm::InputTag>("karmaGeneratorQCDInfoSrc"));
        karmaJetGenJetMapToken = consumes<karma::JetGenJetMap>(m_configPSet.getParameter<edm::InputTag>("karmaJetGenJetMapSrc"));
        karmaGenParticleCollectionToken = consumes<karma::GenParticleCollection>(m_configPSet.getParameter<edm::InputTag>("karmaGenParticleCollectionSrc"));
    }

}


// -- destructor
zjet::NtupleProducer::~NtupleProducer() {
}

// -- static member functions

/*static*/ std::unique_ptr<zjet::NtupleProducerGlobalCache> zjet::NtupleProducer::initializeGlobalCache(const edm::ParameterSet& pSet) {
    // -- create the GlobalCache
    return std::unique_ptr<zjet::NtupleProducerGlobalCache>(new zjet::NtupleProducerGlobalCache(pSet));
}


/*static*/ std::shared_ptr<zjet::NtupleProducerRunCache> zjet::NtupleProducer::globalBeginRun(const edm::Run& run, const edm::EventSetup& setup, const zjet::NtupleProducer::GlobalCache* globalCache) {
    // -- create the RunCache
    auto runCache = std::make_shared<zjet::NtupleProducerRunCache>(globalCache->pSet_);

    typename edm::Handle<karma::Run> runHandle;
    run.getByLabel(globalCache->pSet_.getParameter<edm::InputTag>("karmaRunSrc"), runHandle);

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

void zjet::NtupleProducer::produce(edm::Event& event, const edm::EventSetup& setup) {
    std::unique_ptr<zjet::NtupleEntry> outputNtupleEntry(new zjet::NtupleEntry());

    // -- get object collections for event

    // run data
    karma::util::getByTokenOrThrow(event.getRun(), this->karmaRunToken, this->karmaRunHandle);
    // pileup density
    karma::util::getByTokenOrThrow(event, this->karmaEventToken, this->karmaEventHandle);
    // jet collection
    karma::util::getByTokenOrThrow(event, this->karmaJetCollectionToken, this->karmaJetCollectionHandle);
    // MET collection
    karma::util::getByTokenOrThrow(event, this->karmaMETCollectionToken, this->karmaMETCollectionHandle);

    if (globalCache()->channel_ == zjet::AnalysisChannel::EE) {
        karma::util::getByTokenOrThrow(event, this->karmaElectronCollectionToken, this->karmaElectronCollectionHandle);
    }
    else if (globalCache()->channel_ == zjet::AnalysisChannel::MM) {
        karma::util::getByTokenOrThrow(event, this->karmaMuonCollectionToken, this->karmaMuonCollectionHandle);
    }

    if (!m_isData) {
        // QCD generator information
        karma::util::getByTokenOrThrow(event, this->karmaGeneratorQCDInfoToken, this->karmaGeneratorQCDInfoHandle);
        // genParticle collection
        karma::util::getByTokenOrThrow(event, this->karmaGenParticleCollectionToken, this->karmaGenParticleCollectionHandle);
        // gen jet collection
        karma::util::getByTokenOrThrow(event, this->karmaGenJetCollectionToken, this->karmaGenJetCollectionHandle);
        // jet genJet map
        karma::util::getByTokenOrThrow(event, this->karmaJetGenJetMapToken, this->karmaJetGenJetMapHandle);
    }

    assert(this->karmaMETCollectionHandle->size() == 1);  // only allow MET collections containing a single MET object

    // -- populate outputs

    // event metadata
    outputNtupleEntry->run = event.id().run();
    outputNtupleEntry->lumi = event.id().luminosityBlock();
    outputNtupleEntry->event = event.id().event();
    outputNtupleEntry->bx = event.bunchCrossing();

    // -- copy event content to ntuple
    outputNtupleEntry->rho     = this->karmaEventHandle->rho;
    if (m_isData) {
        // nPUMean estimate in data, taken from external file
        if (m_npuMeanProvider) {
            outputNtupleEntry->nPUMean = m_npuMeanProvider->getNPUMean(
                outputNtupleEntry->run,
                outputNtupleEntry->lumi
            );
        }
    }
    else {
        outputNtupleEntry->nPU     = this->karmaEventHandle->nPU;
        outputNtupleEntry->nPUMean = this->karmaEventHandle->nPUTrue;
        if (m_puWeightProvider) {
            outputNtupleEntry->pileupWeight = this->m_puWeightProvider->getPileupWeight(outputNtupleEntry->nPUMean);
        }
    }

    // write information related to primary vertices

    // TEMPORARY: make PV collection will be standard in newer skims
    // obtain primary vertex collection (if available)
    bool hasPVCollection = event.getByToken(this->karmaVertexCollectionToken, this->karmaVertexCollectionHandle);
    if (hasPVCollection) {
        // fill from PV collection
        outputNtupleEntry->npv     = this->karmaVertexCollectionHandle->size();
        outputNtupleEntry->npvGood = std::count_if(
            this->karmaVertexCollectionHandle->begin(),
            this->karmaVertexCollectionHandle->end(),
            [](const karma::Vertex& vtx) {return vtx.isGoodOfflineVertex();}
        );
    }
    else {
        // fill from karma::Event
        outputNtupleEntry->npv     = this->karmaEventHandle->npv;
        outputNtupleEntry->npvGood = this->karmaEventHandle->npvGood;
    }

    // weights
    outputNtupleEntry->weightForStitching = m_weightForStitching;

    // -- generator data (MC-only)
    if (!m_isData) {
        outputNtupleEntry->generatorWeight = this->karmaGeneratorQCDInfoHandle->weight;
        outputNtupleEntry->generatorWeightProduct = this->karmaGeneratorQCDInfoHandle->weightProduct;
        if (this->karmaGeneratorQCDInfoHandle->binningValues.size() > 0)
            outputNtupleEntry->binningValue = this->karmaGeneratorQCDInfoHandle->binningValues[0];

        // gen jets
        const auto& genJets = this->karmaGenJetCollectionHandle;  // convenience
        if (genJets->size() > 0) {
            const karma::LV* genJet1 = &genJets->at(0);

            outputNtupleEntry->genJet1Pt = genJet1->p4.pt();
            outputNtupleEntry->genJet1Phi = genJet1->p4.phi();
            outputNtupleEntry->genJet1Eta = genJet1->p4.eta();
            outputNtupleEntry->genJet1Y = genJet1->p4.Rapidity();

            if (genJets->size() > 1) {
                const karma::LV* genJet2 = &genJets->at(1);

                outputNtupleEntry->genJet2Pt = genJet2->p4.pt();
                outputNtupleEntry->genJet2Phi = genJet2->p4.phi();
                outputNtupleEntry->genJet2Eta = genJet2->p4.eta();
                outputNtupleEntry->genJet2Y = genJet2->p4.Rapidity();
            }
        }
    }

    const auto& jets = this->karmaJetCollectionHandle;  // convenience
    // leading jet kinematics
    if (jets->size() > 0) {
        const karma::Jet* jet1 = &jets->at(0);
        // write out jetID (1 if pass, 0 if fail, -1 if not requested/not available)
        if (globalCache()->jetIDProvider_)
            outputNtupleEntry->jet1Id = (globalCache()->jetIDProvider_->getJetID(*jet1));

        outputNtupleEntry->jet1Pt = jet1->p4.pt();
        outputNtupleEntry->jet1Phi = jet1->p4.phi();
        outputNtupleEntry->jet1Eta = jet1->p4.eta();
        outputNtupleEntry->jet1Y = jet1->p4.Rapidity();

        // matched genJet (MC-only)
        const karma::LV* jet1MatchedGenJet = nullptr;
        if (!m_isData) {
            jet1MatchedGenJet = getMatchedGenJet(0);
            if (jet1MatchedGenJet) {
                outputNtupleEntry->jet1MatchedGenJetPt = jet1MatchedGenJet->p4.pt();
                outputNtupleEntry->jet1MatchedGenJetPhi = jet1MatchedGenJet->p4.phi();
                outputNtupleEntry->jet1MatchedGenJetEta = jet1MatchedGenJet->p4.eta();
                outputNtupleEntry->jet1MatchedGenJetY = jet1MatchedGenJet->p4.Rapidity();
            }
        }

        // second-leading jet kinematics
        if (jets->size() > 1) {
            const karma::Jet* jet2 = &jets->at(1);
            // write out jetID (1 if pass, 0 if fail, -1 if not requested/not available)
            if (globalCache()->jetIDProvider_)
                outputNtupleEntry->jet2Id = (globalCache()->jetIDProvider_->getJetID(*jet2));

            outputNtupleEntry->jet2Pt = jet2->p4.pt();
            outputNtupleEntry->jet2Phi = jet2->p4.phi();
            outputNtupleEntry->jet2Eta = jet2->p4.eta();
            outputNtupleEntry->jet2Y = jet2->p4.Rapidity();

            // matched genJet (MC-only)
            const karma::LV* jet2MatchedGenJet = nullptr;
            if (!m_isData) {
                jet2MatchedGenJet = getMatchedGenJet(1);
                if (jet2MatchedGenJet) {
                    outputNtupleEntry->jet2MatchedGenJetPt = jet2MatchedGenJet->p4.pt();
                    outputNtupleEntry->jet2MatchedGenJetPhi = jet2MatchedGenJet->p4.phi();
                    outputNtupleEntry->jet2MatchedGenJetEta = jet2MatchedGenJet->p4.eta();
                    outputNtupleEntry->jet2MatchedGenJetY = jet2MatchedGenJet->p4.Rapidity();
                }
            }
        }
    }

    // -- leptons

    if (globalCache()->channel_ == zjet::AnalysisChannel::EE) {
        this->fillLeptonVariables(outputNtupleEntry.get(), *this->karmaElectronCollectionHandle);
    }
    else if (globalCache()->channel_ == zjet::AnalysisChannel::MM) {
        this->fillLeptonVariables(outputNtupleEntry.get(), *this->karmaMuonCollectionHandle);
    }

    outputNtupleEntry->met = this->karmaMETCollectionHandle->at(0).p4.Pt();
    outputNtupleEntry->sumEt = this->karmaMETCollectionHandle->at(0).sumEt;
    outputNtupleEntry->metRaw = this->karmaMETCollectionHandle->at(0).uncorP4.Pt();
    outputNtupleEntry->sumEtRaw = this->karmaMETCollectionHandle->at(0).uncorSumEt;

    // move outputs to event tree
    event.put(std::move(outputNtupleEntry));
}

template<typename TLeptonCollection>
void zjet::NtupleProducer::fillLeptonVariables(zjet::NtupleEntry* outputNtupleEntry, const TLeptonCollection& leptons) {
    if (leptons.size() > 0) {
        outputNtupleEntry->lepton1Pt = leptons.at(0).p4.pt();
        outputNtupleEntry->lepton1Phi = leptons.at(0).p4.phi();
        outputNtupleEntry->lepton1Eta = leptons.at(0).p4.eta();
        outputNtupleEntry->lepton1PDGId = leptons.at(0).pdgId;
        if (leptons.size() > 1) {
            outputNtupleEntry->lepton2Pt = leptons.at(1).p4.pt();
            outputNtupleEntry->lepton2Phi = leptons.at(1).p4.phi();
            outputNtupleEntry->lepton2Eta = leptons.at(1).p4.eta();
            outputNtupleEntry->lepton2PDGId = leptons.at(1).pdgId;
        }
    }
}

void zjet::NtupleProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
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
const karma::LV* zjet::NtupleProducer::getMatchedGenJet(unsigned int jetIndex) {

    // -- obtain the collection of trigger objects matched to jet with index `jetIndex`
    const auto& jetMatchedJenJet = this->karmaJetGenJetMapHandle->find(
        edm::Ref<karma::JetCollection>(this->karmaJetCollectionHandle, jetIndex)
    );

    // if there is a gen jet match, return it
    if (jetMatchedJenJet != this->karmaJetGenJetMapHandle->end()) {
        return &(*jetMatchedJenJet->val);
    }

    // if no match, a nullptr is returned
    return nullptr;
}

//define this as a plug-in
using ZJetNtupleProducer = zjet::NtupleProducer;
DEFINE_FWK_MODULE(ZJetNtupleProducer);
