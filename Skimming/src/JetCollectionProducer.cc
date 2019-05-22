#include "Karma/Skimming/interface/JetCollectionProducer.h"


void karma::JetCollectionProducer::produceSingle(const pat::Jet& in, karma::Jet& out, const edm::Event& event, const edm::EventSetup& setup) {

    // populate the output object
    out.p4 = in.p4();
    out.uncorP4 = in.correctedP4("Uncorrected");

    out.area = in.jetArea();

    out.nConstituents = in.nConstituents();
    out.nCharged = in.chargedMultiplicity();
    out.nElectrons = in.electronMultiplicity();
    out.nMuons = in.muonMultiplicity();
    out.nPhotons = in.photonMultiplicity();

    out.hadronFlavor = in.hadronFlavour();
    out.partonFlavor = in.partonFlavour();

    out.neutralHadronFraction = in.neutralHadronEnergyFraction();
    out.chargedHadronFraction = in.chargedHadronEnergyFraction();
    out.chargedEMFraction = in.chargedEmEnergyFraction();
    out.neutralEMFraction = in.neutralEmEnergyFraction();
    out.muonFraction = in.muonEnergyFraction();
    out.photonFraction = in.photonEnergyFraction();
    out.electronFraction = in.electronEnergyFraction();
    out.hfHadronFraction = in.HFHadronEnergyFraction();
    out.hfEMFraction = in.HFEMEnergyFraction();

    // store the different JEC levels in one of the transient maps
    for (const std::string& jecLevel : in.availableJECLevels()) {
        out.transientLVs_[jecLevel] = in.correctedP4(jecLevel);
    }
}


//define this as a plug-in
using karma::JetCollectionProducer;
DEFINE_FWK_MODULE(JetCollectionProducer);
