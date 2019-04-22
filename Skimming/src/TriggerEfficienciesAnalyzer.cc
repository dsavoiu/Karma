// system include files

#include "HLTrigger/HLTcore/interface/HLTConfigProvider.h"
#include "HLTrigger/HLTcore/interface/HLTPrescaleProvider.h"
#include "L1Trigger/GlobalTriggerAnalyzer/interface/L1GtUtils.h"

#include "Karma/Skimming/interface/TriggerEfficienciesAnalyzer.h"

// -- constructor
karma::TriggerEfficienciesAnalyzer::TriggerEfficienciesAnalyzer(const edm::ParameterSet& config, const karma::GlobalCacheTE* globalCache) :
    m_configPSet(config) {
    // -- process configuration


    // -- declare which collections are consumed and create tokens
    jetCollectionToken = consumes<edm::View<pat::Jet>>(edm::InputTag("slimmedJets"));

    triggerResultsToken = consumes<edm::TriggerResults>(edm::InputTag("TriggerResults", "", "HLT"));
    //triggerPrescalesToken = consumes<pat::PackedTriggerPrescales>(edm::InputTag("patTrigger"));
    triggerObjectsToken = consumes<pat::TriggerObjectStandAloneCollection>(edm::InputTag("selectedPatTrigger"));

    // -- initialize stream scratch spacea

    // copy output histograms to stream (preserving structure)
    //for (std::pair<const std::string, std::shared_ptr<TH1D>>& nameAndHist : globalCache->outputHistograms_) {
    edm::LogInfo("TriggerEfficienciesAnalyzer") << "Copying Histograms to stream...";
    for (const auto& nameAndHist : globalCache->outputHistograms_) {
        edm::LogInfo("TriggerEfficienciesAnalyzer") << "Copying Histogram '" << nameAndHist.first << "' to stream";
        m_triggerEfficiencyHistos.emplace(std::make_pair(nameAndHist.first, std::make_shared<TH1D>(*nameAndHist.second)));  // copy binning, etc.
    }

}


// -- destructor
karma::TriggerEfficienciesAnalyzer::~TriggerEfficienciesAnalyzer() {
}


// -- static member functions

/*static*/ std::unique_ptr<karma::GlobalCacheTE> karma::TriggerEfficienciesAnalyzer::initializeGlobalCache(const edm::ParameterSet& pSet) {
    // -- create the GlobalCache
    return std::unique_ptr<karma::GlobalCacheTE>(new karma::GlobalCacheTE(pSet));
}


/*static*/ std::shared_ptr<karma::RunCacheTE> karma::TriggerEfficienciesAnalyzer::globalBeginRun(const edm::Run& run, const edm::EventSetup& setup, const GlobalCache* globalCache) {
    // -- create the RunCacheTE
    auto runCache = std::make_shared<karma::RunCacheTE>(globalCache->pSet_);

    // -- populate the Run CacheTE
    edm::LogInfo("TriggerEfficienciesAnalyzer") << "Extracting HLT configuration for process name: " << globalCache->hltProcessName_;
    bool hltChanged(true);
    bool hltInitSuccess = globalCache->hltConfigProvider_.init(run, setup, globalCache->hltProcessName_, hltChanged);
    if (hltInitSuccess) {
        if (hltChanged) {
            edm::LogWarning("TriggerEfficienciesAnalyzer") << "HLT Configuration has changed for run " << run.run() ;
        }
    }
    else {
        edm::LogError("TriggerEfficienciesAnalyzer") << " HLT config extraction failure with process name " << globalCache->hltProcessName_;
    }

    // -- get and cache trigger menu information
    //runCache->hltMenuName_ = globalCache->hltConfigProvider_.tableName();
    edm::LogInfo("TriggerEfficienciesAnalyzer") << "Run " << run.run() << " trigger menu: " << globalCache->hltConfigProvider_.tableName();

    // -- get and cache trigger path information
    for (size_t iHLTPath = 0; iHLTPath < globalCache->hltConfigProvider_.size(); ++iHLTPath) {
        // get trigger path information
        const std::string& triggerVersionedName = globalCache->hltConfigProvider_.triggerName(iHLTPath);
        const unsigned int idxInMenu = globalCache->hltConfigProvider_.triggerIndex(triggerVersionedName);
        //const std::vector<std::string>& filterNames = globalCache->hltConfigProvider_.saveTagsModules(idxInMenu);

        // check for the preselection trigger
        if (boost::regex_match(triggerVersionedName, globalCache->hltPreselectionPathRegex_)) {
            edm::LogInfo("TriggerEfficienciesAnalyzer") << "Preselecting events using trigger: " << triggerVersionedName <<", #" << idxInMenu;
            runCache->hltVersionedPreselectionPathName_ = triggerVersionedName;
            runCache->hltVersionedPreselectionPathIndexInMenu_ = idxInMenu;
        }

        // add triggers that match the configured path regexes
        for (const auto& nameAndRegex : globalCache->hltPathRegexes_) {
            if (boost::regex_match(triggerVersionedName, nameAndRegex.second)) {
                edm::LogInfo("TriggerEfficienciesAnalyzer") << "Will measure efficiency for trigger: " << nameAndRegex.first << " (" << triggerVersionedName << ", #" << idxInMenu << ")";
                runCache->hltVersionedPathNames_[nameAndRegex.first] = triggerVersionedName;
                runCache->hltPathIndicesInMenu_[nameAndRegex.first] = idxInMenu;
                break;  // possible other matches (should not happen) ignored
            }
        }
    }

    return runCache;
}


/*static*/ std::shared_ptr<karma::RunSummaryCacheTE> karma::TriggerEfficienciesAnalyzer::globalBeginRunSummary(const edm::Run& run, const edm::EventSetup& setup, const RunContext* runContext) {
    // -- create the RunSummaryCacheTE

    auto runSummaryCache = std::make_shared<karma::RunSummaryCacheTE>(runContext->global()->pSet_);
    //return runContext->globalCache()->makeHist1D(std::to_string(run.runNumber()), "a", runContext->global()->triggerEfficiencyBinning_);
    return runSummaryCache;
};


void karma::TriggerEfficienciesAnalyzer::endRunSummary(const edm::Run& run, const edm::EventSetup& setup, karma::RunSummaryCacheTE* runSummaryCache) const {
    // NOOP
};


/*static*/ void karma::TriggerEfficienciesAnalyzer::globalEndRunSummary(const edm::Run& run, const edm::EventSetup& setup, const RunContext* runContext, karma::RunSummaryCacheTE* runSummaryCache) {
    // NOOP
};

void karma::TriggerEfficienciesAnalyzer::endStream() {
    edm::LogInfo("TriggerEfficienciesAnalyzer") << "[" << std::hex << this << std::dec << "] End Stream";
    // write accumulated info on each stream to file
    edm::LogInfo("TriggerEfficienciesAnalyzer") << "Adding together histograms from stream.";
    for (const auto& nameAndHist : m_triggerEfficiencyHistos) {
        globalCache()->addToHist1D(nameAndHist.first, nameAndHist.second);
    }
}

/*static*/ void karma::TriggerEfficienciesAnalyzer::globalEndJob(karma::GlobalCacheTE* globalCache) {
    globalCache->writeAllAndCloseFile();
}

// -- member functions

void karma::TriggerEfficienciesAnalyzer::beginStream(edm::StreamID streamID) {
    edm::LogInfo("TriggerEfficienciesAnalyzer") << "[" << std::hex << this << std::dec << "] Begin Stream with ID = " << streamID.value();
}

void karma::TriggerEfficienciesAnalyzer::analyze(const edm::Event& event, const edm::EventSetup& setup) {


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

    // skip event if it is not accepted by the preselection trigger path
    if (!this->triggerResultsHandle->accept(runCache()->hltVersionedPreselectionPathIndexInMenu_)) return;
    edm::LogInfo("TriggerEfficienciesAnalyzer") << "Event " << event.id().event() << " passed preselection";

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

    // -- second pass: identify and extract L1 and HLT jets for each reco jet

    for (size_t iJet = 0; iJet < nRecoJets; ++iJet) {

        // ignore reco jets without HLT and L1 matches
        if (!(hltJets[iJet] && l1Jets[iJet])) continue;


        double recoJetPt = this->jetCollectionHandle->at(iJet).pt();

        // every reco jet with HLT and L1 matches counts as reference
        m_triggerEfficiencyHistos["Reference"]->Fill(recoJetPt);

        // go through all 'probe' trigger paths
        for (const auto& pathNameAndVersionedName : runCache()->hltVersionedPathNames_) {
            // check if matched trigger objects pass all filters

            /* // -- old filter-based implementation
            // retrieve HLT filter specifications for path
            const std::vector<std::pair<std::string, double>>& hltFilterSpecsForPath = globalCache()->hltPathFiltersThresholds_.at(pathNameAndVersionedName.first);
            size_t nHLTFiltersMatched = 0;
            for (const auto& filterNameAndThreshold : hltFilterSpecsForPath) {
                //~ std::cout << "Does HLT pass filter '" << filterNameAndThreshold.first << "'?";
                for (size_t iObjectFilter = 0; iObjectFilter < hltJets[iJet]->filterLabels().size(); ++iObjectFilter) {
                    const std::string& objectFilterName = hltJets[iJet]->filterLabels()[iObjectFilter];
                    //~ std::cout << objectFilterName;
                    if ((objectFilterName == filterNameAndThreshold.first)) {
                        // object filter name matched
                        ++nHLTFiltersMatched;
                        //~ std::cout << " -> yes!" << std::endl;
                        break;
                    }
                    //~ std::cout << " -> no" << std::endl;
                }
            }
            // skip if HLT didn't pass
            if ((nHLTFiltersMatched == 0) || (nHLTFiltersMatched != hltFilterSpecsForPath.size())) continue;

            const std::vector<std::pair<std::string, double>>& l1FilterSpecsForPath = globalCache()->hltPathL1FiltersThresholds_.at(pathNameAndVersionedName.first);
            size_t nL1FiltersMatched = 0;
            for (const auto& filterNameAndThreshold : l1FilterSpecsForPath) {
                //~ std::cout << "Does L1 pass filter '" << filterNameAndThreshold.first << "'?";
                for (size_t iObjectFilter = 0; iObjectFilter < l1Jets[iJet]->filterLabels().size(); ++iObjectFilter) {
                    const std::string& objectFilterName = l1Jets[iJet]->filterLabels()[iObjectFilter];
                    //~ std::cout << objectFilterName;
                    if ((objectFilterName == filterNameAndThreshold.first)) {
                        // object filter name matched
                        ++nL1FiltersMatched;
                        //~ std::cout << " -> yes!" << std::endl;
                        break;
                    }
                    //~ std::cout << " -> no" << std::endl;
                }
            }
            // skip if L1 didn't pass
            if ((nL1FiltersMatched == 0) || (nL1FiltersMatched != l1FilterSpecsForPath.size())) continue; */

            // -- new threshold-based implementation
            // retrieve HLT filter specifications for path
            const std::vector<std::pair<std::string, double>>& hltFilterSpecsForPath = globalCache()->hltPathFiltersThresholds_.at(pathNameAndVersionedName.first);
            size_t nHLTFiltersMatched = 0;
            for (const auto& filterNameAndThreshold : hltFilterSpecsForPath) {
                for (size_t iObjectFilter = 0; iObjectFilter < hltJets[iJet]->filterLabels().size(); ++iObjectFilter) {
                    if ((hltJets[iJet]->pt() >= filterNameAndThreshold.second)) {
                        ++nHLTFiltersMatched;
                        break;
                    }
                }
            }
            // skip if HLT didn't pass
            if (nHLTFiltersMatched != hltFilterSpecsForPath.size()) continue;

            const std::vector<std::pair<std::string, double>>& l1FilterSpecsForPath = globalCache()->hltPathL1FiltersThresholds_.at(pathNameAndVersionedName.first);
            size_t nL1FiltersMatched = 0;
            for (const auto& filterNameAndThreshold : l1FilterSpecsForPath) {
                for (size_t iObjectFilter = 0; iObjectFilter < l1Jets[iJet]->filterLabels().size(); ++iObjectFilter) {
                    if ((l1Jets[iJet]->pt() >= filterNameAndThreshold.second)) {
                        ++nL1FiltersMatched;
                        break;
                    }
                }
            }
            // skip if L1 didn't pass
            if (nL1FiltersMatched != l1FilterSpecsForPath.size()) continue;


            // if we got this far, the jet would have pased the trigger path -> Fill histogram
            m_triggerEfficiencyHistos[pathNameAndVersionedName.first]->Fill(recoJetPt);
        }  // HLT paths
    }  // reco jets
}


void karma::TriggerEfficienciesAnalyzer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    // The following says we do not know what parameters are allowed so do no validation
    // Please change this to state exactly what you do use, even if it is no parameters
    edm::ParameterSetDescription desc;
    desc.setUnknown();
    descriptions.addDefault(desc);
}


//define this as a plug-in
using karma::TriggerEfficienciesAnalyzer;
DEFINE_FWK_MODULE(TriggerEfficienciesAnalyzer);
