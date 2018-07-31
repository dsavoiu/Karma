#include "DijetAnalysis/Skimming/interface/JetCollectionProducer.h"


void dijet::JetCollectionProducer::produceSingle(const pat::Jet& in, dijet::Jet& out) {

    // populate the output object
    out.p4 = in.p4();

}


//define this as a plug-in
using dijet::JetCollectionProducer;
DEFINE_FWK_MODULE(JetCollectionProducer);
