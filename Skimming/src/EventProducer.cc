// system include files
#include <iostream>

#include "HLTrigger/HLTcore/interface/HLTConfigProvider.h"
#include "HLTrigger/HLTcore/interface/HLTPrescaleProvider.h"
#include "L1Trigger/GlobalTriggerAnalyzer/interface/L1GtUtils.h"

#include "Karma/Skimming/interface/EventProducer.h"

// -- constructor
karma::EventProducer::EventProducer(const edm::ParameterSet& config, const karma::GlobalCache* globalCache) : m_configPSet(config) {
    // -- register products
    produces<karma::Event>();
    produces<karma::Lumi, edm::InLumi>();
    produces<karma::Run, edm::InRun>();

    // -- process configuration

    // -- declare which collections are consumed and create tokens
    pileupDensityToken = consumes<double>(m_configPSet.getParameter<edm::InputTag>("pileupDensitySrc"));
    pileupSummaryInfosToken = consumes<edm::View<PileupSummaryInfo>>(m_configPSet.getParameter<edm::InputTag>("pileupSummaryInfoSrc"));
    triggerResultsToken = consumes<edm::TriggerResults>(m_configPSet.getParameter<edm::InputTag>("triggerResultsSrc"));
    //triggerPrescalesToken = consumes<pat::PackedTriggerPrescales>(m_configPSet.getParameter<edm::InputTag>("triggerPrescalesSrc"));
    primaryVerticesToken = consumes<edm::View<reco::Vertex>>(m_configPSet.getParameter<edm::InputTag>("primaryVerticesSrc"));
    goodPrimaryVerticesToken = consumes<edm::View<reco::Vertex>>(m_configPSet.getParameter<edm::InputTag>("goodPrimaryVerticesSrc"));

    // due to CMSSW constraints, need to have one HLTPrescaleProvider per EDProducer instance
    m_hltPrescaleProvider = std::unique_ptr<HLTPrescaleProvider>(
        new HLTPrescaleProvider(
            m_configPSet.getParameter<edm::ParameterSet>("hltPrescaleProvider"),
            this->consumesCollector(),
            *this
        )
    );
}


// -- destructor
karma::EventProducer::~EventProducer() {
}


// -- static member functions

/*static*/ std::unique_ptr<karma::GlobalCache> karma::EventProducer::initializeGlobalCache(const edm::ParameterSet& pSet) {
    // -- create the GlobalCache
    return std::unique_ptr<karma::GlobalCache>(new karma::GlobalCache(pSet));
}


/*static*/ std::shared_ptr<karma::RunCache> karma::EventProducer::globalBeginRun(const edm::Run& run, const edm::EventSetup& setup, const karma::EventProducer::GlobalCache* globalCache) {
    // -- create the RunCache
    auto runCache = std::make_shared<karma::RunCache>(globalCache->pSet_);

    // -- populate the Run Cache
    std::cout << "Extracting HLT configuration for process name: " << globalCache->hltProcessName_ << std::endl;
    bool hltChanged(true);
    bool hltInitSuccess = globalCache->hltConfigProvider_.init(run, setup, globalCache->hltProcessName_, hltChanged);
    if (hltInitSuccess) {
        if (hltChanged) {
            std::cout << "HLT Configuration has changed!" << std::endl;
        }
    }
    else {
        edm::LogError("EventProducer") << " HLT config extraction failure with process name " << globalCache->hltProcessName_;
    }

    // -- get trigger menu information
    runCache->hltMenuName_ = globalCache->hltConfigProvider_.tableName();

    // -- get trigger path information
    //    (i.e. matching trigger path names and the indices indicating
    //    their position in the trigger menu)
    karma::HLTPathInfos* hltPathInfos = &(runCache->hltPathInfos_);
    size_t filtersNextStartIndex = 0;

    for (size_t iHLTPath = 0; iHLTPath < globalCache->hltConfigProvider_.size(); ++iHLTPath) {
        // get trigger path information
        const std::string& name = globalCache->hltConfigProvider_.triggerName(iHLTPath);
        size_t idxInMenu = globalCache->hltConfigProvider_.triggerIndex(name);
        const std::vector<std::string>& filterNames = globalCache->hltConfigProvider_.saveTagsModules(idxInMenu);

        // skip triggers that don't match the configured path regexes
        bool regexMatch = false;
        std::cout << "Match('" << name << "')? -> ";
        for (const auto& regex : globalCache->hltPathRegexes_) {
            if (boost::regex_search(name, regex)) {
                regexMatch = true;
                std::cout << " yes ";
                break;
            }
            else std::cout << " no ";
        }
        std::cout << std::endl;

        // only save interesting trigger paths
        if (regexMatch) {
            hltPathInfos->emplace_back(
                /*name = */name,
                /*indexInMenu = */idxInMenu,
                /*filtersStartIndex = */filtersNextStartIndex,
                /*filterNames = */filterNames
            );
        }

        // keep track of the index at which filters start for each HLT path
        filtersNextStartIndex += filterNames.size();
    }

    std::cout << "Selected HLT Paths:" << std::endl;
    for (const auto& hltPathInfo : (*hltPathInfos)) {
        std::cout << "  name: " << hltPathInfo.name_ << std::endl;
        std::cout << "  indexInMenu: " << hltPathInfo.indexInMenu_ << std::endl;
        std::cout << "  numFilters: " << hltPathInfo.numFilters() << std::endl;
        for (size_t iFilter = 0; iFilter < hltPathInfo.numFilters(); ++iFilter) {
            std::cout << "    Filter #" << iFilter << " (#" << hltPathInfo.filtersStartIndex_ + iFilter << "): " << hltPathInfo.filterNames_[iFilter] << std::endl;
        }
    }

    return runCache;
}

/*static*/ std::shared_ptr<karma::LumiCache> karma::EventProducer::globalBeginLuminosityBlock(const edm::LuminosityBlock& lumi, const edm::EventSetup& setup, const karma::EventProducer::RunContext* runContext) {
    // -- create the LumiCache
    auto lumiCache = std::make_shared<karma::LumiCache>(runContext->global()->pSet_);


    // -- populate the LumiCache
    // nothing to do

    return lumiCache;
}

/*static*/ void karma::EventProducer::globalBeginRunProduce(edm::Run& run, const edm::EventSetup& setup, const RunContext* runContext) {
    std::unique_ptr<karma::Run> karmaRun(new karma::Run());

    // -- populate run data and fill Run tree
    karmaRun->run = run.run();

    karmaRun->triggerMenuName = runContext->run()->hltMenuName_;
    karmaRun->triggerPathInfos = runContext->run()->hltPathInfos_;

    run.put(std::move(karmaRun));
}

/*static*/ void karma::EventProducer::globalBeginLuminosityBlockProduce(edm::LuminosityBlock& lumi, const edm::EventSetup& setup, const LuminosityBlockContext* lumiContext) {
    #if CMSSW_MAJOR_VERSION > 8
        std::unique_ptr<karma::Lumi> karmaLumi(new karma::Lumi()); // -> use unique_ptr
    #else
        // bug in CMSSW8: upstream code missing "std::move" for unique_ptr
        std::auto_ptr<karma::Lumi> karmaLumi(new karma::Lumi());  //  -> substitute auto_ptr
    #endif

    // -- populate luminosity block data and fill Lumi tree
    karmaLumi->run = lumi.run();
    karmaLumi->lumi = lumi.luminosityBlock();

    lumi.put(std::move(karmaLumi));
}


// -- member functions

void karma::EventProducer::produce(edm::Event& event, const edm::EventSetup& setup) {
    //std::unique_ptr<karma::Event> karmaEvent(new karma::Event());
    std::unique_ptr<karma::Event> outputEvent(new karma::Event());

    // -- get object collections for event
    bool obtained = true;
    // pileup density
    obtained &= event.getByToken(this->pileupDensityToken, this->pileupDensityHandle);
    // trigger results and prescales
    obtained &= event.getByToken(this->triggerResultsToken, this->triggerResultsHandle);
    //obtained &= event.getByToken(this->triggerPrescalesToken, this->triggerPrescalesHandle);
    // primary vertices
    obtained &= event.getByToken(this->primaryVerticesToken, this->primaryVerticesHandle);
    obtained &= event.getByToken(this->goodPrimaryVerticesToken, this->goodPrimaryVerticesHandle);

    // MC-specific products
    if (!globalCache()->isData_) {
        obtained &= event.getByToken(this->pileupSummaryInfosToken, this->pileupSummaryInfosHandle);
    }

    assert(obtained);  // raise if one collection could not be obtained

    // -- populate outputs

    // pileup density (rho)
    outputEvent->rho = *this->pileupDensityHandle;
    outputEvent->npv = this->primaryVerticesHandle->size();
    outputEvent->npvGood = this->goodPrimaryVerticesHandle->size();

    // pileup summary informations (nPU, nPUTrue, etc.)
    if (!globalCache()->isData_) {
        for (const auto& pileupSummaryInfo : (*this->pileupSummaryInfosHandle)) {
            if (pileupSummaryInfo.getBunchCrossing() == 0) {
                outputEvent->nPU = pileupSummaryInfo.getPU_NumInteractions();
                outputEvent->nPUTrue = pileupSummaryInfo.getTrueNumInteractions();
            }
        }
    }

    // -- trigger decisions (bits) and prescales
    bool hltChanged(true);
    // must be called on each event, since there is no guarantee that
    // the HLTPrescaleProvider has been re-initialized correctly on new run transition
    bool hltInitSuccess = m_hltPrescaleProvider->init(event.getRun(), setup, globalCache()->hltProcessName_, hltChanged);
    assert(hltInitSuccess);

    const size_t numSelectedHLTPaths = runCache()->hltPathInfos_.size();
    outputEvent->hltBits.resize(numSelectedHLTPaths);
    outputEvent->triggerPathHLTPrescales.resize(numSelectedHLTPaths);
    outputEvent->triggerPathL1Prescales.resize(numSelectedHLTPaths);
    for (size_t iPath = 0; iPath < numSelectedHLTPaths; ++iPath) {
        // need the original index of the path in the trigger menu to obtain trigger decision
        const int& triggerIndex = runCache()->hltPathInfos_[iPath].indexInMenu_;
        // need the full trigger name to obtain trigger prescale
        const std::string& triggerName = runCache()->hltPathInfos_[iPath].name_;
        const std::pair<int, int> l1AndHLTPrescales = m_hltPrescaleProvider->prescaleValues(event, setup, triggerName);

        outputEvent->hltBits[iPath] = this->triggerResultsHandle->accept(triggerIndex);
        outputEvent->triggerPathL1Prescales[iPath] = l1AndHLTPrescales.first;
        outputEvent->triggerPathHLTPrescales[iPath] = l1AndHLTPrescales.second;
    }

    // move outputs to event tree
    event.put(std::move(outputEvent));
}


void karma::EventProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    // The following says we do not know what parameters are allowed so do no validation
    // Please change this to state exactly what you do use, even if it is no parameters
    edm::ParameterSetDescription desc;
    desc.setUnknown();
    descriptions.addDefault(desc);
}


//define this as a plug-in
using karma::EventProducer;
DEFINE_FWK_MODULE(EventProducer);
