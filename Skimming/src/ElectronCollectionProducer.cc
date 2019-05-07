#include "Karma/Skimming/interface/ElectronCollectionProducer.h"


void karma::ElectronCollectionProducer::produceSingle(const pat::Electron& in, karma::Electron& out, const edm::Event& event, const edm::EventSetup& setup) {

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

    out.ecalScale = in.ecalScale();
    out.ecalSmear = in.ecalSmear();

}

bool karma::ElectronCollectionProducer::acceptSingle(const pat::Electron& in, const edm::Event& event, const edm::EventSetup& setup) {
    // accept all electrons
    return true;
}

//define this as a plug-in
using karma::ElectronCollectionProducer;
DEFINE_FWK_MODULE(ElectronCollectionProducer);
