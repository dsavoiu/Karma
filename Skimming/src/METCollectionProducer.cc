#include "Karma/Skimming/interface/METCollectionProducer.h"


void karma::METCollectionProducer::produceSingle(const pat::MET& in, karma::MET& out, const edm::Event& event, const edm::EventSetup& setup) {

    // populate the output object
    out.p4 =                     in.p4();
    out.sumEt =                  in.sumEt();
    out.uncorP4 =                in.uncorP4();
    out.uncorSumEt =             in.uncorSumEt();

    out.significance =           in.metSignificance();

    // only pat::METs made from reco::PFMETs have these properties
    if (in.isPFMET()) {
        out.neutralHadronFraction =  in.NeutralHadEtFraction();
        out.chargedHadronFraction =  in.ChargedHadEtFraction();
        out.muonFraction =           in.MuonEtFraction();
        out.photonFraction =         in.NeutralEMFraction();
        out.electronFraction =       in.ChargedEMEtFraction();
        out.hfHadronFraction =       in.Type6EtFraction();
        out.hfEMFraction =           in.Type7EtFraction();
    }

    // store the different correction levels in one of the transient maps
    out.transientLVs_["corP4Raw"] = in.corP4(pat::MET::METCorrectionLevel::Raw);
    out.transientDoubles_["corSumEtRaw"] = in.corSumEt(pat::MET::METCorrectionLevel::Raw);
    out.transientLVs_["corP4Type1"] = in.corP4(pat::MET::METCorrectionLevel::Type1);
    out.transientDoubles_["corSumEtType1"] = in.corSumEt(pat::MET::METCorrectionLevel::Type1);
}


//define this as a plug-in
using karma::METCollectionProducer;
DEFINE_FWK_MODULE(METCollectionProducer);
