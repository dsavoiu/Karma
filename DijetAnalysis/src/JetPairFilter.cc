#include "Karma/DijetAnalysis/interface/JetPairFilter.h"

// -- constructor
dijet::JetPairFilter::JetPairFilter(const edm::ParameterSet& config) : NtupleFilterBase<dijet::NtupleEntry>(config) {
    // -- process configuration

}


// -- destructor
dijet::JetPairFilter::~JetPairFilter() {
}



// -- member functions

bool dijet::JetPairFilter::filterNtupleEntry(const dijet::NtupleEntry& ntupleEntry) {

    // -- filter events
    bool result = true;

    // ensure that at least two jets exist
    result &= ((ntupleEntry.jet1pt > 0) && (ntupleEntry.jet2pt > 0));

    return result;
}


//define this as a plug-in
using DijetJetPairFilter = dijet::JetPairFilter;
DEFINE_FWK_MODULE(DijetJetPairFilter);


// -- constructor
dijet::JetPairFilterV2::JetPairFilterV2(const edm::ParameterSet& config) : NtupleFilterBase<dijet::NtupleV2Entry>(config) {
    // -- process configuration

}


// -- destructor
dijet::JetPairFilterV2::~JetPairFilterV2() {
}



// -- member functions

bool dijet::JetPairFilterV2::filterNtupleEntry(const dijet::NtupleV2Entry& ntupleEntry) {

    // -- filter events
    bool result = true;

    // ensure that at least two jets exist
    result &= (ntupleEntry.Jet_pt.size() >= 2);

    return result;
}


//define this as a plug-in
using DijetJetPairFilterV2 = dijet::JetPairFilterV2;
DEFINE_FWK_MODULE(DijetJetPairFilterV2);
