#include "DijetAnalysis/Skimming/interface/EventHLTFilter.h"


// -- constructor
dijet::EventHLTFilter::EventHLTFilter(const edm::ParameterSet& config) : m_configPSet(config) {
    dijetEventToken = consumes<dijet::Event>(m_configPSet.getParameter<edm::InputTag>("dijetEventSrc"));
}


bool dijet::EventHLTFilter::filter(edm::Event& event, const edm::EventSetup& setup) {

    bool obtained = true;
    // dijet event
    obtained &= event.getByToken(this->dijetEventToken, this->dijetEventHandle);
    assert(obtained);  // raise if one collection could not be obtained

    // return true if at least one HLT bit is set
    for (size_t iBit = 0; iBit < this->dijetEventHandle->hltBits.size(); ++iBit) {
        if (this->dijetEventHandle->hltBits[iBit]) {
            return true;
        }
    }

    // return false if no HLT bit is set
    return false;
}


//define this as a plug-in
using dijet::EventHLTFilter;
DEFINE_FWK_MODULE(EventHLTFilter);
