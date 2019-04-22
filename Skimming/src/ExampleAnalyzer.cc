#include "Karma/Skimming/interface/ExampleAnalyzer.h"

// -- constructor
karma::ExampleAnalyzer::ExampleAnalyzer(const edm::ParameterSet& config, const karma::ExampleGlobalCache* globalCache) :
    m_configPSet(config) {
    // -- process configuration

    // -- declare which collections are consumed and create tokens
    jetCollectionToken = consumes<edm::View<pat::Jet>>(edm::InputTag("slimmedJets"));

    // -- initialize stream scratch space
}


// -- destructor
karma::ExampleAnalyzer::~ExampleAnalyzer() {
}


// -- static member functions

/*static*/ std::unique_ptr<karma::ExampleGlobalCache> karma::ExampleAnalyzer::initializeGlobalCache(const edm::ParameterSet& pSet) {
    // -- create the GlobalCache
    return std::unique_ptr<karma::ExampleGlobalCache>(new karma::ExampleGlobalCache(pSet));
}


/*static*/ std::shared_ptr<karma::ExampleRunCache> karma::ExampleAnalyzer::globalBeginRun(const edm::Run& run, const edm::EventSetup& setup, const GlobalCache* globalCache) {
    // -- create the ExampleRunCache
    auto runCache = std::make_shared<karma::ExampleRunCache>(globalCache->pSet_);

    // -- user code here: initialize the cache


    return runCache;
}


/*static*/ std::shared_ptr<karma::ExampleRunSummaryCache> karma::ExampleAnalyzer::globalBeginRunSummary(const edm::Run& run, const edm::EventSetup& setup, const RunContext* runContext) {
    // -- create the ExampleRunSummaryCache

    auto runSummaryCache = std::make_shared<karma::ExampleRunSummaryCache>(runContext->global()->pSet_);

    // -- user code here: initialize the cache


    return runSummaryCache;
};


void karma::ExampleAnalyzer::endRunSummary(const edm::Run& run, const edm::EventSetup& setup, karma::ExampleRunSummaryCache* runSummaryCache) const {
    // framework guarantee: is never called by two streams simultaenously

    // -- user code here: perform any per-stream wrap-up actions on the run-summary cache

};


/*static*/ void karma::ExampleAnalyzer::globalEndRunSummary(const edm::Run& run, const edm::EventSetup& setup, const RunContext* runContext, karma::ExampleRunSummaryCache* runSummaryCache) {

    // -- user code here: perform any global wrap-up actions on the run-summary cache

};

void karma::ExampleAnalyzer::endStream() {
    
    // -- user code here: perform any end-of-stream wrap-up actions
    //globalCache()->addToHist(histName, streamHist);
}

/*static*/ void karma::ExampleAnalyzer::globalEndJob(karma::ExampleGlobalCache* globalCache) {
    // -- user code here: perform any global end-of-job wrap-up actions
    
    // -- write everything to file and close it
    globalCache->writeAllAndCloseFile();
}

// -- member functions

void karma::ExampleAnalyzer::beginStream(edm::StreamID streamID) {
    
    // -- user code here: perform any start-of-stream initialization actions
    //std::cout << "[" << std::hex << this << std::dec << "] Begin Stream with ID = " << streamID.value() << std::endl;
}

void karma::ExampleAnalyzer::analyze(const edm::Event& event, const edm::EventSetup& setup) {

    
    // -- get object collections for event
    bool obtained = true;
    
    // -- user code here: obtain event data (collection entries)
    // jets
    obtained |= event.getByToken(this->jetCollectionToken, this->jetCollectionHandle);

    assert(obtained);  // raise if one collection could not be obtained

    // -- user code here: main analyzer code
}


void karma::ExampleAnalyzer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    // The following says we do not know what parameters are allowed so do no validation
    // Please change this to state exactly what you do use, even if it is no parameters
    edm::ParameterSetDescription desc;
    desc.setUnknown();
    descriptions.addDefault(desc);
}


//define this as a plug-in
using karma::ExampleAnalyzer;
DEFINE_FWK_MODULE(ExampleAnalyzer);
