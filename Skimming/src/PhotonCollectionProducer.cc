#include "Karma/Skimming/interface/PhotonCollectionProducer.h"


void karma::PhotonCollectionProducer::produceSingle(const pat::Photon& in, karma::Photon& out, const edm::Event& event, const edm::EventSetup& setup) {

    // populate the output object
    out.p4 = in.p4();

}


//define this as a plug-in
using karma::PhotonCollectionProducer;
DEFINE_FWK_MODULE(PhotonCollectionProducer);
