#include "DijetAnalysis/Analysis/interface/LeadingJetEtaFilter.h"

// -- constructor
dijet::LeadingJetEtaFilter::LeadingJetEtaFilter(const edm::ParameterSet& config) : 
    NtupleFilterBase(config),
    maxJetAbsEta_(config.getParameter<double>("maxJetAbsEta")) {
    // -- validate configuration
    assert(maxJetAbsEta_ >= 0);
}


// -- destructor
dijet::LeadingJetEtaFilter::~LeadingJetEtaFilter() {
}



// -- member functions

bool dijet::LeadingJetEtaFilter::filterNtupleEntry(const dijet::NtupleEntry& ntupleEntry) {
    return (std::abs(ntupleEntry.jet1eta) < this->maxJetAbsEta_);
}


//define this as a plug-in
using dijet::LeadingJetEtaFilter;
DEFINE_FWK_MODULE(LeadingJetEtaFilter);
