#include "Karma/Skimming/interface/GenJetCollectionProducer.h"


void dijet::GenJetCollectionProducer::produceSingle(const reco::GenJet& in, dijet::LV& out, const edm::Event& event, const edm::EventSetup& setup) {

    // populate the output object
    out.p4 = in.p4();

}


//define this as a plug-in
using dijet::GenJetCollectionProducer;
DEFINE_FWK_MODULE(GenJetCollectionProducer);
