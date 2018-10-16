#include "DijetAnalysis/Analysis/interface/LeadingJetRapidityFilter.h"

// -- constructor
dijet::LeadingJetRapidityFilter::LeadingJetRapidityFilter(const edm::ParameterSet& config) :
    NtupleFilterBase(config),
    maxJetAbsRapidity_(config.getParameter<double>("maxJetAbsRapidity")) {
    // -- validate configuration
    assert(maxJetAbsRapidity_ >= 0);
}


// -- destructor
dijet::LeadingJetRapidityFilter::~LeadingJetRapidityFilter() {
}



// -- member functions

bool dijet::LeadingJetRapidityFilter::filterNtupleEntry(const dijet::NtupleEntry& ntupleEntry) {
    return (std::abs(ntupleEntry.jet1y) < this->maxJetAbsRapidity_);
}


//define this as a plug-in
using dijet::LeadingJetRapidityFilter;
DEFINE_FWK_MODULE(LeadingJetRapidityFilter);
