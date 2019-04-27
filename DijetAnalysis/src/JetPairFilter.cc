#include "Karma/DijetAnalysis/interface/JetPairFilter.h"

// -- constructor
dijet::JetPairFilter::JetPairFilter(const edm::ParameterSet& config) : NtupleFilterBase(config) {
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
using dijet::JetPairFilter;
DEFINE_FWK_MODULE(JetPairFilter);
