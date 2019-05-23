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

    if (m_produceEcalTrkEnergyCorrections) {
        out.ecalTrkEnergyPreCorr = in.userFloat("ecalTrkEnergyPreCorr");
        out.ecalTrkEnergyPostCorr = in.userFloat("ecalTrkEnergyPostCorr");
    }

    // retrieve electron Ids and store in transient map
    for (const auto& electronIdTagAndWorkingPoints : m_electronIdSpecs) {
        int electronIDCompact = 0;

        bool looserWPFailed = false;
        for (const auto& workingPoint : electronIdTagAndWorkingPoints.second) {
            // check if tag exists (and throw)
            if (!in.isElectronIDAvailable(workingPoint)) {
                edm::Exception exception(edm::errors::NotFound);
                exception << "Could not find electron Id with tag '"
                          << workingPoint << "' "
                          << "in user data of product '"
                          << this->inputCollectionHandle_.provenance()->branchName()
                          <<  "'. Available tags are: ";
                const std::vector<pat::Electron::IdPair>& availableIDs = in.electronIDs();
                for (size_t iID = 0; iID < availableIDs.size(); ++iID) {
                    exception << ((iID == 0) ? "" : ", ") << availableIDs[iID].first;
                }
                throw exception;
            }

            // sanity check: tighter IDs should all fail if looser ID fails
            bool result = static_cast<bool>(in.electronID(workingPoint));
            if (looserWPFailed && result) {
                // electron failed looser WP, but it would pass this one -> throw!
                edm::Exception exception(edm::errors::LogicError);
                exception << "Electron passes tighter Id '"
                          << workingPoint << "' despite failing previous, looser ones!"
                          << "The specified ID sequence, from loose to tight, was: ";
                for (size_t iName = 0; iName < electronIdTagAndWorkingPoints.second.size(); ++iName) {
                    exception << ((iName == 0) ? "" : ", ") << electronIdTagAndWorkingPoints.second[iName];
                }
                throw exception;
            }

            // set flag if current working point failed
            looserWPFailed |= (!result);

            // all OK -> increment compact ID
            if (result) ++electronIDCompact;
        }
        out.transientInts_[electronIdTagAndWorkingPoints.first] = electronIDCompact;
    }
}

bool karma::ElectronCollectionProducer::acceptSingle(const pat::Electron& in, const edm::Event& event, const edm::EventSetup& setup) {
    // accept all electrons
    return true;
}

//define this as a plug-in
using karma::ElectronCollectionProducer;
DEFINE_FWK_MODULE(ElectronCollectionProducer);
