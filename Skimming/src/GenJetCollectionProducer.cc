#include "Karma/Skimming/interface/GenJetCollectionProducer.h"


void karma::GenJetCollectionProducer::produceSingle(const reco::GenJet& in, karma::LV& out, const edm::Event& event, const edm::EventSetup& setup) {

    // populate the output object
    out.p4 = in.p4();

}


//define this as a plug-in
using karma::GenJetCollectionProducer;
DEFINE_FWK_MODULE(GenJetCollectionProducer);
