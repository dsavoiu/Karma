#include "Karma/Skimming/interface/GenParticleCollectionProducer.h"


void karma::GenParticleCollectionProducer::produceSingle(const reco::GenParticle& in, karma::GenParticle& out, const edm::Event& event, const edm::EventSetup& setup) {

    // populate the output object
    out.p4 = in.p4();

    out.pdgId = in.pdgId();

    out.nDaughters = in.numberOfDaughters();
    out.status = in.status();

    const reco::GenStatusFlags& flags = in.statusFlags();

    out.isPrompt                            = flags.isPrompt();
    out.isDecayedLeptonHadron               = flags.isDecayedLeptonHadron();
    out.isTauDecayProduct                   = flags.isTauDecayProduct();
    out.isPromptTauDecayProduct             = flags.isPromptTauDecayProduct();
    out.isDirectTauDecayProduct             = flags.isDirectTauDecayProduct();
    out.isDirectPromptTauDecayProduct       = flags.isDirectPromptTauDecayProduct();
    out.isDirectHadronDecayProduct          = flags.isDirectHadronDecayProduct();
    out.isHardProcess                       = flags.isHardProcess();
    out.fromHardProcess                     = flags.fromHardProcess();
    out.isHardProcessTauDecayProduct        = flags.isHardProcessTauDecayProduct();
    out.isDirectHardProcessTauDecayProduct  = flags.isDirectHardProcessTauDecayProduct();
    out.isLastCopy                          = flags.isLastCopy();

}

bool karma::GenParticleCollectionProducer::acceptSingle(const reco::GenParticle& in, const edm::Event& event, const edm::EventSetup& setup) {

    return (allowedPDGIds_.count(in.pdgId()));
}

//define this as a plug-in
using karma::GenParticleCollectionProducer;
DEFINE_FWK_MODULE(GenParticleCollectionProducer);
