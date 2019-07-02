#include "Karma/Common/interface/Producers/ZBosonsProducer.h"

#include "Karma/SkimmingFormats/interface/Event.h"


//define this as a plug-in
using KarmaZBosonsFromMuonsProducer = karma::ZBosonsProducer<karma::MuonCollection>;
DEFINE_FWK_MODULE(KarmaZBosonsFromMuonsProducer);

using KarmaZBosonsFromElectronsProducer = karma::ZBosonsProducer<karma::ElectronCollection>;
DEFINE_FWK_MODULE(KarmaZBosonsFromElectronsProducer);
