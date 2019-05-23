// system include files

#include "Karma/DijetAnalysis/interface/JetTriggerObjectMatchingProducer.h"


void dijet::JetTriggerObjectMatchingProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    // The following says we do not know what parameters are allowed so do no validation
    // Please change this to state exactly what you do use, even if it is no parameters
    edm::ParameterSetDescription desc;
    desc.setUnknown();
    descriptions.addDefault(desc);
}


//define this as a plug-in
using dijet::JetTriggerObjectMatchingProducer;
DEFINE_FWK_MODULE(JetTriggerObjectMatchingProducer);
