#include "Karma/Common/interface/Producers/ZBosonProducer.h"

#include "Karma/SkimmingFormats/interface/Event.h"


//template karma::ZBosonProducer<karma::MuonCollection>;
//template karma::ZBosonProducer<karma::ElectronCollection>;


//define this as a plug-in
//using KarmaZBosonFromMuonsProducer = karma::ZBosonProducer<karma::MuonCollection>;
//DEFINE_FWK_MODULE(KarmaZBosonFromMuonsProducer);

using KarmaZBosonFromElectronsProducer = karma::ZBosonProducer<karma::ElectronCollection>;
DEFINE_FWK_MODULE(KarmaZBosonFromElectronsProducer);
