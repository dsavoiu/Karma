#include "Karma/Skimming/interface/MuonCollectionProducer.h"


void karma::MuonCollectionProducer::produceSingle(const pat::Muon& in, karma::Muon& out, const edm::Event& event, const edm::EventSetup& setup) {

    // populate the output object
    out.p4 = in.p4();

    out.pdgId = in.pdgId();
    out.status = in.status();
    out.charge = in.charge();

    out.trackIso = in.trackIso();
    out.caloIso = in.caloIso();
    out.ecalIso = in.ecalIso();
    out.hcalIso = in.hcalIso();

    out.particleIso = in.particleIso();
    out.chargedHadronIso = in.chargedHadronIso();
    out.neutralHadronIso = in.neutralHadronIso();
    out.photonIso = in.photonIso();
    out.puChargedHadronIso = in.puChargedHadronIso();

    out.recoSelectors = in.selectors();

}

bool karma::MuonCollectionProducer::acceptSingle(const pat::Muon& in, const edm::Event& event, const edm::EventSetup& setup) {
    // accept all muons
    return true;
}

//define this as a plug-in
using karma::MuonCollectionProducer;
DEFINE_FWK_MODULE(MuonCollectionProducer);
