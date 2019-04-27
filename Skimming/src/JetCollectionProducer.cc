#include "Karma/Skimming/interface/JetCollectionProducer.h"


void dijet::JetCollectionProducer::produceSingle(const pat::Jet& in, dijet::Jet& out, const edm::Event& event, const edm::EventSetup& setup) {

    // populate the output object
    out.p4 = in.p4();
    out.area = in.jetArea();

    out.nConstituents = in.nConstituents();
    out.nCharged = in.chargedMultiplicity();

    out.hadronFlavor = in.hadronFlavour();
    out.partonFlavor = in.partonFlavour();

    out.neutralHadronFraction = in.neutralHadronEnergyFraction();
    out.chargedHadronFraction = in.chargedHadronEnergyFraction();
    out.muonFraction = in.muonEnergyFraction();
    out.photonFraction = in.photonEnergyFraction();
    out.electronFraction = in.electronEnergyFraction();
    out.hfHadronFraction = in.HFHadronEnergyFraction();
    out.hfEMFraction = in.HFEMEnergyFraction();
}


//define this as a plug-in
using dijet::JetCollectionProducer;
DEFINE_FWK_MODULE(JetCollectionProducer);
