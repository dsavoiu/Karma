#include "Karma/Skimming/interface/EventHLTFilter.h"


// -- constructor
karma::EventHLTFilter::EventHLTFilter(const edm::ParameterSet& config) : m_configPSet(config) {
    karmaEventToken = consumes<karma::Event>(m_configPSet.getParameter<edm::InputTag>("karmaEventSrc"));
}


bool karma::EventHLTFilter::filter(edm::Event& event, const edm::EventSetup& setup) {

    // karma event
    karma::util::getByTokenOrThrow(event, this->karmaEventToken, this->karmaEventHandle);

    // return true if at least one HLT bit is set
    for (size_t iBit = 0; iBit < this->karmaEventHandle->hltBits.size(); ++iBit) {
        if (this->karmaEventHandle->hltBits[iBit]) {
            return true;
        }
    }

    // return false if no HLT bit is set
    return false;
}


//define this as a plug-in
using karma::EventHLTFilter;
DEFINE_FWK_MODULE(EventHLTFilter);
