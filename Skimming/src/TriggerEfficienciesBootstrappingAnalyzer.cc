// system include files

#include "HLTrigger/HLTcore/interface/HLTConfigProvider.h"
#include "HLTrigger/HLTcore/interface/HLTPrescaleProvider.h"
#include "L1Trigger/GlobalTriggerAnalyzer/interface/L1GtUtils.h"

#include "DijetAnalysis/Skimming/interface/TriggerEfficienciesBootstrappingAnalyzer.h"

// -- constructor
dijet::TriggerEfficienciesBootstrappingAnalyzer::TriggerEfficienciesBootstrappingAnalyzer(const edm::ParameterSet& config, const dijet::GlobalCacheTEB* globalCache) :
    m_configPSet(config) {
    // -- process configuration


    // -- declare which collections are consumed and create tokens
    jetCollectionToken = consumes<edm::View<pat::Jet>>(config.getParameter<edm::InputTag>("jetCollectionSrc"));
    triggerResultsToken = consumes<edm::TriggerResults>(edm::InputTag("TriggerResults", "", "HLT"));
    triggerObjectsToken = consumes<pat::TriggerObjectStandAloneCollection>(edm::InputTag("selectedPatTrigger"));

    // -- initialize stream scratch spacea

    // copy output histograms to stream (preserving structure)
    edm::LogInfo("TriggerEfficienciesBootstrappingAnalyzer") << "Copying Histograms to stream...";
    for (const auto& nameAndHist : globalCache->outputHistograms_) {
        edm::LogInfo("TriggerEfficienciesBootstrappingAnalyzer") << "Copying Histogram '" << nameAndHist.first << "' to stream";
        m_triggerEfficiencyHistos.emplace(std::make_pair(nameAndHist.first, std::make_shared<TH1D>(*nameAndHist.second)));  // copy binning, etc.
    }

}


// -- destructor
dijet::TriggerEfficienciesBootstrappingAnalyzer::~TriggerEfficienciesBootstrappingAnalyzer() {
}


// -- static member functions

/*static*/ std::unique_ptr<dijet::GlobalCacheTEB> dijet::TriggerEfficienciesBootstrappingAnalyzer::initializeGlobalCache(const edm::ParameterSet& pSet) {
    // -- create the GlobalCache
    return std::unique_ptr<dijet::GlobalCacheTEB>(new dijet::GlobalCacheTEB(pSet));
}


/*static*/ std::shared_ptr<dijet::RunCacheTEB> dijet::TriggerEfficienciesBootstrappingAnalyzer::globalBeginRun(const edm::Run& run, const edm::EventSetup& setup, const GlobalCache* globalCache) {
    // -- create the RunCacheTEB
    auto runCache = std::make_shared<dijet::RunCacheTEB>(globalCache->pSet_);

    // -- populate the Run CacheTE
    edm::LogInfo("TriggerEfficienciesBootstrappingAnalyzer") << "Extracting HLT configuration for process name: " << globalCache->hltProcessName_;
    bool hltChanged(true);
    bool hltInitSuccess = globalCache->hltConfigProvider_.init(run, setup, globalCache->hltProcessName_, hltChanged);
    if (hltInitSuccess) {
        if (hltChanged) {
            edm::LogWarning("TriggerEfficienciesBootstrappingAnalyzer") << "HLT Configuration has changed for run " << run.run() ;
        }
    }
    else {
        edm::LogError("TriggerEfficienciesBootstrappingAnalyzer") << " HLT config extraction failure with process name " << globalCache->hltProcessName_;
    }

    // -- get and cache trigger menu information
    //runCache->hltMenuName_ = globalCache->hltConfigProvider_.tableName();
    edm::LogInfo("TriggerEfficienciesBootstrappingAnalyzer") << "Run " << run.run() << " trigger menu: " << globalCache->hltConfigProvider_.tableName();

    // -- get and cache trigger path information
    for (size_t iHLTPath = 0; iHLTPath < globalCache->hltConfigProvider_.size(); ++iHLTPath) {
        // get trigger path information
        const std::string& triggerVersionedName = globalCache->hltConfigProvider_.triggerName(iHLTPath);
        const unsigned int idxInMenu = globalCache->hltConfigProvider_.triggerIndex(triggerVersionedName);

        // add triggers that match the configured path regexes
        for (const auto& nameAndRegex : globalCache->hltPathRegexes_) {
            if (boost::regex_match(triggerVersionedName, nameAndRegex.second)) {
                edm::LogInfo("TriggerEfficienciesBootstrappingAnalyzer") << "Will measure efficiency for trigger: " << nameAndRegex.first << " (" << triggerVersionedName << ", #" << idxInMenu << ")";
                runCache->hltVersionedPathNames_[nameAndRegex.first] = triggerVersionedName;
                runCache->hltPathIndicesInMenu_[nameAndRegex.first] = idxInMenu;
                break;  // possible other matches (should not happen) ignored
            }
        }

        // add index of triggers that match the configured 'tag' path regexes
        for (const auto& tagNameAndRegex : globalCache->hltTagPathRegexes_) {
            // if tag path is already added (e.g. as probe for another path), do not add again
            if (runCache->hltPathIndicesInMenu_.find(tagNameAndRegex.first) != runCache->hltPathIndicesInMenu_.end()) {
                continue;
            }
            if (boost::regex_match(triggerVersionedName, tagNameAndRegex.second)) {
                edm::LogInfo("TriggerEfficienciesBootstrappingAnalyzer") << "Adding tag trigger to RunCache: " << tagNameAndRegex.first << " (" << triggerVersionedName << ", #" << idxInMenu << ")";
                runCache->hltPathIndicesInMenu_[tagNameAndRegex.first] = idxInMenu;
                break;  // possible other matches (should not happen) ignored
            }
        }
    }

    return runCache;
}

void dijet::TriggerEfficienciesBootstrappingAnalyzer::endStream() {
    edm::LogInfo("TriggerEfficienciesBootstrappingAnalyzer") << "[" << std::hex << this << std::dec << "] End Stream";
    // write accumulated info on each stream to file
    edm::LogInfo("TriggerEfficienciesBootstrappingAnalyzer") << "Adding together histograms from stream.";
    for (const auto& nameAndHist : m_triggerEfficiencyHistos) {
        globalCache()->addToHist1D(nameAndHist.first, nameAndHist.second);
    }
}

/*static*/ void dijet::TriggerEfficienciesBootstrappingAnalyzer::globalEndJob(dijet::GlobalCacheTEB* globalCache) {
    globalCache->writeAllAndCloseFile();
}

// -- member functions

void dijet::TriggerEfficienciesBootstrappingAnalyzer::beginStream(edm::StreamID streamID) {
    edm::LogInfo("TriggerEfficienciesBootstrappingAnalyzer") << "[" << std::hex << this << std::dec << "] Begin Stream with ID = " << streamID.value();
}

void dijet::TriggerEfficienciesBootstrappingAnalyzer::analyze(const edm::Event& event, const edm::EventSetup& setup) {


    // -- get object collections for event
    bool obtained = true;
    // jets
    obtained &= event.getByToken(this->jetCollectionToken, this->jetCollectionHandle);
    // trigger results and prescales
    obtained &= event.getByToken(this->triggerResultsToken, this->triggerResultsHandle);
    //obtained &= event.getByToken(this->triggerPrescalesToken, this->triggerPrescalesHandle);
    // trigger objects
    obtained &= event.getByToken(this->triggerObjectsToken, this->triggerObjectsHandle);

    assert(obtained);  // raise if one collection could not be obtained

    // skip event if there are no reco jets
    size_t nRecoJets = this->jetCollectionHandle->size();
    if (nRecoJets == 0) return;

    // -- first pass: identify and extract L1 and HLT jets for each reco jet
    std::vector<pat::TriggerObjectStandAlone*> hltJets(nRecoJets, nullptr);
    std::vector<pat::TriggerObjectStandAlone*> l1Jets(nRecoJets, nullptr);
    for (size_t iJet = 0; iJet < nRecoJets; ++iJet) {
        for (size_t iTO = 0; iTO < this->triggerObjectsHandle->size(); ++iTO) {
            const pat::TriggerObjectStandAlone& triggerObject = this->triggerObjectsHandle->at(iTO);
            // -- skip trigger objects that are not deltaR-matched to the reco jet
            if (ROOT::Math::VectorUtil::DeltaR(triggerObject.p4(), this->jetCollectionHandle->at(iJet).p4()) > 0.2) {
                continue;
            }

            // -- determine object type and fill pointer accordingly
            for (const auto& objType : triggerObject.triggerObjectTypes()) {
                // HLT Jet object types
                if (!hltJets[iJet] && ((objType == 85) || (objType == 86))) {
                    //hltJets[iJet] = &this->triggerObjectsHandle->at(iTO);
                    hltJets[iJet] = const_cast<pat::TriggerObjectStandAlone*>(&this->triggerObjectsHandle->at(iTO));
                    break;
                }
                // L1 Jet object types
                else if (!l1Jets[iJet] && ((objType == -99) || (objType == -84) || (objType == -85) || (objType == -86))) {
                    //l1Jets[iJet] = &this->triggerObjectsHandle->at(iTO);
                    l1Jets[iJet] = const_cast<pat::TriggerObjectStandAlone*>(&this->triggerObjectsHandle->at(iTO));
                    break;
                }
            }
        }
    }

    // -- second pass: count reference and probe jets by reco. pT

    for (size_t iJet = 0; iJet < nRecoJets; ++iJet) {

        // ignore reco jets without HLT and L1 matches
        if (!(hltJets[iJet] && l1Jets[iJet])) continue;


        double recoJetPt = this->jetCollectionHandle->at(iJet).pt();

        // go through all 'probe' trigger paths
        for (const auto& pathNameAndVersionedName : runCache()->hltVersionedPathNames_) {

            const std::string& tagPath = globalCache()->hltPathTagPaths_.at(pathNameAndVersionedName.first);
            const int& tagPathIndexInMenu = runCache()->hltPathIndicesInMenu_.at(tagPath);
            const bool tagDecision = this->triggerResultsHandle->accept(tagPathIndexInMenu);

            // check if 'tag' trigger path fired
            if (tagDecision) {

                // every reco jet with HLT and L1 matches counts as reference
                const std::string& tagPathHistogramName = globalCache()->hltPathReferenceHistogramNames_.at(pathNameAndVersionedName.first);
                m_triggerEfficiencyHistos[tagPathHistogramName]->Fill(recoJetPt);

                // if jet would have pased the 'probe' trigger path -> fill histogram
                if ( (hltJets[iJet]->pt() >= globalCache()->hltPathHLTThresholds_.at(pathNameAndVersionedName.first)) &&
                     (l1Jets[iJet]->pt() >= globalCache()->hltPathL1Thresholds_.at(pathNameAndVersionedName.first))) {
                    //std::cout << " probe passed!" << std::endl;
                    m_triggerEfficiencyHistos[pathNameAndVersionedName.first]->Fill(recoJetPt);
                } // if passThreshold

            } // if tagDecision

        }  // HLT paths

    }  // reco jets

}


void dijet::TriggerEfficienciesBootstrappingAnalyzer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    // The following says we do not know what parameters are allowed so do no validation
    // Please change this to state exactly what you do use, even if it is no parameters
    edm::ParameterSetDescription desc;
    desc.setUnknown();
    descriptions.addDefault(desc);
}


//define this as a plug-in
using dijet::TriggerEfficienciesBootstrappingAnalyzer;
DEFINE_FWK_MODULE(TriggerEfficienciesBootstrappingAnalyzer);
