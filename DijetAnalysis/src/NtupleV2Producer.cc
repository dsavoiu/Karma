// system include files
#include <iostream>
#include <bitset>
#include <exception>

#include "Karma/DijetAnalysis/interface/NtupleV2Producer.h"

#include "boost/filesystem/path.hpp"
#include "boost/filesystem/operations.hpp"

// -- constructor
dijet::NtupleV2Producer::NtupleV2Producer(const edm::ParameterSet& config, const dijet::NtupleV2ProducerGlobalCache* globalCache) : m_configPSet(config) {
    // -- register products
    produces<dijet::NtupleV2Entry>();

    // -- process configuration

    /// m_triggerEfficienciesProvider = std::unique_ptr<karma::TriggerEfficienciesProvider>(
    ///     new TriggerEfficienciesProvider(m_configPSet.getParameter<std::string>("triggerEfficienciesFile"))
    /// );

    /// std::cout << "Read trigger efficiencies for paths:" << std::endl;
    /// for (const auto& mapIter : m_triggerEfficienciesProvider->triggerEfficiencies()) {
    ///     std::cout << "    " << mapIter.first << " -> " << &(*mapIter.second) << std::endl;
    /// }

    // set a flag if we are running on (real) data
    m_isData = m_configPSet.getParameter<bool>("isData");
    m_stitchingWeight = m_configPSet.getParameter<double>("stitchingWeight");

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

    // load external file to get `pileupWeight` in MC
    if (!m_isData) {
        if (!m_configPSet.getParameter<std::string>("pileupWeightFile").empty()) {
            m_puWeightProvider = std::unique_ptr<karma::PileupWeightProvider>(
                new karma::PileupWeightProvider(
                    m_configPSet.getParameter<std::string>("pileupWeightFile"),
                    m_configPSet.getParameter<std::string>("pileupWeightHistogramName")
                )
            );
        }
        /*
        // can provide an alternative pileup weight file
        if (!m_configPSet.getParameter<std::string>("pileupWeightFileAlt").empty()) {
            m_puWeightProviderAlt = std::unique_ptr<karma::PileupWeightProvider>(
                new karma::PileupWeightProvider(
                    m_configPSet.getParameter<std::string>("pileupWeightFileAlt"),
                    m_configPSet.getParameter<std::string>("pileupWeightHistogramName")
                )
            );
        }
        */
        // can provide pileup weight files for each HLT path
        auto pileupWeightByHLTFileBasename = m_configPSet.getParameter<std::string>("pileupWeightByHLTFileBasename");
        if (!pileupWeightByHLTFileBasename.empty()) {
            m_puWeightProvidersByHLT.resize(globalCache->hltPaths_.size());
            for (size_t iHLTPath = 0; iHLTPath < globalCache->hltPaths_.size(); ++iHLTPath) {
                std::string pileupWeightFileName = pileupWeightByHLTFileBasename + "_" + globalCache->hltPaths_.at(iHLTPath) + ".root";

                if (!boost::filesystem::exists(pileupWeightFileName)) {
                    std::cout << "No HLT-dependent pileup weight information found for trigger path: " << globalCache->hltPaths_.at(iHLTPath) << std::endl;
                    continue;
                }

                std::cout << "Reading HLT-dependent pileup weight information from file: " << pileupWeightFileName << std::endl;
                m_puWeightProvidersByHLT[iHLTPath] = new karma::PileupWeightProvider(
                    pileupWeightByHLTFileBasename + "_" + globalCache->hltPaths_[iHLTPath] + ".root",
                    m_configPSet.getParameter<std::string>("pileupWeightHistogramName")
                );
            }
        }
    }

    // -- declare which collections are consumed and create tokens
    karmaEventToken = consumes<karma::Event>(m_configPSet.getParameter<edm::InputTag>("karmaEventSrc"));
    karmaRunToken = consumes<karma::Run, edm::InRun>(m_configPSet.getParameter<edm::InputTag>("karmaRunSrc"));
    karmaVertexCollectionToken = consumes<karma::VertexCollection>(m_configPSet.getParameter<edm::InputTag>("karmaVertexCollectionSrc"));
    karmaJetCollectionToken = consumes<karma::JetCollection>(m_configPSet.getParameter<edm::InputTag>("karmaJetCollectionSrc"));
    karmaMETCollectionToken = consumes<karma::METCollection>(m_configPSet.getParameter<edm::InputTag>("karmaMETCollectionSrc"));
    karmaJetTriggerObjectsMapToken = consumes<karma::JetTriggerObjectsMap>(m_configPSet.getParameter<edm::InputTag>("karmaJetTriggerObjectMapSrc"));
    if (!m_isData) {
        karmaGenJetCollectionToken = consumes<karma::LVCollection>(m_configPSet.getParameter<edm::InputTag>("karmaGenJetCollectionSrc"));
        karmaGeneratorQCDInfoToken = consumes<karma::GeneratorQCDInfo>(m_configPSet.getParameter<edm::InputTag>("karmaGeneratorQCDInfoSrc"));
        karmaJetGenJetMapToken = consumes<karma::JetGenJetMap>(m_configPSet.getParameter<edm::InputTag>("karmaJetGenJetMapSrc"));
        karmaGenParticleCollectionToken = consumes<karma::GenParticleCollection>(m_configPSet.getParameter<edm::InputTag>("karmaGenParticleCollectionSrc"));
    }
    else {
        karmaPrefiringWeightToken = consumes<double>(m_configPSet.getParameter<edm::InputTag>("karmaPrefiringWeightSrc"));
        karmaPrefiringWeightUpToken = consumes<double>(m_configPSet.getParameter<edm::InputTag>("karmaPrefiringWeightUpSrc"));
        karmaPrefiringWeightDownToken = consumes<double>(m_configPSet.getParameter<edm::InputTag>("karmaPrefiringWeightDownSrc"));
    }

}


// -- destructor
dijet::NtupleV2Producer::~NtupleV2Producer() {
}

// -- static member functions

/*static*/ std::unique_ptr<dijet::NtupleV2ProducerGlobalCache> dijet::NtupleV2Producer::initializeGlobalCache(const edm::ParameterSet& pSet) {
    // -- create the GlobalCache
    return std::unique_ptr<dijet::NtupleV2ProducerGlobalCache>(new dijet::NtupleV2ProducerGlobalCache(pSet));
}


/*static*/ std::shared_ptr<dijet::NtupleV2ProducerRunCache> dijet::NtupleV2Producer::globalBeginRun(const edm::Run& run, const edm::EventSetup& setup, const dijet::NtupleV2Producer::GlobalCache* globalCache) {
    // -- create the RunCache
    auto runCache = std::make_shared<dijet::NtupleV2ProducerRunCache>(globalCache->pSet_);

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
                ///std::cout << " -> matched! " << iPath << " = " << iRequestedPath << std::endl;
                runCache->triggerPathsIndicesInConfig_[iPath] = iRequestedPath;
                break;
            }
        }
    }

    // -- retrieve names of MET filters in skim

    // retrieve process name from Karma Run InputTag
    std::string processName = globalCache->pSet_.getParameter<edm::InputTag>("karmaEventSrc").process();

    // if no specific process name, use previous process name
    if (processName.empty()) {
        const auto& processHistory = run.processHistory();
        processName = processHistory.at(processHistory.size() - 2).processName();
    }

    // retrieve the MET filter names from skim
    try {
        const auto& metFiltersInSkim = karma::util::getModuleParameterFromHistory<std::vector<std::string>>(
            run, processName, "karmaEvents", "metFilterNames");

        for (const auto& requestedMETFilterName : globalCache->metFilterNames_) {
            const auto& it = std::find(
                metFiltersInSkim.begin(),
                metFiltersInSkim.end(),
                requestedMETFilterName
            );

            // throw if MET filter not found for a requested label!
            if (it == metFiltersInSkim.end()) {
                edm::Exception exception(edm::errors::NotFound);
                exception
                    << "Cannot find MET filter for name '" << requestedMETFilterName << "' in skim!";
                throw exception;
            }

            // retrieve index
            int index = std::distance(metFiltersInSkim.begin(), it);
            runCache->metFilterIndicesInSkim_.emplace_back(index);
        }
    }
    catch (edm::Exception& e) {
        std::cout << "[WARNING] Could not retrieve MET filters from skim!" << std::endl;
    }

    return runCache;
}

// -- member functions

void dijet::NtupleV2Producer::produce(edm::Event& event, const edm::EventSetup& setup) {
    std::unique_ptr<dijet::NtupleV2Entry> outputNtupleV2Entry(new dijet::NtupleV2Entry());

    // -- get object collections for event

    // run data
    karma::util::getByTokenOrThrow(event.getRun(), this->karmaRunToken, this->karmaRunHandle);
    // pileup density
    karma::util::getByTokenOrThrow(event, this->karmaEventToken, this->karmaEventHandle);
    // jet collection
    karma::util::getByTokenOrThrow(event, this->karmaJetCollectionToken, this->karmaJetCollectionHandle);
    // MET collection
    karma::util::getByTokenOrThrow(event, this->karmaMETCollectionToken, this->karmaMETCollectionHandle);
    // jet trigger objects map
    karma::util::getByTokenOrThrow(event, this->karmaJetTriggerObjectsMapToken, this->karmaJetTriggerObjectsMapHandle);
    if (!m_isData) {
        // QCD generator information
        karma::util::getByTokenOrThrow(event, this->karmaGeneratorQCDInfoToken, this->karmaGeneratorQCDInfoHandle);
        // genParticle collection
        karma::util::getByTokenOrThrow(event, this->karmaGenParticleCollectionToken, this->karmaGenParticleCollectionHandle);
        // gen jet collection
        karma::util::getByTokenOrThrow(event, this->karmaGenJetCollectionToken, this->karmaGenJetCollectionHandle);
        // Jet-GenJet map
        karma::util::getByTokenOrThrow(event, this->karmaJetGenJetMapToken, this->karmaJetGenJetMapHandle);
    }
    else {
        // prefiring weights
        karma::util::getByTokenOrThrow(event, this->karmaPrefiringWeightToken, this->karmaPrefiringWeightHandle);
        karma::util::getByTokenOrThrow(event, this->karmaPrefiringWeightUpToken, this->karmaPrefiringWeightUpHandle);
        karma::util::getByTokenOrThrow(event, this->karmaPrefiringWeightDownToken, this->karmaPrefiringWeightDownHandle);
    }

    assert(this->karmaMETCollectionHandle->size() == 1);  // only allow MET collections containing a single MET object

    // get random number generator engine
    edm::Service<edm::RandomNumberGenerator> rng;
    CLHEP::HepRandomEngine& rngEngine = rng->getEngine(event.streamID());

    // -- populate outputs

    // event metadata
    outputNtupleV2Entry->run = event.id().run();
    outputNtupleV2Entry->lumi = event.id().luminosityBlock();
    outputNtupleV2Entry->event = event.id().event();
    outputNtupleV2Entry->bx = event.bunchCrossing();
    outputNtupleV2Entry->randomUniform = CLHEP::RandFlat::shoot(&rngEngine, 0, 1);

    // -- copy event content to ntuple
    outputNtupleV2Entry->rho     = this->karmaEventHandle->rho;
    if (m_isData) {
        // nPUMean estimate in data, taken from external file
        if (m_npuMeanProvider) {
            outputNtupleV2Entry->nPUMean = m_npuMeanProvider->getNPUMean(
                outputNtupleV2Entry->run,
                outputNtupleV2Entry->lumi
            );
        }
    }
    else {
        outputNtupleV2Entry->nPU     = this->karmaEventHandle->nPU;
        outputNtupleV2Entry->nPUMean = this->karmaEventHandle->nPUTrue;
        if (m_puWeightProvider) {
            outputNtupleV2Entry->pileupWeight = this->m_puWeightProvider->getPileupWeight(outputNtupleV2Entry->nPUMean);
        }
        /*if (m_puWeightProviderAlt) {
            outputNtupleV2Entry->pileupWeightAlt = this->m_puWeightProviderAlt->getPileupWeight(outputNtupleV2Entry->nPUMean);
        }*/
    }

    // write information related to primary vertices

    // TEMPORARY: make PV collection will be standard in newer skims
    // obtain primary vertex collection (if available)
    bool hasPVCollection = event.getByToken(this->karmaVertexCollectionToken, this->karmaVertexCollectionHandle);
    if (hasPVCollection) {
        // fill from PV collection
        outputNtupleV2Entry->npv     = this->karmaVertexCollectionHandle->size();
        outputNtupleV2Entry->npvGood = std::count_if(
            this->karmaVertexCollectionHandle->begin(),
            this->karmaVertexCollectionHandle->end(),
            [](const karma::Vertex& vtx) {return vtx.isGoodOfflineVertex();}
        );
    }
    else {
        // fill from karma::Event
        outputNtupleV2Entry->npv     = this->karmaEventHandle->npv;
        outputNtupleV2Entry->npvGood = this->karmaEventHandle->npvGood;
    }

    // weights
    outputNtupleV2Entry->stitchingWeight = m_stitchingWeight;

    // prefiring weights
    if (m_isData) {
        outputNtupleV2Entry->prefiringWeight = *(this->karmaPrefiringWeightHandle);
        outputNtupleV2Entry->prefiringWeightUp = *(this->karmaPrefiringWeightUpHandle);
        outputNtupleV2Entry->prefiringWeightDown = *(this->karmaPrefiringWeightDownHandle);
    }

    // -- trigger results and prescales
    // number of triggers requested in analysis config
    //outputNtupleV2Entry->nTriggers = globalCache()->hltPaths_.size();
    if (globalCache()->doPrescales_) {
        outputNtupleV2Entry->triggerPrescales.resize(globalCache()->hltPaths_.size(), 0);
    }
    // store trigger results as `dijet::TriggerBits`
    dijet::TriggerBits bitsetHLTBits;
    int indexHighestFiredTriggerPath = -1;  // keep track (mainly for simulated PU weight application)
    // go through all triggers in skim
    for (size_t iBit = 0; iBit < this->karmaEventHandle->hltBits.size(); ++iBit) {
        // the index is < `globalCache()->hltPaths_.size()` by definition
        const int idxInConfig = runCache()->triggerPathsIndicesInConfig_[iBit];

        if (idxInConfig >= 0) {
            // store prescale value
            if (globalCache()->doPrescales_) {
                outputNtupleV2Entry->triggerPrescales[idxInConfig] = this->karmaEventHandle->triggerPathHLTPrescales[iBit] *
                                                                     this->karmaEventHandle->triggerPathL1Prescales[iBit];
            }
            // if trigger fired
            if (this->karmaEventHandle->hltBits[iBit]) {
                // set bit
                bitsetHLTBits[idxInConfig] = true;
                indexHighestFiredTriggerPath = idxInConfig;
            }
        }
    }

    // -- MET filter bits
    dijet::TriggerBits bitsetMETFilterBits;
    for (size_t iBit = 0; iBit < runCache()->metFilterIndicesInSkim_.size(); ++iBit) {
        bitsetMETFilterBits[iBit] = false;
        if (this->karmaEventHandle->metFilterBits.at(runCache()->metFilterIndicesInSkim_[iBit])) {
            bitsetMETFilterBits[iBit] = true;
        }
    }

    // encode bitsets as 'unsigned long'
    outputNtupleV2Entry->triggerResults = bitsetHLTBits.to_ulong();
    outputNtupleV2Entry->metFilterBits = bitsetMETFilterBits.to_ulong();

    // -- generator data (MC-only)
    if (!m_isData) {
        ////std::cout << "GEN" << std::endl;
        outputNtupleV2Entry->generatorWeight = this->karmaGeneratorQCDInfoHandle->weight;
        if (this->karmaGeneratorQCDInfoHandle->binningValues.size() > 0)
            outputNtupleV2Entry->binningValue = this->karmaGeneratorQCDInfoHandle->binningValues[0];

        outputNtupleV2Entry->incomingParton1Flavor = this->karmaGeneratorQCDInfoHandle->parton1PdgId;
        outputNtupleV2Entry->incomingParton2Flavor = this->karmaGeneratorQCDInfoHandle->parton2PdgId;
        outputNtupleV2Entry->incomingParton1x = this->karmaGeneratorQCDInfoHandle->parton1x;
        outputNtupleV2Entry->incomingParton2x = this->karmaGeneratorQCDInfoHandle->parton2x;
        outputNtupleV2Entry->scalePDF = this->karmaGeneratorQCDInfoHandle->scalePDF;
        outputNtupleV2Entry->alphaQCD = this->karmaGeneratorQCDInfoHandle->alphaQCD;
    }

    // -- jets
    ////std::cout << "JETS" << std::endl;
    size_t nJet = this->karmaJetCollectionHandle->size();
    outputNtupleV2Entry->Jet_pt.resize(nJet);
    outputNtupleV2Entry->Jet_phi.resize(nJet);
    outputNtupleV2Entry->Jet_eta.resize(nJet);
    outputNtupleV2Entry->Jet_mass.resize(nJet);
    outputNtupleV2Entry->Jet_area.resize(nJet);
    outputNtupleV2Entry->Jet_rawFactor.resize(nJet);
    outputNtupleV2Entry->Jet_hadronFlavor.resize(nJet);
    outputNtupleV2Entry->Jet_partonFlavor.resize(nJet);
    outputNtupleV2Entry->Jet_genJetMatch.resize(nJet);
    outputNtupleV2Entry->Jet_jerSmearingFactor.resize(nJet);
    outputNtupleV2Entry->Jet_jerScaleFactor.resize(nJet);
    outputNtupleV2Entry->Jet_hltMatch.resize(nJet);
    outputNtupleV2Entry->Jet_l1Match.resize(nJet);
    outputNtupleV2Entry->Jet_hltPassPtAveThreshold.resize(nJet);
    outputNtupleV2Entry->Jet_hltPassPtThreshold.resize(nJet);
    outputNtupleV2Entry->Jet_l1PassPtThreshold.resize(nJet);
    outputNtupleV2Entry->Jet_jetId.resize(nJet);
    /* -- not needed for now
    outputNtupleV2Entry->Jet_NHF.resize(nJet);
    outputNtupleV2Entry->Jet_NEMF.resize(nJet);
    outputNtupleV2Entry->Jet_CHF.resize(nJet);
    outputNtupleV2Entry->Jet_MUF.resize(nJet);
    outputNtupleV2Entry->Jet_CEMF.resize(nJet);
    outputNtupleV2Entry->Jet_NumConst.resize(nJet);
    outputNtupleV2Entry->Jet_NumNeutralParticles.resize(nJet);
    */
    outputNtupleV2Entry->Jet_jesUncertaintyFactors.resize(nJet);
    for (size_t iJet = 0; iJet < nJet; ++iJet) {

        // retrieve jet
        const auto& jet = this->karmaJetCollectionHandle->at(iJet);

        // write out jetID (1 if pass, 0 if fail, -1 if not requested/not available)
        if (globalCache()->jetIDProvider_)
            outputNtupleV2Entry->Jet_jetId[iJet] = (globalCache()->jetIDProvider_->getJetID(jet));

        outputNtupleV2Entry->Jet_pt[iJet] = jet.p4.pt();
        outputNtupleV2Entry->Jet_phi[iJet] = jet.p4.phi();
        outputNtupleV2Entry->Jet_eta[iJet] = jet.p4.eta();
        outputNtupleV2Entry->Jet_mass[iJet] = jet.p4.mass();
        outputNtupleV2Entry->Jet_area[iJet] = jet.area;
        outputNtupleV2Entry->Jet_rawFactor[iJet] = 1.0 - jet.uncorP4.pt()/jet.p4.pt();

        /* -- not needed for now
        // PF energy fractions
        outputNtupleV2Entry->Jet_NHF[iJet] = jet.neutralHadronFraction;
        outputNtupleV2Entry->Jet_NEMF[iJet] = jet.neutralEMFraction;
        outputNtupleV2Entry->Jet_CHF[iJet] = jet.chargedHadronFraction;
        outputNtupleV2Entry->Jet_MUF[iJet] = jet.muonFraction;
        outputNtupleV2Entry->Jet_CEMF[iJet] = jet.chargedEMFraction;
        outputNtupleV2Entry->Jet_NumConst[iJet] = jet.nConstituents;
        outputNtupleV2Entry->Jet_NumNeutralParticles[iJet] = jet.nConstituents - jet.nCharged;
        */
        // factors used for individual JEC uncertainties
        for (const auto& jesUncSrc : globalCache()->jesUncertaintySources_) {
            outputNtupleV2Entry->Jet_jesUncertaintyFactors[iJet].push_back(jet.transientDoubles_.at(jesUncSrc));
        };

        // matched genJet (MC-only)
        if (!m_isData) {
            // index of matched gen jet
            outputNtupleV2Entry->Jet_genJetMatch[iJet] = getMatchedGenJetIndex(iJet);
            // flavor information
            outputNtupleV2Entry->Jet_partonFlavor[iJet] = jet.partonFlavor;
            outputNtupleV2Entry->Jet_hadronFlavor[iJet] = jet.hadronFlavor;
            // factors used for JER smearing
            try {
                outputNtupleV2Entry->Jet_jerSmearingFactor[iJet] = jet.transientDoubles_.at("JERSmearingFactor");
                outputNtupleV2Entry->Jet_jerScaleFactor[iJet] = jet.transientDoubles_.at("JERScaleFactor");
            }
            catch (const std::out_of_range& err) {
                // factors not calculated (jets not being smeared) -> set to unity
                outputNtupleV2Entry->Jet_jerSmearingFactor[iJet] = 1.0;
                outputNtupleV2Entry->Jet_jerScaleFactor[iJet] = 1.0;
            }
        }

        // trigger bitsets
        dijet::TriggerBitsets jetTriggerBitsets = getTriggerBitsetsForJet(iJet);
        outputNtupleV2Entry->Jet_hltMatch[iJet] = (jetTriggerBitsets.hltMatches | globalCache()->hltZeroThresholdMask_).to_ulong();
        outputNtupleV2Entry->Jet_l1Match[iJet]  = (jetTriggerBitsets.l1Matches  | globalCache()->l1ZeroThresholdMask_).to_ulong();
        outputNtupleV2Entry->Jet_hltPassPtThreshold[iJet] = jetTriggerBitsets.hltPassThresholds.to_ulong();
        outputNtupleV2Entry->Jet_l1PassPtThreshold[iJet] = jetTriggerBitsets.l1PassThresholds.to_ulong();

        // bitsets for ptave (index 0 for ptave of jets 0 and 1, etc)
        if (iJet < nJet-1) {
            dijet::TriggerBitsets jetPtAveTriggerBitsets = getTriggerBitsetsForJetPair(iJet);
            outputNtupleV2Entry->Jet_hltPassPtAveThreshold[iJet] = jetPtAveTriggerBitsets.hltPassThresholds.to_ulong();
        }
        outputNtupleV2Entry->Jet_hltPassPtAveThreshold[nJet-1] = 0;  // undefined, fill with 0
    }

    // -- gen jets
    if (!m_isData) {
        size_t nGenJet = this->karmaGenJetCollectionHandle->size();
        outputNtupleV2Entry->GenJet_pt.resize(nGenJet);
        outputNtupleV2Entry->GenJet_phi.resize(nGenJet);
        outputNtupleV2Entry->GenJet_eta.resize(nGenJet);
        outputNtupleV2Entry->GenJet_mass.resize(nGenJet);
        for (size_t iGenJet = 0; iGenJet < nGenJet; ++iGenJet) {

            // retrieve jet
            const auto& genJet = this->karmaGenJetCollectionHandle->at(iGenJet);

            outputNtupleV2Entry->GenJet_pt[iGenJet] = genJet.p4.pt();
            outputNtupleV2Entry->GenJet_phi[iGenJet] = genJet.p4.phi();
            outputNtupleV2Entry->GenJet_eta[iGenJet] = genJet.p4.eta();
            outputNtupleV2Entry->GenJet_mass[iGenJet] = genJet.p4.mass();
        }
    }

    // -- MET
    outputNtupleV2Entry->MET_pt = this->karmaMETCollectionHandle->at(0).p4.Pt();
    outputNtupleV2Entry->MET_sumEt = this->karmaMETCollectionHandle->at(0).sumEt;
    outputNtupleV2Entry->MET_rawPt = this->karmaMETCollectionHandle->at(0).uncorP4.Pt();
    outputNtupleV2Entry->MET_rawSumEt = this->karmaMETCollectionHandle->at(0).uncorSumEt;

    // determine PU weight as a function of the active HLT path
    if (!m_isData) {
        // determine PU weight by simulated trigger
        outputNtupleV2Entry->pileupWeightSimulatedHLT = -1.0;
        if (indexHighestFiredTriggerPath >= 0) {
            auto* puWeightByHLTProvider = m_puWeightProvidersByHLT.at(indexHighestFiredTriggerPath);
            if (puWeightByHLTProvider) {
                outputNtupleV2Entry->pileupWeightSimulatedHLT = puWeightByHLTProvider->getPileupWeight(outputNtupleV2Entry->nPUMean);
            }
        }
    }

    // move outputs to event tree
    event.put(std::move(outputNtupleV2Entry));
}


void dijet::NtupleV2Producer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
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
dijet::HLTAssignment dijet::NtupleV2Producer::getHLTAssignment(unsigned int jetIndex) {

    dijet::HLTAssignment hltAssignment;

    // -- obtain the collection of trigger objects matched to jet with index `jetIndex`
    const auto& jetMatchedTriggerObjects = this->karmaJetTriggerObjectsMapHandle->find(
        edm::Ref<karma::JetCollection>(this->karmaJetCollectionHandle, jetIndex)
    );

    // if there is at least one trigger object match for the jet
    if (jetMatchedTriggerObjects != this->karmaJetTriggerObjectsMapHandle->end()) {

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
 * Obtain index of gen jet matched to a reco jet with a particular index
 */
int dijet::NtupleV2Producer::getMatchedGenJetIndex(unsigned int jetIndex) const {

    // -- obtain the collection of trigger objects matched to jet with index `jetIndex`
    const auto& jetMatchedGenJet = this->karmaJetGenJetMapHandle->find(
        edm::Ref<karma::JetCollection>(this->karmaJetCollectionHandle, jetIndex)
    );

    // if there is a gen jet match, return it
    if (jetMatchedGenJet != this->karmaJetGenJetMapHandle->end()) {
        return jetMatchedGenJet->val.key();
    }

    // no match
    return -1;
    /*const karma::LV* matchedGenJet = getMatchedGenJet(jetIndex);

    // no match -> return -1
    if (!matchedGenJet) {
        return -1;
    }

    // retrieve the index
    const auto& itMatchedGenJet = std::find(
        this->karmaGenJetCollectionHandle->begin(),
        this->karmaGenJetCollectionHandle->end(),
        *matchedGenJet
    );
    return std::distance(this->karmaGenJetCollectionHandle->begin(), itMatchedGenJet);*/
}

/**
 * Obtain gen jet matched to a reco jet with a particular index
 */
const karma::LV* dijet::NtupleV2Producer::getMatchedGenJet(unsigned int jetIndex) const {

    // -- obtain the collection of trigger objects matched to jet with index `jetIndex`
    const auto& jetMatchedGenJet = this->karmaJetGenJetMapHandle->find(
        edm::Ref<karma::JetCollection>(this->karmaJetCollectionHandle, jetIndex)
    );

    // if there is a gen jet match, return it
    if (jetMatchedGenJet != this->karmaJetGenJetMapHandle->end()) {
        return &(*jetMatchedGenJet->val);
    }

    // if no match, a nullptr is returned
    return nullptr;
}

/**
 * Helper function to determine if a jet has L1 and/or HLT matches, and to check if those matches pass the configured thresholds.
 * This is typically needed for measuring the trigger efficiency.
 */
dijet::TriggerBitsets dijet::NtupleV2Producer::getTriggerBitsetsForJet(unsigned int jetIndex) {

    dijet::TriggerBitsets triggerBitsets;
    /* explanation of the bitsets in `triggerBitsets`:
     * Bit                                              will be true iff
     * ---                                              -----------------
     * triggerBitsets.hltMatches[hltPathIndex]          jet with index `jetIndex` has a matched HLT object assigned to the HLT path with index `hltPathIndex`
     * triggerBitsets.l1Matches[hltPathIndex]           jet with index `jetIndex` has a matched L1  object assigned to the HLT path with index `hltPathIndex`
     * triggerBitsets.hltPassThresholds[hltPathIndex]   there exists an HLT object matched to the jet with index `jetIndex` whose pT is above the HLT threshold configured for the HLT path with index `hltPathIndex`
     * triggerBitsets.l1PassThresholds[hltPathIndex]    there exists an L1  object matched to the jet with index `jetIndex` whose pT is above the L1  threshold configured for the HLT path with index `hltPathIndex`
     * */

    // -- obtain the collection of trigger objects matched to jet with index `jetIndex`
    const auto& jetMatchedTriggerObjects = this->karmaJetTriggerObjectsMapHandle->find(
        edm::Ref<karma::JetCollection>(this->karmaJetCollectionHandle, jetIndex)
    );

    // if there is at least one trigger object match for the jet
    if (jetMatchedTriggerObjects != this->karmaJetTriggerObjectsMapHandle->end()) {

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
                if (jetMatchedTriggerObject->isHLT() && (jetMatchedTriggerObject->p4.Pt() >= globalCache()->hltThresholds_[idxInConfig])) {
                    triggerBitsets.hltPassThresholds[idxInConfig] = true;
                }
                else if (!jetMatchedTriggerObject->isHLT() && (jetMatchedTriggerObject->p4.Pt() >= globalCache()->l1Thresholds_[idxInConfig])) {
                    triggerBitsets.l1PassThresholds[idxInConfig] = true;
                }
            }
        }
    }
    else {
        ///std::cout << "Event has NO matches for jet " << jetIndex << std::endl;
    }

    return triggerBitsets;
}


/**
 * Helper function to determine if both leading jets have been matched to an HLT trigger path,
 * and to check if those matches pass the configured thresholds. This is typically needed for
 * measuring the trigger efficiency of dijet triggers.
 */
dijet::TriggerBitsets dijet::NtupleV2Producer::getTriggerBitsetsForJetPair(unsigned int jetIndex) {

    dijet::TriggerBitsets triggerBitsets;
    /* explanation of the bitsets in `triggerBitsets`:
     * Bit                                              will be true iff
     * ---                                              -----------------
     * triggerBitsets.hltMatches[hltPathIndex]          jet with indices `jetIndex` and `jetIndex+1` each have a matched HLT object assigned to the HLT path with index `hltPathIndex`
     * triggerBitsets.l1Matches[hltPathIndex]           jet with indices `jetIndex` and `jetIndex+1` each have a matched L1  object assigned to the HLT path with index `hltPathIndex`
     * triggerBitsets.hltPassThresholds[hltPathIndex]   there exists a pair of HLT objects matched to the leading jet pair whose average pT is above the HLT threshold configured for the HLT path with index `hltPathIndex`
     * triggerBitsets.l1PassThresholds[hltPathIndex]    there exists a pair of L1  objects matched to the leading jet pair whose **individual** pTs are both above the L1 threshold configured for the HLT path with index `hltPathIndex`
     *
     * Note the difference between 'hltPassThresholds' and 'l1PassThresholds'!
     * */

    // return immediately if event has less than `jetIndex + 2` jets
    if (this->karmaJetCollectionHandle->size() < jetIndex + 2)
        return triggerBitsets;

    // -- obtain the collection of trigger objects matched to leading jet
    const auto& jet1MatchedTriggerObjects = this->karmaJetTriggerObjectsMapHandle->find(
        edm::Ref<karma::JetCollection>(this->karmaJetCollectionHandle, jetIndex)
    );
    // -- obtain the collection of trigger objects matched to subleading jet
    const auto& jet2MatchedTriggerObjects = this->karmaJetTriggerObjectsMapHandle->find(
        edm::Ref<karma::JetCollection>(this->karmaJetCollectionHandle, jetIndex + 1)
    );

    // if there is at least one trigger object match for each jet
    if ((jet1MatchedTriggerObjects != this->karmaJetTriggerObjectsMapHandle->end()) && (jet2MatchedTriggerObjects != this->karmaJetTriggerObjectsMapHandle->end())) {

        // loop over all pairs trigger objects matched to the leading jet pair
        for (const auto& jet1MatchedTriggerObject : jet1MatchedTriggerObjects->val) {
            for (const auto& jet2MatchedTriggerObject : jet2MatchedTriggerObjects->val) {

                // skip pairs of trigger objects of "mixed" type
                if (jet1MatchedTriggerObject->isHLT() != jet2MatchedTriggerObject->isHLT())
                    continue;

                // set L1 and HLT matching trigger bits if jet pair is assigned the corresponding HLT path
                for (const auto& jet1AssignedPathIdx : jet1MatchedTriggerObject->assignedPathIndices) {
                    // get the index of trigger in analysis config
                    const int jet1AssignedPathIdxInConfig = runCache()->triggerPathsIndicesInConfig_[jet1AssignedPathIdx];

                    // skip unrequested trigger paths
                    if (jet1AssignedPathIdxInConfig < 0)
                        continue;

                    for (const auto& jet2AssignedPathIdx : jet2MatchedTriggerObject->assignedPathIndices) {
                        // get the index of trigger in analysis config
                        const int jet2AssignedPathIdxInConfig = runCache()->triggerPathsIndicesInConfig_[jet2AssignedPathIdx];

                        // skip unrequested trigger paths
                        if (jet2AssignedPathIdxInConfig < 0)
                            continue;

                        // skip if objects not matched to the same trigger path
                        if (jet1AssignedPathIdxInConfig != jet2AssignedPathIdxInConfig)
                            continue;

                        if ((jet1MatchedTriggerObject->isHLT()) && (jet2MatchedTriggerObject->isHLT())) {
                            // both matches are HLT trigger objects
                            triggerBitsets.hltMatches[jet1AssignedPathIdxInConfig] = true;
                        }
                        else if ((!jet1MatchedTriggerObject->isHLT()) && (!jet2MatchedTriggerObject->isHLT())) {
                            // both matches are L1 trigger objects
                            triggerBitsets.l1Matches[jet1AssignedPathIdxInConfig] = true;
                        }
                        // no else, since no pairs of trigger objects of "mixed" type
                    }
                }

                // set L1 and HLT emulation trigger bits if jets (jet pair) pass(es) preset thresholds
                for (size_t idxInConfig = 0; idxInConfig < globalCache()->hltPaths_.size(); ++idxInConfig) {

                    // if HLT objects
                    if (((jet1MatchedTriggerObject->isHLT()) && (jet2MatchedTriggerObject->isHLT()))) {
                        // compute average pt on HLT level
                        const double jet12HLTPtAve = 0.5 * (jet1MatchedTriggerObject->p4.Pt() + jet2MatchedTriggerObject->p4.Pt());
                        // check threshold and set HLT bit
                        if (jet12HLTPtAve >= globalCache()->hltThresholds_[idxInConfig])
                            triggerBitsets.hltPassThresholds[idxInConfig] = true;
                    }
                    // else, if L1 objects
                    else if ((!jet1MatchedTriggerObject->isHLT()) && (!jet2MatchedTriggerObject->isHLT())) {
                        // check thresholds separately for each L1 object
                        if ((jet1MatchedTriggerObject->p4.Pt() >= globalCache()->l1Thresholds_[idxInConfig]) && (jet1MatchedTriggerObject->p4.Pt() >= globalCache()->l1Thresholds_[idxInConfig])) {
                            triggerBitsets.l1PassThresholds[idxInConfig] = true;
                        }
                    }
                }
            }
        }
    }


    return triggerBitsets;
}


//define this as a plug-in
using DijetNtupleV2Producer = dijet::NtupleV2Producer;
DEFINE_FWK_MODULE(DijetNtupleV2Producer);
