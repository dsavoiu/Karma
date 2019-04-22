#include "Karma/Skimming/interface/METCollectionProducer.h"


void karma::METCollectionProducer::produceSingle(const pat::MET& in, karma::MET& out, const edm::Event& event, const edm::EventSetup& setup) {

    // populate the output object
    out.p4 =                     in.uncorP4();  // use only uncorrected MET in skims

    out.significance =           in.metSignificance();
    out.sumEt =                  in.uncorSumEt();

    out.neutralHadronFraction =  in.NeutralHadEtFraction();
    out.chargedHadronFraction =  in.ChargedHadEtFraction();
    out.muonFraction =           in.MuonEtFraction();
    out.photonFraction =         in.NeutralEMFraction();
    out.electronFraction =       in.ChargedEMEtFraction();
    out.hfHadronFraction =       in.Type6EtFraction();
    out.hfEMFraction =           in.Type7EtFraction();
}


//define this as a plug-in
using karma::METCollectionProducer;
DEFINE_FWK_MODULE(METCollectionProducer);
