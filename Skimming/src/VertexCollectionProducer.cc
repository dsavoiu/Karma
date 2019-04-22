#include "Karma/Skimming/interface/VertexCollectionProducer.h"


void karma::VertexCollectionProducer::produceSingle(const reco::Vertex& in, karma::Vertex& out, const edm::Event& event, const edm::EventSetup& setup) {

    // populate the output object
    out.position = in.position();
    // time coordinate only available starting with CMSSW_8_1_X
    #if (CMSSW_MAJOR_VERSION >= 9) || (CMSSW_MAJOR_VERSION == 8 && CMSSW_MINOR_VERSION >= 1)
    out.time = in.t();
    #endif

    out.chi2 = in.chi2();
    out.ndof = in.ndof();
    out.nTracks = in.nTracks();

    out.validity = in.isValid();

}


//define this as a plug-in
using karma::VertexCollectionProducer;
DEFINE_FWK_MODULE(VertexCollectionProducer);
