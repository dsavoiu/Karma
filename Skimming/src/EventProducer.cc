// system include files
#include <iostream>

#include "HLTrigger/HLTcore/interface/HLTConfigProvider.h"
#include "HLTrigger/HLTcore/interface/HLTPrescaleProvider.h"
#include "L1Trigger/GlobalTriggerAnalyzer/interface/L1GtUtils.h"

#include "DijetAnalysis/Skimming/interface/EventProducer.h"

// -- constructor
dijet::EventProducer::EventProducer(const edm::ParameterSet& config, const dijet::GlobalCache* globalCache) : m_configPSet(config) {
    // -- register products
    produces<dijet::Event>();
    produces<dijet::Lumi, edm::InLumi>();
    produces<dijet::Run, edm::InRun>();

    // -- process configuration

    // -- declare which collections are consumed and create tokens
    pileupDensityToken = consumes<double>(m_configPSet.getParameter<edm::InputTag>("pileupDensitySrc"));
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
dijet::EventProducer::~EventProducer() {
}


// -- static member functions

/*static*/ std::unique_ptr<dijet::GlobalCache> dijet::EventProducer::initializeGlobalCache(const edm::ParameterSet& pSet) {
    // -- create the GlobalCache
    return std::unique_ptr<dijet::GlobalCache>(new dijet::GlobalCache(pSet));
}


/*static*/ std::shared_ptr<dijet::RunCache> dijet::EventProducer::globalBeginRun(const edm::Run& run, const edm::EventSetup& setup, const dijet::EventProducer::GlobalCache* globalCache) {
    // -- create the RunCache
    auto runCache = std::make_shared<dijet::RunCache>(globalCache->pSet_);

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
    dijet::HLTPathInfos* hltPathInfos = &(runCache->hltPathInfos_);
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

/*static*/ std::shared_ptr<dijet::LumiCache> dijet::EventProducer::globalBeginLuminosityBlock(const edm::LuminosityBlock& lumi, const edm::EventSetup& setup, const dijet::EventProducer::RunContext* runContext) {
    // -- create the LumiCache
    auto lumiCache = std::make_shared<dijet::LumiCache>(runContext->global()->pSet_);


    // -- populate the LumiCache
    // nothing to do

    return lumiCache;
}

/*static*/ void dijet::EventProducer::globalBeginRunProduce(edm::Run& run, const edm::EventSetup& setup, const RunContext* runContext) {
    std::unique_ptr<dijet::Run> dijetRun(new dijet::Run());

    // -- populate run data and fill Run tree
    dijetRun->run = run.run();

    dijetRun->triggerMenuName = runContext->run()->hltMenuName_;
    dijetRun->triggerPathInfos = runContext->run()->hltPathInfos_;

    run.put(std::move(dijetRun));
}

/*static*/ void dijet::EventProducer::globalBeginLuminosityBlockProduce(edm::LuminosityBlock& lumi, const edm::EventSetup& setup, const LuminosityBlockContext* lumiContext) {
    #if CMSSW_MAJOR_VERSION > 8
        std::unique_ptr<dijet::Lumi> dijetLumi(new dijet::Lumi()); // -> use unique_ptr
    #else
        // bug in CMSSW8: upstream code missing "std::move" for unique_ptr
        std::auto_ptr<dijet::Lumi> dijetLumi(new dijet::Lumi());  //  -> substitute auto_ptr
    #endif

    // -- populate luminosity block data and fill Lumi tree
    dijetLumi->run = lumi.run();
    dijetLumi->lumi = lumi.luminosityBlock();

    lumi.put(std::move(dijetLumi));
}


// -- member functions

void dijet::EventProducer::produce(edm::Event& event, const edm::EventSetup& setup) {
    //std::unique_ptr<dijet::Event> dijetEvent(new dijet::Event());
    std::unique_ptr<dijet::Event> outputEvent(new dijet::Event());

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

    assert(obtained);  // raise if one collection could not be obtained

    // -- populate outputs


    // pileup density (rho)
    outputEvent->rho = *this->pileupDensityHandle;
    outputEvent->npv = this->primaryVerticesHandle->size();
    outputEvent->npvGood = this->goodPrimaryVerticesHandle->size();

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


void dijet::EventProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    // The following says we do not know what parameters are allowed so do no validation
    // Please change this to state exactly what you do use, even if it is no parameters
    edm::ParameterSetDescription desc;
    desc.setUnknown();
    descriptions.addDefault(desc);
}


//define this as a plug-in
using dijet::EventProducer;
DEFINE_FWK_MODULE(EventProducer);
