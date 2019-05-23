// system include files

#include "Karma/DijetAnalysis/interface/JetMatchingProducers.h"


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


void dijet::JetMuonMatchingProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    // The following says we do not know what parameters are allowed so do no validation
    // Please change this to state exactly what you do use, even if it is no parameters
    edm::ParameterSetDescription desc;
    desc.setUnknown();
    descriptions.addDefault(desc);
}


//define this as a plug-in
using dijet::JetMuonMatchingProducer;
DEFINE_FWK_MODULE(JetMuonMatchingProducer);


void dijet::JetElectronMatchingProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    // The following says we do not know what parameters are allowed so do no validation
    // Please change this to state exactly what you do use, even if it is no parameters
    edm::ParameterSetDescription desc;
    desc.setUnknown();
    descriptions.addDefault(desc);
}


//define this as a plug-in
using dijet::JetElectronMatchingProducer;
DEFINE_FWK_MODULE(JetElectronMatchingProducer);


void dijet::JetLVMatchingProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    // The following says we do not know what parameters are allowed so do no validation
    // Please change this to state exactly what you do use, even if it is no parameters
    edm::ParameterSetDescription desc;
    desc.setUnknown();
    descriptions.addDefault(desc);
}


//define this as a plug-in
using dijet::JetLVMatchingProducer;
DEFINE_FWK_MODULE(JetLVMatchingProducer);
