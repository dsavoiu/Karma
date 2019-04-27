#include "Karma/DijetAnalysis/interface/LeadingJetPtFilter.h"

// -- constructor
dijet::LeadingJetPtFilter::LeadingJetPtFilter(const edm::ParameterSet& config) :
    NtupleFilterBase(config),
    minJetPt_(config.getParameter<double>("minJetPt")) {
    // -- validate configuration
    assert(minJetPt_ >= 0);
}


// -- destructor
dijet::LeadingJetPtFilter::~LeadingJetPtFilter() {
}



// -- member functions

bool dijet::LeadingJetPtFilter::filterNtupleEntry(const dijet::NtupleEntry& ntupleEntry) {
    return (std::abs(ntupleEntry.jet1pt) >= this->minJetPt_);
}


//define this as a plug-in
using dijet::LeadingJetPtFilter;
DEFINE_FWK_MODULE(LeadingJetPtFilter);
