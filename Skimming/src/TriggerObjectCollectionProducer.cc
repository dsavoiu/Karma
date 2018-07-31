#include "DijetAnalysis/Skimming/interface/TriggerObjectCollectionProducer.h"


void dijet::TriggerObjectCollectionProducer::produceSingle(const pat::TriggerObjectStandAlone& in, dijet::TriggerObject& out) {

    // populate the output object
    out.p4 = in.p4();
    out.types = in.triggerObjectTypes();
}


//define this as a plug-in
using dijet::TriggerObjectCollectionProducer;
DEFINE_FWK_MODULE(TriggerObjectCollectionProducer);
