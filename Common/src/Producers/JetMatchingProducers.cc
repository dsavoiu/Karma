// system include files

#include "Karma/Common/interface/Producers/JetMatchingProducers.h"


void karma::JetTriggerObjectMatchingProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    // The following says we do not know what parameters are allowed so do no validation
    // Please change this to state exactly what you do use, even if it is no parameters
    edm::ParameterSetDescription desc;
    desc.setUnknown();
    descriptions.addDefault(desc);
}


//define this as a plug-in
using KarmaJetTriggerObjectMatchingProducer = karma::JetTriggerObjectMatchingProducer;
DEFINE_FWK_MODULE(KarmaJetTriggerObjectMatchingProducer);


void karma::JetMuonMatchingProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    // The following says we do not know what parameters are allowed so do no validation
    // Please change this to state exactly what you do use, even if it is no parameters
    edm::ParameterSetDescription desc;
    desc.setUnknown();
    descriptions.addDefault(desc);
}


//define this as a plug-in
using KarmaJetMuonMatchingProducer = karma::JetMuonMatchingProducer;
DEFINE_FWK_MODULE(KarmaJetMuonMatchingProducer);


void karma::JetElectronMatchingProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    // The following says we do not know what parameters are allowed so do no validation
    // Please change this to state exactly what you do use, even if it is no parameters
    edm::ParameterSetDescription desc;
    desc.setUnknown();
    descriptions.addDefault(desc);
}


//define this as a plug-in
using KarmaJetElectronMatchingProducer = karma::JetElectronMatchingProducer;
DEFINE_FWK_MODULE(KarmaJetElectronMatchingProducer);


void karma::JetLVMatchingProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    // The following says we do not know what parameters are allowed so do no validation
    // Please change this to state exactly what you do use, even if it is no parameters
    edm::ParameterSetDescription desc;
    desc.setUnknown();
    descriptions.addDefault(desc);
}


//define this as a plug-in
using KarmaJetLVMatchingProducer = karma::JetLVMatchingProducer;
DEFINE_FWK_MODULE(KarmaJetLVMatchingProducer);
