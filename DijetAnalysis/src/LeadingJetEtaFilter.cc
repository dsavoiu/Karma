#include "Karma/DijetAnalysis/interface/LeadingJetEtaFilter.h"

// -- constructor
dijet::LeadingJetEtaFilter::LeadingJetEtaFilter(const edm::ParameterSet& config) :
    NtupleFilterBase<dijet::NtupleEntry>(config),
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
using DijetLeadingJetEtaFilter = dijet::LeadingJetEtaFilter;
DEFINE_FWK_MODULE(DijetLeadingJetEtaFilter);
